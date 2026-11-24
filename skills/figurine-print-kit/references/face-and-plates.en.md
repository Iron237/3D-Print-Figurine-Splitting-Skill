# Face socket lead-ins and multi-plate print projects

[中文](face-and-plates.md)

## Refine the rear face and neck interfaces

Locate the long key passing through the fringe, the rear socket and the neck socket in assembly coordinates. Section each socket on its own insertion axis. Identify the first contact at the hairline, mouth or bottom. Retain the previous face, mouth centers, axes, tip and bottom positions as references.

1. Use front, oblique and elevated views to mark the eyelids, nose, lips, cheeks and jawline. Protect the original sculpt, straight bore and bottom. Remesh and fair the artificial rear surfaces within a narrow transition band. Check the outside of thin temple regions.
2. When a key fits the bore but catches on entry, loft a rounded mouth from several sections following its original keyed profile. Blend into the straight guide and preserve the D flat. Measure remaining engagement, axial bottom clearance and stock between the new opening and the outer sculpt. Choose each lead-in length for the available stock and actual insertion direction.
3. Inspect radial sections near the start of the straight bore and the end of the peg. Measure the blind depth along the axis. Seat the face and fringe on the neck, then check the long rear key through the fringe and into the face. Compare the eye, nose and lip surfaces and both silhouettes from matched views. Reopen both assembly and bed orientations and check closure and self-intersections. For a physical check, [crop a matched pair from the final joint](seams-and-coupons.en.md).

## Group plates by the spools, nozzles and time actually needed

Confirm the printer, printable bed area, build surface, physical spools and nozzle sizes. For each production part, record its ID, print orientation, spool, nozzle, layer height, time estimate and surfaces sensitive to support marks. A painted figure can share one spool of white PLA across skin, hair and clothing. Group by separate spools when the user intends to print those base colors or materials.

- Keep compatible nozzle and process settings together. Preserve face and hair orientation, then rotate about the bed normal or translate to reduce travel. Allow room for trees, brims, bed exclusions and tall narrow parts. For sequential printing, also check the toolhead envelope.
- Use single-part estimates for a first layout, then balance long jobs using actual whole-plate slices. Consider starts, nozzle changes and the cost of reprinting a failed plate alongside total time. Record each plate’s estimated time and material from its own slice.
- Build an editable native multi-plate project. Assign each production part as a separately selectable print instance. Name each plate with its number, spool and nozzle. Identify optional test pieces separately. Use manual placement or a native assemble list. When an assembly master exists, preserve the inverse bed-placement transforms so the same meshes can also be viewed assembled.
- A single-hotend project in Bambu Studio has one active machine/nozzle preset. Set the first batch as the default. On the changeover plate and in its instructions, specify the physical nozzle swap, machine and process presets, and slicing of the current plate. Preserve required supports and wall settings as object overrides or in the relevant process. Recheck them after switching.

## Validate each plate from the final editable project

1. Reopen the delivered 3MF. Check printer, bed, filament, part IDs and unique instances per plate. Check omissions, duplicates, floating parts, overlaps and out-of-bounds placement. If an assembly view is included, check its relative positions and height separately.
2. Slice each selected plate with its own machine, nozzle, process and filament profiles. Read back the actual printer, nozzle diameter, layer height, plate ID and object labels from the result. Inspect material-depositing model moves for every object, first layers, support and brim coverage. Resolve slicer warnings.
3. Deliver the editable 3MF and a plate list giving the default setup, changeover, estimated time and grams, and physical test status. After geometry, layout or preset changes, reslice affected plates from the final file.

[inspect_plates.py](../scripts/inspect_plates.py) reads the native Bambu Studio plate table, instance membership, project preset and any packaged slice headers. Run it on the editable master and on the individual verification slices. An editable master can be opened and sliced without embedded G-code. Header labels and estimates help identify a slice; inspect its actual extrusion paths as well.

```sh
python -X utf8 scripts/inspect_plates.py project.3mf
```

The worked build uses a P2S, a 256 × 256 mm bed and one white PLA spool. Seven detail parts occupy two 0.2 mm plates. Eight larger parts share a 0.4 mm plate. Printing them in order requires one nozzle change. Repack for the actual printer, part dimensions and spools. [Bambu Studio command line and selected-plate slicing](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage)
