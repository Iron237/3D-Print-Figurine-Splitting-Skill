# 3D-Printed Figurine Splitting Skill

[中文说明](README.md) · **English guide**

Turn an AI-generated or scanned figurine into parts that can be printed, painted and assembled separately. This Codex skill starts with the actual mesh. If a strand covers an eye, which way can the face come out? If a forearm is fused to a bag, which side can be rebuilt while keeping the hand pose? The skill uses questions like these to agree on the split before cutting.

## Install and invoke

```sh
git clone https://github.com/Iron237/3D-Print-Figurine-Splitting-Skill.git
```

Alternatively, unzip the [latest skill ZIP](https://github.com/Iron237/3D-Print-Figurine-Splitting-Skill/releases/latest/download/figurine-print-kit.zip) to get the skill folder directly. For a Git installation, copy the entire `skills/figurine-print-kit` folder into your Codex skills directory. The default is `~/.codex/skills/`. If you set `CODEX_HOME`, use its `skills/` directory. Start a new chat and invoke the skill explicitly:

> Use $figurine-print-kit to inspect this scanned figure. I print PLA with 0.2 and 0.4 mm nozzles. Grill me one decision at a time about the cuts and paint boundaries, then wait for my agreement before cutting. Use the illustration for color only. Preserve the original hair and hand pose.

Attach the model and mention any known equipment, material, scale or constraints. A color reference is useful even if the geometry should stay as sculpted. If the size is undecided, ask the AI to measure the fine features and choose one. Ask for a split plan only if that is all you need.

## How decisions are made

| Stage | What the skill does |
|---|---|
| Inspect the source | Preserve the source and assembly coordinates. Check units, instance transforms and shells. Inspect front, side, rear and sectional views. Distinguish scan noise and texture boundaries from actual sculpted edges. |
| Ask one question at a time | Start with a choice that changes the build. For example, “Do you want to hold the entire face in your hand to paint the eyes?” Give a recommendation grounded in the mesh and measure what can be measured. |
| Agree on the parts | Record paint access, what stays attached for masking, seam location, insertion direction and fastening for each major part. Agree on whether a reference supplies colors or also authorizes sculpt changes. |
| Cut and rebuild | Use hairlines, cuffs, waistbands or footwear openings where they provide a natural seam. Reconstruct hidden mating surfaces. Inspect both the separated parts and the assembled sculpt. |
| Verify and deliver | Reopen the final STLs, check the assembled pose and intermediate withdrawal positions, then slice for the chosen process. Deliver numbered parts, an assembly reference, paint notes and assembly/disassembly order. Where fit needs testing, crop the coupons from the final mating pair. |

When likeness takes priority, relieve hidden intersections first. Try a small shift or a different assembly sequence before sacrificing a visible eyelid, finger, hair tip or fold. Keep fragile detail attached for masking if separation would damage the sculpt. Remove canceled additions from meshes, previews, inventories and the final package.

## Assembly rules

- **Design the motion as well as the seam.** Parts that meet perfectly at rest can bind halfway out. Identify the obstructions, then choose straight insertion, a staged release or an installation subassembly. At the endpoint of a removal path, confirm that the peg has cleared the socket mouth and every undercut has released.
- **Specify each joint.** Identify male and female parts, key profile, insertion axis, engagement length, per-side clearance, extra socket depth and remaining wall thickness. Trace the load from shoe to hip on a single-leg stance. Multiple pegs need a common insertion stroke.
- **Choose fastening per part.** A face intended for retouching benefits from a removable fit. The load-bearing shoe can be spot-glued after a dry fit. Mask locating shoulders, pegs and sockets before painting. For FDM, consider layer strength and support removal. For resin, account for shrinkage, support contacts and drainage in hollow parts.
- **State the level of verification.** Closed meshes, a digital motion check, generated toolpaths and a physical print are separate results. Inspect actual extrusion paths for FDM or the resin profile and active exposure layers for resin prints. Report what was checked and repeat the affected checks after rework.

The installed skill includes detailed [interview guidance](skills/figurine-print-kit/references/grill.md) and [joint design and assembly notes](skills/figurine-print-kit/references/assembly.md) in Chinese. It can conduct the interview and deliver the job in the user's language.

## When an existing split has rough edges

Separate the pair, inspect the visible seam, hidden cut and socket from the same angle, then section along the insertion axis to find the first contact. Remesh and smooth a narrow band on the hidden cut while preserving hair tips, eyelids and fabric folds. A shared trim boundary on both halves helps prevent daylight along a visible seam.

Where a waist or sock has enough wall thickness, a D key can set rotation, an annular shoulder can set depth and a chamfer can guide entry. To test the joint, crop both final parts with the same cutter. Keep the peg root and tip, socket bottom, shoulder and adjacent walls. Slice each half with its production orientation and process settings. Crop the entire group to test simultaneous engagement of multiple pegs.

> Use $figurine-print-kit to smooth the sock opening and the back of the face while preserving the assembled sculpt. Crop a matched pair from the final sock joint and another from the hair key. Give me the nozzle and print orientation so I can dry-fit both before printing the figure.

See the [English procedure for seams, locating shoulders and production fit coupons](skills/figurine-print-kit/references/seams-and-coupons.en.md).

## Optional geometry tools

Run these commands from the repository root. The interview and design guidance work independently of Python. The two inspection scripts report JSON. The coupon extractor writes two new STLs to a separate directory and preserves the input meshes.

```sh
python -m pip install -r requirements.txt
python examples/joint_demo.py
python -X utf8 skills/figurine-print-kit/scripts/inspect_mesh.py model.stl
python -X utf8 skills/figurine-print-kit/scripts/check_fit.py assembly-check.json
```

- **inspect_mesh.py** reports scene bounds, instances, triangles, boundary and non-manifold edges. An STL's physical scale stays unknown until supplied. A point cloud can be inspected but still needs reconstruction before solid splitting.
- **check_fit.py** checks static overlap and samples piecewise translations. Supply millimetre STLs in a shared assembled coordinate system. Restore the assembly transforms before using files that were individually centered on the print bed. Exit code 0 means measured overlaps stayed within the declared threshold, 1 means interference and 2 means invalid input or a failed computation. Rotation, flex, mechanical strength and motion between samples need separate evaluation.
- **extract_fit_coupons.py** crops the final mating pair along its insertion axis in assembly coordinates. Supply the measured socket mouth, crop radius and axial extents. [Command example](skills/figurine-print-kit/references/seams-and-coupons.en.md#crop-with-the-helper)
- **joint_demo.py** generates a D-shaped peg and socket in a temporary directory. It checks axial withdrawal and a sideways pull using the same parts.

A minimal manifest for the fit checker is shown below. `offsets_mm` contains cumulative translations from the assembled pose. List the moving group and everything that remains in its way at this stage. Omitting `paths` runs only the static check. Use finer steps or a swept-volume check for delicate details.

```json
{
  "units": "mm",
  "tolerance_mm3": 0.005,
  "step_mm": 0.25,
  "parts": {"peg": "peg.stl", "socket": "socket.stl"},
  "paths": [
    {"name": "axial withdrawal", "moving": ["peg"], "fixed": ["socket"],
     "offsets_mm": [[0, 0, 0], [0, 0, 12]]}
  ]
}
```

## A worked example

A single-leg PLA figure was split into 15 production parts at 250 mm overall height. Its face came out for eye painting, the original curl stayed with the front hair, and the fine strap remained against the shirt for masking. The face and fringe were first combined in hand and seated on the neck. The rear hair then slid in from behind, carrying a long locating peg into the face. The first version included a nominal-clearance gauge. The revision added four annular seats and two matched coupon pairs cropped from the final sock and hair joints. Across the same 96 points around the supporting sock, the modeled axial height span fell from 1.77 mm to under 0.01 mm. All 15 production parts and four coupons were sliced. Physical fit is still untested.

Those dimensions belong to that build. A resin bust or a smaller print needs its own measurements, load-path assessment and fit tests. The public [case notes](skills/figurine-print-kit/references/worked-example.md) describe the decisions and validation scope without distributing the source model.
