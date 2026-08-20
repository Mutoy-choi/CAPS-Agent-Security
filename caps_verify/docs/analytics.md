# Collector analytics

CAPS Verify can turn accepted collector submissions into a tenant-free model and defense summary.

## Default: pooled research only

```bash
caps-verify summarize-collector \
  --storage .caps-collector/submissions \
  --output artifacts/pooled-model-asr.json
```

The default purpose filter is `pooled_research`. Submissions accepted only for `service_operation` are not included in the cross-customer research summary.

## Private service operations

An authorized operator may summarize service-operation submissions for customer reporting or service monitoring:

```bash
caps-verify summarize-collector \
  --storage .caps-collector/submissions \
  --purpose service_operation \
  --output artifacts/service-operations.json
```

Do not use this output for pooled model training or cross-customer research without separate permission.

## Output

The generated JSON contains:

```text
source file count
included submission count
invalid submission count
duplicate count
purpose filter
model/target alias
per-defense run counts
A2A-ASR
benign task success
false-block rate
unauthorized tool invocation rate
unauthorized data-flow rate
```

The summary excludes tenant identifiers, raw content, and per-run rows.

## Weighting

Rates are recomputed from accumulated counts instead of averaging customer percentages. This prevents a five-run submission and a five-thousand-run submission from receiving equal statistical weight.

## Deduplication

Submissions are deduplicated using:

```text
tenant identity
selected data-use purpose
configuration fingerprint
evidence manifest
```

This allows the same evaluation to be used separately for service operation and pooled research only when both purposes were explicitly selected in separate submissions.

## Interpretation

A target alias is only comparable when the following are also compatible:

- model snapshot;
- benchmark and scenario version;
- attack budget;
- attachment pipeline;
- available Plugin, Skill, and MCP capabilities;
- defense configuration;
- exclusion and valid-run policy.

The current smoke target must never be presented as a real model result. Replace it with a pinned `TargetAdapter` before using collected ASR in a Security Card or commercial comparison.
