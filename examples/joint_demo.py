"""Exercise the fit checker with an axial release and a blocked sideways release."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh


def save_solid(solid, path):
    mesh = solid.to_mesh()
    trimesh.Trimesh(
        vertices=np.asarray(mesh.vert_properties)[:, :3],
        faces=np.asarray(mesh.tri_verts),
        process=False,
    ).export(path)


def main():
    checker = Path(__file__).resolve().parents[1] / "skills/figurine-print-kit/scripts/check_fit.py"
    with tempfile.TemporaryDirectory(prefix="figurine-joint-") as temp:
        folder = Path(temp)
        flat = mf.CrossSection.square((8, 8), center=True).translate((-2.4, 0))
        key = mf.CrossSection.circle(2, 48) ^ flat
        peg = key.extrude(7.5).translate((0, 0, 2.5))
        block = mf.Manifold.cube((14, 14, 8)).translate((-7, -7, 0))
        socket = block - key.offset(0.2).extrude(7).translate((0, 0, 2))
        save_solid(peg, folder / "peg.stl")
        save_solid(socket, folder / "socket.stl")
        for name, end, expected in [("axial", [0, 0, 12], 0), ("sideways", [18, 0, 0], 1)]:
            spec = {
                "units": "mm", "step_mm": 0.25, "tolerance_mm3": 0.005,
                "parts": {"peg": "peg.stl", "socket": "socket.stl"},
                "paths": [{"name": name, "moving": ["peg"], "fixed": ["socket"],
                           "offsets_mm": [[0, 0, 0], end]}],
            }
            manifest = folder / "assembly-check.json"
            manifest.write_text(json.dumps(spec), encoding="utf-8")
            result = subprocess.run([sys.executable, "-X", "utf8", str(checker), str(manifest)],
                                    capture_output=True, encoding="utf-8")
            if result.returncode != expected:
                raise RuntimeError(f"{name}: unexpected exit {result.returncode}\n{result.stdout}{result.stderr}")
            report = json.loads(result.stdout)
            if report["static_interferences"]:
                raise RuntimeError("The starting pose must be clear for both trials")
            motion = report["translation_paths"][0]
            collisions = motion["interferences"]
            if bool(collisions) != (name == "sideways"):
                raise RuntimeError(f"{name}: unexpected motion result")
            maximum = max((c["overlap_mm3"] for c in collisions), default=0)
            print(f"{name}: {motion['samples']} samples, peak reported overlap {maximum:.3f} mm^3")


if __name__ == "__main__":
    main()
