# Smoothing seams, designing locating shoulders and cropping fit coupons

[中文](seams-and-coupons.md)

## Find the surface that binds

Record the seam, insertion axis and physical scale in the assembly master. Separate the pair. Use a fixed camera and raking light to inspect the visible seam, hidden cut, peg root and socket mouth. Take a section along the insertion axis. Compare with the original sculpt to identify a deliberate garment edge, eyelash or hair tip. Check the exported STL section and sliced layer contours when the preview shows jagged edges. Shading and support marks can resemble a mesh defect.

- **Steps, spikes or uneven facets on a hidden cut.** Select the artificial cut faces and a narrow transition band along connected faces. Pin the surrounding sculpt, straight peg shank and socket wall. Remesh and relax locally, reduce the effect to zero at the edge of the band, and repair folded triangles. Inspect the opposite side of thin hair shells.
- **A ragged visible seam.** Draw one fair boundary following a fold, hairline or paint boundary in assembly coordinates. Use it to trim both parts and put relief on the inside. Try a short section and reassemble it to check for daylight, a step or lost detail. Rounding each half independently can widen the visible gap.
- **A peg enters but stops short.** Section the assembly to find the first contact. Add bottom clearance if the tip bottoms out. If the shoulder catches, correct its seat. If several pins bind, check their common insertion direction and the allowance at the secondary sockets. Inspect the layer preview for support inside a bore or a missing wall. When only a physical sample binds, inspect first-layer expansion, flow and paint buildup.

## Guide insertion with the peg and control depth at the shoulder

Locate the joint in hidden stock on both halves. A flat on a D key controls rotation. Offset the entire socket profile so the flat also gets per-side clearance. Add a short lead-in and retain enough straight engagement beyond it. Measure the peg root, thinnest remaining socket wall, straight engagement and axial clearance beyond the tip. Where multiple pegs engage together, choose the primary locator and relieve the secondary socket in the direction errors accumulate. Recheck rotational play.

Where a waist, hip or sock opening has enough material, put a flat annular shoulder around the peg and a matching coaxial counterbore with a receiving land in the other part. Set shank clearance, radial clearance at the shoulder and axial allowance independently. Inspect the stock behind the full circumference, especially on a sloping seam. At thin shells or narrow cuffs, a short lead-in, a small key or shallow registration with spot glue can preserve the wall. For a single-leg figure, also trace the load from the base to the hip.

Compare the same radii and angles in the same assembled pose before and after revision. Measure peak-to-peak height along the insertion axis, separation between the two lands and where they first contact. Record units, sample count and intentional reliefs. The height span includes the original slope and describes the modeled seat. Use matched close-ups to inspect the seam itself and several silhouettes to check the overall likeness. Recheck the exported solids for self-intersections, overlap at rest and obstructions during withdrawal.

## Take the test pieces directly from the production geometry

1. Pick a joint that can answer a specific build question, such as wobble at a load-bearing sock or binding at a small hair key. Restore the two final parts from the same revision to their shared assembly coordinates in millimetres at 100% scale. **Intersect each part separately with the same crop solid.** Retain the peg tip, root, lead-in, straight socket, bottom, shoulder and surrounding walls. Put gripping flats or a print base away from mating surfaces.
2. Overlay a section of each coupon on its parent part. Check that the crop preserved the socket bottom, complete peg and shoulder, and excluded nearby strands. A single-key sample tests local fit. To test pin spacing or simultaneous engagement, crop both pegs and sockets together. Check the head assembly sequence on the complete subassembly.
3. Apply each part’s production print orientation. Match material, nozzle, line width, layer height, flow, compensation and support contacts. If a coupon gets a flat-down orientation for convenience, document the change and its possible effect on layer direction, supports or bore size. Reopen and slice the coupons separately. Inspect support access and wall paths, and report material and time separately from the production set.
4. Remove supports and loose strands, align the flat and push along the axis. Record where resistance starts, whether the shoulder seats, whether it rocks, and whether it pulls out along the intended path. To test a painted joint, reproduce the production masking, primer and finish. Apply corrections to the production pair, recrop the samples and recheck adjoining parts. Record digital checks, slice results and physical observations separately.

### Crop with the helper

[extract_fit_coupons.py](../scripts/extract_fit_coupons.py) uses a coaxial cylindrical crop. The command below assumes a socket mouth at the origin and insertion along +Z. Run it from the skill directory and substitute the production files and measured dimensions in millimetres.

```sh
python -X utf8 scripts/extract_fit_coupons.py peg.stl socket.stl samples/waist --center 0 0 0 --axis 0 0 1 --radius 8 --behind 4 --ahead 10
```

`--behind` extends from the mouth towards the peg root. `--ahead` extends into the socket. Choose a radius that includes the entire shoulder and nearby wall. The new output directory contains `male.stl` and `female.stl` in assembly coordinates for overlay checks. Apply the production print orientations afterwards. If the cylinder captures separate bodies, adjust the crop or select the joint region with a shaped cutter in CAD.
