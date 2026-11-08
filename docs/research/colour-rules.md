# Colour step: why rules first, and how they handle chalk (2026-11-08)

## The hard part
Hold colour is easy until chalk and lighting get involved:
- **Chalk** is white magnesium carbonate, and it collects on the grip surface. A heavily
  used red hold shows a white centre with red edges. Averaging its pixels gives pink,
  which is the worst possible error, because pink and red are separate routes at most
  gyms.
- **Pink vs red by hue is unreliable.** Under warm LED lighting both sit near hue 0°/360°.
  What actually separates them is pigment saturation: red pigment is near-fully
  saturated and darker, while pink is a red tint (less saturated, lighter).
- **White holds look like chalk.** A rule that drops low-saturation bright pixels deletes
  a white hold entirely.

## Decisions
1. **Grey-world white balance** before anything else, with the scale computed on
   **wall pixels only** (outside all masks) when a wall mask is available. Walls are
   near-neutral, while the holds are deliberately saturated and would bias a whole-image
   grey-world.
2. **Chalk pixels are dropped** inside each mask: HSV `S < chalk_s_max` and
   `V > chalk_v_min`.
3. **Per-pixel voting** over the pixels that remain. Each pixel votes for a hue
   *family*: red-pink, orange, yellow, green, blue, purple, or achromatic (black, grey,
   white by brightness).
4. **Pink vs red uses saturation and lightness, not hue.** Among red-pink pixels, take
   the most saturated quantile (chalk only ever lowers saturation, so the top quantile
   is the pigment). It's red if that quantile's saturation is at least `red_s_min` and
   its Lab L* is at most `red_l_max`, otherwise pink.
5. **White rule with the edge ring.** If most of the mask is chalk-like, look at the
   ring just inside the mask boundary (the sides of the hold, which hands rarely
   touch). If the ring is also achromatic and bright, the hold is white. If the ring is
   coloured, vote on the ring alone.
6. **Crop classifier second.** A small timm model (MobileNetV3-Large by default for CPU
   inference on Spaces, ResNet18 as the alternative) is trained on labelled crops. The
   rules give an explainable baseline and a confidence. The classifier is used when it
   beats the rules on the val set, and the eval reports both.

All thresholds and the colour list live in `configs/colours.yaml`. The same file
generates the Label Studio colour choices, so adding a colour is one edit.

## Rejected
- **k-means clustering per image** (NeuralClimb): unsupervised, so the clusters don't
  line up with the gym's named colours, and chalk forms its own cluster.
- **Hue-only thresholds**: these fail on pink vs red, the one pair the exit criteria
  single out.
- **Classifier only, no rules**: it needs hundreds of labelled crops before it's useful,
  and it isn't explainable when it fails on chalk. The rules work from day one.
