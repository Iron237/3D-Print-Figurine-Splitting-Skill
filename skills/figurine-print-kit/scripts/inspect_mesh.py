"""Read-only inventory of figure meshes and point clouds. Requires numpy, trimesh and scipy."""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import trimesh


def positive_float(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("expected a finite positive number")
    return number


def mesh_topology(geometry):
    vertices = np.asarray(geometry.vertices)
    faces = np.asarray(geometry.faces)
    result = {"triangles": len(faces)}
    if not len(faces) or not np.isfinite(vertices).all():
        return result
    # Work on exactly coincident coordinates. Keep defects visible in the report.
    points, lookup = np.unique(vertices, axis=0, return_inverse=True)
    mesh = trimesh.Trimesh(points, lookup.reshape(-1)[faces], process=False)
    mesh.remove_unreferenced_vertices()
    incidence = np.bincount(mesh.edges_unique_inverse)
    repeated = len(faces) - len(np.unique(np.sort(mesh.faces, axis=1), axis=0))
    result.update(
        welded_used_vertices=len(mesh.vertices),
        vertex_connected_bodies=int(mesh.body_count),
        boundary_edges=int(np.count_nonzero(incidence == 1)),
        edges_with_more_than_two_faces=int(np.count_nonzero(incidence > 2)),
        duplicate_triangles=int(repeated),
        zero_area_triangles=int(np.count_nonzero(mesh.area_faces == 0)),
        watertight=bool(mesh.is_watertight),
        winding_consistent=bool(mesh.is_winding_consistent),
    )
    if mesh.is_watertight and mesh.is_winding_consistent:
        result["signed_volume_model_units_cubed"] = float(mesh.volume)
    return result


def inspect(path, mm_per_unit=None):
    scene = trimesh.load_scene(path, process=False)
    if not scene.graph.nodes_geometry:
        raise ValueError("no mesh or point geometry instances were loaded")
    bounds = []
    inventory = {}
    for node in sorted(scene.graph.nodes_geometry, key=str):
        matrix, name = scene.graph[node]
        geometry = scene.geometry[name]
        if not hasattr(geometry, "vertices"):
            raise ValueError(f"unsupported geometry {name}: {type(geometry).__name__}")
        if name not in inventory:
            vertices = np.asarray(geometry.vertices)
            item = {"geometry": str(name), "type": type(geometry).__name__,
                    "source_vertices": len(vertices),
                    "nonfinite_vertices": int(np.count_nonzero(~np.isfinite(vertices).all(axis=1))),
                    "instances": []}
            if isinstance(geometry, trimesh.Trimesh):
                item.update(mesh_topology(geometry))
            inventory[name] = item
        vertices = np.asarray(geometry.vertices)
        finite = vertices[np.isfinite(vertices).all(axis=1)]
        transform = np.asarray(matrix)
        if not np.isfinite(transform).all():
            raise ValueError(f"non-finite transform on {node}")
        inventory[name]["instances"].append({
            "node": str(node),
            "linear_determinant": float(np.linalg.det(transform[:3, :3])),
        })
        if len(finite):
            world = trimesh.transform_points(finite, transform)
            bounds.append(np.vstack([world.min(axis=0), world.max(axis=0)]))
    if not bounds:
        raise ValueError("no finite points to measure")
    bounds = np.array(bounds)
    low, high = bounds[:, 0].min(axis=0), bounds[:, 1].max(axis=0)
    units = scene.units
    source = "caller" if mm_per_unit is not None else "unknown"
    if mm_per_unit is None and units:
        try:
            mm_per_unit = float(trimesh.units.unit_conversion(units, "mm"))
            source = "importer"
        except (KeyError, ValueError):
            pass
    return {
        "file": path.name, "importer_units": units, "scale_source": source,
        "mm_per_model_unit": mm_per_unit,
        "scene_bounds_model_units": [low.tolist(), high.tolist()],
        "scene_extents_xyz_mm": ((high - low) * mm_per_unit).tolist() if mm_per_unit else None,
        "geometries": list(inventory.values()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("--mm-per-unit", type=positive_float, help="explicit scale for the loaded coordinates")
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.model, args.mm_per_unit), indent=2, ensure_ascii=False, allow_nan=False))
    except Exception as exc:
        parser.exit(2, f"Inspection failed: {exc}\n")


if __name__ == "__main__":
    main()
