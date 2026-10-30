# media

## Text, images, audio, and multimodal inputs

**Documented:** Sparse text representations support fast conventional classifiers. The scikit-learn example shows that headers/footers/quotes can create easy classification cues and materially change evaluation. [Sparse document classification](https://scikit-learn.org/stable/auto_examples/text/plot_document_classification_20newsgroups.html)

**Decision synthesis:** For text classification, compare TF-IDF plus a linear model against frozen embeddings and fine-tuning; choose from held-out quality, cost and language/domain coverage. Split by originating document/thread/person/source as needed; remove task-inappropriate metadata shortcuts. Keep preprocessing semantics: removing negation, punctuation, case or stop words may destroy task signal.

**Documented:** Transfer learning can freeze a pretrained base, train a new head, then optionally fine-tune with a low learning rate. Keras cautions about batch-normalization state when fine-tuning. [Keras transfer learning](https://keras.io/guides/transfer_learning/)

**Decision synthesis:** With small image/audio datasets, compare frozen pretrained features/head before training from scratch. Check source-domain mismatch, pretrained preprocessing and licenses. Split by patient/device/speaker/video before cropping or augmentation. Validate augmentations preserve the label. Distinguish classification, localization, segmentation, transcription and generation, using task-appropriate labels and metrics; a classifier notebook is not a segmentation pipeline. For multimodal records, align timestamps/entities, define missing-modality behavior and evaluate each modality's contribution and deployment availability.

### Match media annotation to evaluation

| Output | Annotation and candidate metric | Decisions that must be fixed |
|---|---|---|
| Object detection | Boxes/classes and detection AP/recall under specified overlap matching | IoU thresholds, class averaging, object-size slices, duplicate detections, score cutoff and maximum detections |
| Semantic segmentation | Pixel/region masks and per-class Dice or IoU | Background/void handling, samplewise versus global aggregation, tiny objects and empty masks |
| Speech transcription | Verified reference transcript and WER/CER plus task-critical errors | Token/text normalization, language/speaker/noise slices, empty/silent audio and end-to-end latency |

Detection AP is tied to a localization/matching protocol and is not interchangeable with the binary-classification AP function. [Detection mAP implementation](https://lightning.ai/docs/torchmetrics/stable/detection/mean_average_precision.html). Segmentation aggregation and background inclusion can materially change the reported overlap score. [Dice implementation](https://lightning.ai/docs/torchmetrics/stable/segmentation/dice.html). WER/CER use edit-distance-based comparisons; define silence/empty-reference behavior instead of dropping such cases. [JiWER](https://jitsi.github.io/jiwer/)

Use these only for the actual media task. If boxes/masks/transcripts are unavailable, return to annotation design or explicitly change the task; a dataset with only image-level classes does not supply supervised detection ground truth. Keep document/patient/speaker/video groups intact before derived samples are made.
