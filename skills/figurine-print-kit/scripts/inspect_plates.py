"""List Bambu Studio plates, their assigned instances and any packaged slice headers."""
import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


def metadata(element):
    return {m.get("key"): m.get("value") for m in element.findall("metadata") if m.get("key")}


def slice_header(archive, path):
    # Object labels and estimates are at the top of Bambu Studio's G-code.
    # Restrict reads to the preamble; this report does not check extrusion paths.
    header = {}
    with archive.open(path) as stream:
        for line in stream.read(65536).decode("utf-8", errors="replace").splitlines():
            if line.startswith("; HEADER_BLOCK_END"):
                break
            if line.startswith("; model label id:"):
                header["object_labels"] = re.findall(r"\d+", line.partition(":")[2])
            elif line.startswith("; total filament weight [g]"):
                header["filament_weight_g"] = line.partition(":")[2].strip()
            elif "total estimated time:" in line and line.startswith(";"):
                header["estimated_time"] = line.partition("total estimated time:")[2].strip()
    return header


def inspect(path):
    with zipfile.ZipFile(path) as archive:
        cfg = ET.fromstring(archive.read("Metadata/model_settings.config"))
        project = json.loads(archive.read("Metadata/project_settings.config"))
        objects = {obj.get("id"): metadata(obj).get("name", obj.get("id")) for obj in cfg.findall("object")}
        plates = []
        assigned = set()
        plate_ids = set()
        for plate in cfg.findall("plate"):
            data = metadata(plate)
            number = int(data["plater_id"])
            if number in plate_ids:
                raise ValueError(f"duplicate plate number {number}")
            plate_ids.add(number)
            instances = []
            for instance in plate.findall("model_instance"):
                row = metadata(instance)
                key = (row["object_id"], row["instance_id"])
                if key in assigned:
                    raise ValueError(f"instance {key} listed more than once")
                assigned.add(key)
                instances.append({"object_id": key[0], "instance_id": key[1],
                                  "name": objects[key[0]], "label": row.get("identify_id")})
            record = {"plate": number, "name": data.get("plater_name"), "instances": instances}
            gcode = data.get("gcode_file")
            if gcode:
                header = slice_header(archive, gcode)
                bbox = f"Metadata/plate_{number}.json"
                if bbox in archive.namelist():
                    summary = json.loads(archive.read(bbox))
                    header["slice_nozzle_mm"] = summary.get("nozzle_diameter")
                    header["first_layer_bbox_xy"] = summary.get("bbox_all")
                record["slice_header"] = header
            plates.append(record)
        if not plates:
            raise ValueError("no native plate records in this project")
        return {"project_printer": project.get("printer_settings_id"), "project_nozzle_mm": project.get("nozzle_diameter"),
                "filament_profiles": project.get("filament_settings_id"), "filament_colors": project.get("filament_colour"),
                "assigned_instances": len(assigned), "plates": plates}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.project), ensure_ascii=False, indent=2))
    except (OSError, KeyError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        parser.exit(2, f"Cannot read Bambu Studio plate metadata: {exc}\n")


if __name__ == "__main__":
    main()
