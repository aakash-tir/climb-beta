# Prior art and approach (researched 2026-11-08)

## Question
How have others found climbing holds and grouped them into routes, and what went wrong
for them?

## What exists
- **NeuralClimb** ([github.com/scsukas8/NeuralClimb](https://github.com/scsukas8/NeuralClimb)):
  detects holds, then clusters hold colours with k-means in HLS space. Reported failures:
  shadows taken for holds, and holds close to the wall colour missed. The colour step
  was unsupervised, so it couldn't be tuned per gym.
- **Indoor-Climbing-Hold-and-Route-Segmentation**
  ([github.com/xiaoxiae/…](https://github.com/xiaoxiae/Indoor-Climbing-Hold-and-Route-Segmentation)):
  a university project that segments holds and routes, with data and weights on Kaggle.
  It's the closest prior art to our pipeline.
- **ClimbFind** ([github.com/Huang-Vincent/ClimbFind](https://github.com/Huang-Vincent/ClimbFind)):
  hold detection plus colour isolation. Little documentation.
- **Ascend** ([github.com/imix8/Ascend](https://github.com/imix8/Ascend)): YOLOv8 for
  technique analysis. Holds are found by colour thresholding plus edge detection.
- **Roboflow bouldering blog** ([blog.roboflow.com/bouldering](https://blog.roboflow.com/bouldering/)):
  the same two-stage design we chose. A colour-blind detector finds holds, then each
  crop goes to a colour classifier. The author notes the classifier was tuned to their
  own gym's colours. That's the main reason our Phase 1 targets a single gym.
- **IJME paper 2509** (2025, [ubplj.org](https://www.ubplj.org/index.php/tesd/article/download/2509/2022/8337)):
  compares classical colour clustering with deep segmentation for hold and route mapping.
  It reports that edge and blob methods are fragile to parameter changes.

## Lessons we're taking
1. **Detection must not depend on colour.** Every project that segmented by colour
   missed holds that match the wall, and also confused shadows with holds. The detector
   trains with strong hue/saturation augmentation so it learns shape and texture.
2. **Colour is a separate, gym-specific step.** The Roboflow author's comment and
   NeuralClimb's k-means failures both point here. Our colour step is explicit rules
   first (explainable, easy to tune), then a small crop classifier trained on our own
   labels.
3. **Chalk and pink vs red are where colour fails.** None of the prior projects handle
   chalk explicitly. That's our "hard part" (see `colour-rules.md`).

## Sources
- https://github.com/scsukas8/NeuralClimb
- https://github.com/xiaoxiae/Indoor-Climbing-Hold-and-Route-Segmentation
- https://github.com/Huang-Vincent/ClimbFind
- https://github.com/imix8/Ascend
- https://blog.roboflow.com/bouldering/
- https://www.ubplj.org/index.php/tesd/article/download/2509/2022/8337
