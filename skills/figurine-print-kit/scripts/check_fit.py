"""Check static overlap and sampled translations of assembled STL files, in millimetres."""
import argparse
import itertools
import json
import math
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh


def number(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name} must be numeric")
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f"{name} is out of range")
    return float(value)


def solid(path):
    if path.suffix.lower() != ".stl":
        raise ValueError(f"expected an assembled-position STL: {path.name}")
    mesh = trimesh.load_mesh(path, process=False)
    # STL repeats vertices per facet. Weld exact coordinates without repairing the geometry.
    points, lookup = np.unique(mesh.vertices, axis=0, return_inverse=True)
    mesh = trimesh.Trimesh(points, lookup.reshape(-1)[mesh.faces], process=False)
    if not len(mesh.faces) or not np.isfinite(mesh.vertices).all() or not mesh.is_volume:
        raise ValueError(f"{path.name}: requires a closed, consistently oriented, positive-volume mesh")
    body = mf.Manifold(mf.Mesh64(np.ascontiguousarray(mesh.vertices, dtype=np.float64),
                                 np.ascontiguousarray(mesh.faces, dtype=np.uint64)))
    if body.status() != mf.Error.NoError or body.is_empty():
        raise ValueError(f"{path.name}: solid conversion failed ({body.status()})")
    return body


def overlap(left, right):
    a = np.asarray(left.bounding_box())
    b = np.asarray(right.bounding_box())
    if np.any(np.minimum(a[3:], b[3:]) <= np.maximum(a[:3], b[:3])):
        return 0.0
    section = left ^ right
    if section.status() != mf.Error.NoError:
        raise ValueError(f"intersection failed ({section.status()})")
    return max(0.0, section.volume())


def members(path, name, solids):
    values = path.get(name)
    if not isinstance(values, list) or not values or any(not isinstance(x, str) for x in values):
        raise ValueError(f"{name} must be a nonempty list of part IDs")
    if len(set(values)) != len(values) or set(values) - solids.keys():
        raise ValueError(f"repeated or unknown IDs in {name}: {values}")
    return values


def sample_offsets(points, step):
    yield points[0]
    for start, end in zip(points, points[1:]):
        delta = end - start
        count = math.ceil(np.linalg.norm(delta) / step)
        for i in range(1, count + 1):
            yield end if i == count else start + delta * (i / count)


def check_path(path, solids, tolerance, default_step):
    moving = members(path, "moving", solids)
    fixed = members(path, "fixed", solids)
    if set(moving) & set(fixed):
        raise ValueError("a part cannot be both moving and fixed in one path")
    points = np.asarray(path["offsets_mm"], dtype=float)
    if (points.ndim != 2 or points.shape[1] != 3 or len(points) < 2 or
            not np.isfinite(points).all() or np.any(points[0] != 0) or not np.any(points != 0)):
        raise ValueError("offsets_mm must start at [0,0,0] and include a finite nonzero XYZ displacement")
    step = number(path.get("step_mm", default_step), "step_mm", positive=True)
    worst = {}
    samples = 0
    for offset in sample_offsets(points, step):
        samples += 1
        for a in moving:
            translated = solids[a].translate(offset)
            for b in fixed:
                volume = overlap(translated, solids[b])
                key = (a, b)
                previous = worst.get(key)
                if volume > tolerance and (previous is None or volume > previous["overlap_mm3"]):
                    worst[key] = {"parts": list(key), "overlap_mm3": volume, "offset_mm": offset.tolist()}
    return {"name": path["name"], "moving": moving, "fixed": fixed, "step_mm": step,
            "samples": samples, "interferences": list(worst.values())}


def check(manifest):
    spec = json.loads(manifest.read_text(encoding="utf-8-sig"))
    if spec.get("units") != "mm":
        raise ValueError('declare "units": "mm" and supply all files in this unit')
    files = spec["parts"]
    if not isinstance(files, dict) or len(files) < 2:
        raise ValueError("parts must map at least two unique part IDs to assembled STL paths")
    if not all(isinstance(name, str) and name and isinstance(rel, str) and rel for name, rel in files.items()):
        raise ValueError("parts must map nonempty IDs to nonempty file paths")
    tolerance = number(spec["tolerance_mm3"], "tolerance_mm3")
    motions = spec.get("paths", [])
    if not isinstance(motions, list):
        raise ValueError("paths must be a list")
    solids = {name: solid(manifest.parent / rel) for name, rel in files.items()}
    collisions = []
    for a, b in itertools.combinations(solids, 2):
        volume = overlap(solids[a], solids[b])
        if volume > tolerance:
            collisions.append({"parts": [a, b], "overlap_mm3": volume})
    paths = [check_path(p, solids, tolerance, spec.get("step_mm")) for p in motions]
    return {
        "units": "mm", "part_count": len(solids), "static_pairs": math.comb(len(solids), 2),
        "tolerance_mm3": tolerance, "static_interferences": collisions, "translation_paths": paths,
        "motion_checked": bool(paths),
        "over_limit_in_checked_scope": bool(collisions or any(p["interferences"] for p in paths)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        report = check(args.manifest)
        print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
    except Exception as exc:
        parser.exit(2, f"Fit check failed: {exc}\n")
    return int(report["over_limit_in_checked_scope"])


if __name__ == "__main__":
    raise SystemExit(main())
