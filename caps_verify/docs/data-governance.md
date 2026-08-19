# CAPS Verify data governance

## Goal

Build a proprietary agent-security dataset from **authorized, structured evaluation evidence**, not from covert collection of customer prompts or files.

The intended data flywheel is:

```text
Customer runs CAPS Verify locally
        ↓
Raw prompts, files, and tool payloads remain local
        ↓
Customer reviews an aggregate or redacted submission
        ↓
Explicit opt-in transmission
        ↓
Tenant-isolated collector
        ↓
Benchmark baselines, drift models, attack ranking, and defense research
```

## Default rule

Telemetry is off by default. Installing a Plugin, Skill, MCP server, package, or server Probe does not transmit data.

Every transmission requires:

- an explicitly configured endpoint;
- an authentication credential;
- organization, project, and installation identifiers;
- a selected privacy mode;
- a selected data-use purpose;
- acceptance of a versioned contribution agreement.

## Privacy modes

| Mode | Submitted | Not submitted |
|---|---|---|
| `aggregate_only` | Target alias, benchmark version, configuration fingerprint, aggregate ASR/FPR/utility/composition metrics, evidence hashes | Run rows, prompts, attachments, tool arguments, tool results, final state |
| `redacted_runs` | Everything in `aggregate_only`, plus scenario/variant/defense labels, outcome booleans, and action counts | Prompts, attachments, tool arguments, tool results, final state, credentials, customer content |

`aggregate_only` is the recommended default.

## Data-use purposes

### Service operation

Use data only for the customer's reports, service reliability, security, debugging, abuse prevention, and legal obligations.

### Pooled research

A separate opt-in that permits de-identified aggregate metrics and redacted run outcomes to improve:

- attack-family coverage;
- defense-ablation analysis;
- composition-risk estimates;
- model and agent safety drift baselines;
- scenario prioritization;
- attack-candidate ranking;
- comparative cohort statistics.

Do not infer pooled-research consent from product use.

## Enterprise dataset design

The high-value proprietary tables should be structured, low-content data rather than raw customer logs.

### Configuration table

```text
configuration_fingerprint
model_provider
model_alias
model_snapshot
agent_host
attachment_pipeline_version
skill_digest
plugin_digest
mcp_schema_digest
policy_digest
defense_stack_digest
```

### Evaluation table

```text
scenario_family
surface
modality
attack_operator
composition_group
defense_mode
attack_budget
attack_success
benign_task_success
false_block
unauthorized_tool_invocation
unauthorized_data_flow
latency_bucket
cost_bucket
```

### Drift table

```text
previous_configuration_fingerprint
current_configuration_fingerprint
changed_components
asr_delta
utility_delta
false_block_delta
release_gate_result
```

### Provenance summary table

```text
source_type
capability_type
action_type
destination_class
sensitivity_class
policy_decision
executed
```

This is enough to train attack rankers, risk models, and regression detectors without ingesting customer documents.

## Tenant isolation

The prototype collector hashes organization and project identifiers before using them in storage paths. A production implementation should add:

- per-tenant API credentials;
- row-level or database-level tenant isolation;
- encryption at rest with managed keys;
- role-based admin access;
- immutable access logs;
- rate and payload limits;
- deletion workflows;
- backup-expiration controls;
- customer-visible submission receipts.

A single global bearer token is acceptable only for local development.

## Retention

Recommended defaults:

| Data | Default | Maximum without renewed purpose review |
|---|---:|---:|
| Aggregate metrics | 365 days | 3 years |
| Redacted run outcomes | 90 days | 1 year |
| Authentication/audit events | 180 days | 1 year |
| Raw prompts or attachments | Not accepted | Not accepted |

Actual retention must be defined by customer contract and applicable law.

## Deletion

A deletion request should resolve all submissions linked to:

```text
organization_id
project_id
installation_id
configuration_fingerprint
receipt_id
```

Deletion should cover primary storage, analytics copies, and backups according to a documented schedule.

## Data quality

Pooled data is useful only when evaluation metadata is comparable. Require:

- pinned benchmark and scenario versions;
- pinned target aliases or model snapshots;
- configuration fingerprints;
- explicit attack budgets;
- valid-run counts and exclusions;
- confidence intervals;
- clean-task controls;
- evidence-manifest hashes.

Do not combine paper-reported ASR, production incidents, synthetic smoke tests, and independent evaluations without a source-quality label.

## Publication

External reports should publish cohort-level statistics only when:

- the cohort is large enough to avoid re-identification;
- customers are not named without separate permission;
- attack details do not create immediate unpatched risk;
- uncertainty and evaluation scope are visible;
- coordinated disclosure has been completed where necessary.

## Prohibited design patterns

- Silent telemetry hidden in a Skill, Plugin, Hook, or MCP tool.
- Uploading raw prompts or attachments under an ambiguous “diagnostics” label.
- Reusing service-operation data for model training without separate consent.
- Mixing tenant data without access controls.
- Claiming ownership over customer raw content.
- Treating ASR as a universal model score without the evaluated configuration.
