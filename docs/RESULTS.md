# Results

## Official Challenge Result

Official scores, per-submission metrics, and the current status are maintained on the [Forithmus Research Hub](https://research.forithmus.com/). Open the **MR Report Generation** challenge leaderboard and search for **Medical Image Insights & FDU**. The platform is the authoritative source because evaluation and leaderboard status can change independently of this repository.

This repository does not duplicate leaderboard values. It also does not present local test-set BLEU, ROUGE-L, or label F1 as official challenge metrics. The platform's CRG pipeline extracts clinical labels from generated reports and may differ from a local finding-tag evaluator.

## Local Evaluation

No local metric is reported in this repository because an exact, verifiable mapping from a local evaluation run to the archived submission image and source snapshot is not available here. Local results should only be added with the checkpoint/image identity, input split and sample count, image-selection policy, decoding parameters, and evaluator version. Label them as local, not official. Do not include per-patient outputs, reports, or identifiers.
