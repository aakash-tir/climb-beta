# External training data: public datasets vs YouTube frames

*Design, 2026-11-09. Issue #67. Status: proposed, no code yet.*

## Question
The first ~20 Basecamp photos exist, and more come each session. The owner proposed
adding still frames from climbing YouTube videos (empty boulders, filmed before anyone
climbs) as extra training data. Those frames help only with **hold outlines**: their
colour and tape conventions aren't Basecamp's. Does that beat public labelled hold
datasets, and how should the dataset hold images that carry only some of the labels?

## Recommendation: public datasets now, YouTube frames only as a gated pilot
1. **Use public outline datasets first** (M2): the Roboflow set being pinned in #12 and
   [ClimbInst](https://huggingface.co/datasets/ClimbVision/ClimbInst) (#72, pending a
   licence check). Together they hold about 3,000 labelled wall images from many gyms,
   for a few hours of download and conversion work.
2. **Put the labelling hours into Basecamp photos.** A Basecamp photo takes about the
   same time to label as a YouTube frame (every hold outlined), but it also trains colour
   and tape, can go to val or test, and matches the real gym. Every hour spent on a
   YouTube frame is an hour not spent on that.
3. **Defer YouTube frames to a pilot** (#74). Run it only if the first detector's errors
   on **Basecamp val** cluster in conditions the public data lacks, keep the frames only
   if ~30 pilot frames raise Basecamp val hold recall by ≥ 2 points, and keep them
   private forever.
4. **Build the schema for partial labels now** (#68), so public outline-only data,
   ClimbInst's merged class and any later frames all go through the same guards.

### Comparison

| | Public datasets (Roboflow #12, ClimbInst) | YouTube frames |
|---|---|---|
| Labelled images | ~1,700 (Roboflow `blackcreed`, per a 2025 paper) + 1,509 (ClimbInst, 89k instances) | 0. Each frame needs every hold outlined (~50–90 per wall) |
| Effort to first use | hours: download, convert, licence check, dedupe | frame hunting and screening, plus ~5–10 min/frame with SAM 2 clicks: 100 frames ≈ 10–15 h *(estimate)* |
| Labels | polygons; ClimbInst merges hold + volume into one class | whatever we draw: outlines only |
| Image quality | phone and camera stills | video compression, wide-angle lenses, often motion blur or a climber in shot |
| Variety | many gyms and walls | many gyms; pro-level setting; little gain over public sets |
| Rights | Roboflow: CC BY 4.0 with attribution. ClimbInst: **not stated**, follows its sources (#72) | ToS breach and copyrighted: private forever, never published |
| Usable for val/test | no (not Basecamp) | no (not Basecamp) |

Overlap warning: ClimbInst is partly built from a Roboflow "Climbing Holds and Volumes"
project and the Sláma Kaggle set (Prague and Heidelberg gyms), so using it with #12 needs
dedupe (#71). Other candidates seen and not chosen: smaller Roboflow Universe projects
(`pwals/bouldering-holds`, `rock-climbing-9qwqx/hold-segmentation`, `murasaki/holdbase`:
tens to a few hundred images each), the Kaggle set on its own (already inside ClimbInst),
and *The Way Up* (CVPR 2025 workshop: hold usage in sport-climbing video, not masks).

## Dataset schema: a source manifest per built dataset
Every built YOLO-seg dataset (`data/yolo/<name>/`) gets a `manifest.jsonl`, one record
per image (#68). The YOLO label files stay standard. The manifest says which of those
labels can be trusted, and the guards read it.

```jsonc
{
  "image": "cave-left__IMG_0012",          // stem in images/<split>/
  "source": "basecamp",                    // basecamp | public:roboflow | public:climbinst | youtube
  "source_ref": "cave-left/IMG_0012.jpg",  // wall/photo, dataset@version/id, or video key + time (private)
  "group": "cave-left",                    // dedupe and split unit: wall id, video_key/shot, upstream scene
  "gym": "basecamp",                       // basecamp | other | unknown
  "label_scope": {
    "classes": ["hold", "volume", "tape"], // classes outlined EXHAUSTIVELY in this image
    "class_scheme": "full",                // full | holdlike (hold + volume merged)
    "colour": true,                        // colour sidecar trustworthy (Basecamp palette)
    "start_tape": true                     // tape marks Basecamp starts
  },
  "outline_only": false,                   // true <=> colour == false and start_tape == false
  "mask_quality": "manual",                // manual | sam_corrected | pseudo_box
  "ignore_regions": [],                    // polygons blanked at build: unlabelled tape, people, logos
  "licence": "private:basecamp",           // CC-BY-4.0 | private:basecamp | private:youtube | ...
  "publishable": false,
  "allowed_splits": ["train", "val", "test"]
}
```

Typical records:

| Source | `outline_only` | `label_scope.classes` | `class_scheme` | `allowed_splits` | `publishable` |
|---|---|---|---|---|---|
| Basecamp | false | hold, volume, tape | full | train, val, test | false (until the gym agrees) |
| Roboflow (#12) | true | whatever it labels | full or holdlike | train | true (CC BY 4.0) |
| ClimbInst (#72) | true | holdlike | holdlike | train | per licence |
| YouTube (#75) | true | hold, volume | full | train | **false, always** |

Why each field exists:
- **`label_scope.classes`** — YOLO treats every unlabelled pixel as background. An
  outline-only image with an unlabelled tape strip would teach the detector that tape
  is wall. So anything visible that's out of scope goes in `ignore_regions` and is
  blanked (median wall colour + blur) before training (#69). Holds in scope must be
  outlined exhaustively.
- **`colour` / `start_tape`** — the colour crop loader and any tape/start data use only
  images where these are true, even when a sidecar file exists (#69).
- **`class_scheme`** — ClimbInst's single class can't train a 3-class head; it's used in
  a 1-class pretraining stage instead (#73).
- **`group`** — the unit for dedupe caps (#71) and, for Basecamp, the wall split.
- **`gym`** — a video or public image shot *at Basecamp* could show a test wall. The
  cross-source dedupe fails the build if an external image matches a Basecamp photo.
- **`publishable` / `licence`** — the publishing guards refuse anything not publishable (#70).

## Splits: Basecamp-only val and test
- **Test = Basecamp test walls only.** This is unchanged: `eval/check_exit_criteria.py`
  measures only these, with no pseudo-masks.
- **Val = Basecamp val walls only.** Val picks the checkpoint and drives the YouTube
  go/no-go, so it must reflect real use too. `merge_datasets` already takes val/test
  from the Basecamp dataset. #68 makes that a hard check: any val/test image whose
  `source` isn't `basecamp` raises.
- **External data is train-only.** Public datasets' own val/test splits are folded into
  our train after dedupe. Their scores say nothing about Basecamp.
- **Basecamp split stays by wall** (`data/split_by_wall.py`). A wall keeps its split
  across resets, so new photos of a test wall never reach training.
- **Balance.** About 3,000 external images against a few dozen Basecamp photos would
  make Basecamp ~1% of each epoch. Training is two-stage (#73): a 1-class `holdlike`
  pretrain on all outline sources, then a 3-class fine-tune on Basecamp (repeated to ≥
  ~30% of samples) plus 3-class public data.
- **Colour and start-hold work** (colour rules tuning #36, the classifier, colour eval,
  routes) read only `outline_only: false` images, which today means Basecamp only.

## YouTube frames, if the pilot goes ahead
- **Selection** (#75): from a local video file the owner already has (the public repo
  contains no downloader), sample ~2 fps, split into shots, and drop frames with blur
  (Laplacian variance), motion (frame difference) or a person (stock COCO `person`
  detector). Keep at most a few frames per shot, then dedupe by perceptual hash.
- **Labelling** (#76): a separate Label Studio project with hold/volume masks and an
  `ignore` label, and no colour or tape choices. Outline every hold.
- **Storage:** `data/external/youtube/` (gitignored), never synced to the HF dataset.
  The manifest with video ids and timestamps lives there too, not in git.

## Rights and privacy
- **YouTube frames:** downloading videos breaks YouTube's Terms of Service, and the
  frames are the creators' copyrighted work. They stay on the owner's machine only:
  never in git, never in a public or private HF dataset, never in the Hugging Face
  Space, and never in a published dataset. No video URLs, ids or creator names go in
  committed files. The guards in #70 enforce this.
- **Weights trained on YouTube frames:** this is an owner decision, recorded in #74.
  The proposed default is that the public Space ships only weights trained on public
  and Basecamp data.
- **Public datasets:** keep their licence terms. CC BY 4.0 needs attribution in the
  README's "Data and licences" section. ClimbInst is used only once its terms are
  confirmed (#72).
- **Basecamp photos:** unchanged: gitignored, private HF dataset, never published
  without the gym's permission.

## Issues
| # | Milestone | What | State |
|---|---|---|---|
| #68 | M2 | Source manifest + label scopes; val/test Basecamp-only check | ready |
| #69 | M2 | Outline-only out of colour data; blank ignore regions | after #68 |
| #70 | M2 | Publishing guards (HF sync, Space, gitignore) | after #68 |
| #71 | M2 | Near-duplicate detection across sources | ready |
| #72 | M2 | ClimbInst download + conversion | needs-decision (licence) |
| #73 | M4 | Two-stage training: holdlike pretrain → Basecamp fine-tune | after #68, #72 |
| #74 | M4 | YouTube pilot go/no-go from Basecamp val errors; weights-in-Space decision | blocked on #63 |
| #75 | M2 | Empty-wall frame extractor for local videos | blocked on #74 |
| #76 | M3 | Outline-only Label Studio config + export | blocked on #74 |

## Sources
- ClimbInst: https://huggingface.co/datasets/ClimbVision/ClimbInst
- Roboflow Universe candidates: see `docs/research/datasets-and-labelling.md`; also
  https://universe.roboflow.com/pwals/bouldering-holds-9wavr,
  https://universe.roboflow.com/murasaki/holdbase
- Kaggle (Sláma): https://www.kaggle.com/datasets/tomasslama/indoor-climbing-gym-hold-segmentation
- Blackcreed set size (1,717 images, 63,897 annotations), as cited in:
  https://www.researchgate.net/publication/387283911_Development_of_a_climbing_performance_analysis_tool_using_computer_vision
- The Way Up (CVPR 2025 W): https://arxiv.org/abs/2505.12854
