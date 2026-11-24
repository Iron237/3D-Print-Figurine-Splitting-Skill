"""Clip a matched pair of fit coupons from final millimetre STLs in assembly coordinates."""
import argparse
import tempfile
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh

from check_fit import solid


def crop_tool(center, axis, radius, behind, ahead):
    center = np.asarray(center, dtype=float)
    axis = np.asarray(axis, dtype=float)
    if not np.isfinite([*center, *axis, radius, behind, ahead]).all():
        raise ValueError("crop dimensions and coordinates must be finite")
    length = np.linalg.norm(axis)
    if length == 0 or not np.isfinite(length) or min(radius, behind, ahead) <= 0:
        raise ValueError("provide a nonzero insertion axis and positive radius, behind and ahead distances")
    direction = axis / length
    reference = np.eye(3)[np.argmin(np.abs(direction))]
    x = np.cross(reference, direction)
    x /= np.linalg.norm(x)
    frame = np.column_stack((x, np.cross(direction, x), direction, center - direction * behind))
    return mf.Manifold.cylinder(behind + ahead, radius, circular_segments=96).transform(frame)


def require_one_body(body, name):
    if body.status() != mf.Error.NoError or body.is_empty() or body.volume() <= 0:
        raise ValueError(f"{name}: empty or invalid crop; check the joint center, units and assembled pose")
    # A single printable body may include closed inner cavity surfaces.
    if sum(shell.volume() > 0 for shell in body.decompose()) != 1:
        raise ValueError(f"{name}: crop contains separate bodies; adjust the crop or select the joint locally in CAD")


def extract(male, female, tool, destination):
    if male.resolve().samefile(female.resolve()):
        raise ValueError("provide the two different production parts that form the joint")
    if destination.exists():
        raise ValueError(f"output directory already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".fit-coupons-", dir=destination.parent) as staging:
        pair = Path(staging) / "pair"
        pair.mkdir()
        for label, source in (("male", male), ("female", female)):
            coupon = solid(source) ^ tool
            require_one_body(coupon, label)
            mesh = coupon.to_mesh64()
            path = pair / f"{label}.stl"
            trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                            faces=np.asarray(mesh.tri_verts), process=False).export(path)
            require_one_body(solid(path), label)
        pair.rename(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("male", type=Path)
    parser.add_argument("female", type=Path)
    parser.add_argument("output", type=Path, help="new directory for male.stl and female.stl")
    parser.add_argument("--center", nargs=3, type=float, required=True, metavar=("X", "Y", "Z"),
                        help="point at the socket mouth in assembled millimetres")
    parser.add_argument("--axis", nargs=3, type=float, required=True, metavar=("X", "Y", "Z"),
                        help="insertion direction pointing into the socket")
    parser.add_argument("--radius", type=float, required=True, help="radial crop extent in mm")
    parser.add_argument("--behind", type=float, required=True, help="mm from the center towards the peg root")
    parser.add_argument("--ahead", type=float, required=True, help="mm from the center towards the socket bottom")
    args = parser.parse_args()
    try:
        tool = crop_tool(args.center, args.axis, args.radius, args.behind, args.ahead)
        extract(args.male, args.female, tool, args.output)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"Coupon extraction failed: {exc}\n")
    print(f"Created {args.output} in assembly coordinates. Apply each production print orientation before slicing.")


if __name__ == "__main__":
    main()
