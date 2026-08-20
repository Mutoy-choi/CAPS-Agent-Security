# CAPS Benchmark Data Contribution Terms — Draft v1

> **Draft for product design and legal review.** This file is not a substitute for counsel and should not be used as final customer terms without review.

These terms describe the optional submission of CAPS Verify evaluation results to a CAPS-operated collector.

## 1. Explicit opt-in

Telemetry is disabled by default. A Contributor submits data only after an authorized administrator:

1. configures a collector endpoint and authentication token;
2. selects a privacy mode and data-use purpose; and
3. passes `--accept-contribution-terms` or enables an equivalent reviewed organization setting.

Installing the package, Plugin, Skill, or MCP server alone does not constitute consent and must not trigger transmission.

## 2. Contributor authority

The Contributor represents that it has authority to submit the selected evaluation data and that doing so complies with its contracts, privacy notices, employment rules, and applicable law.

The Contributor must not submit data belonging to another person or organization without authorization.

## 3. Data that may be submitted

### `aggregate_only`

- model or target alias selected by the Contributor;
- benchmark and scenario versions;
- configuration fingerprint;
- aggregate ASR, utility, false-block, data-flow, and composition metrics;
- evidence-file hashes;
- tenant, project, and installation identifiers selected by the Contributor.

### `redacted_runs`

Includes the fields above plus per-run outcome metadata such as scenario ID, variant, defense mode, success booleans, and action counts.

It does **not** include raw prompts, attachment contents, tool arguments, tool results, final fixture state, credentials, customer records, or chain-of-thought.

## 4. Prohibited submissions

The Contributor must not submit:

- passwords, API keys, cookies, credentials, or authentication material;
- personal information or customer records;
- confidential source documents or production prompts;
- raw email, Drive, CRM, payment, health, employment, or financial content;
- regulated or unlawful content;
- data that the Contributor is not authorized to share.

CAPS may reject, quarantine, or delete a submission that appears to violate these restrictions.

## 5. Data-use choices

### `service_operation`

CAPS may store and process submitted data only to provide the evaluation service, generate the Contributor's reports, secure the service, prevent abuse, debug failures, and satisfy legal obligations.

### `pooled_research`

In addition to `service_operation`, the Contributor grants CAPS permission to use submitted aggregate metrics and redacted run outcomes to:

- improve attacks, defenses, scenarios, scoring, and release gates;
- create de-identified cohort statistics and benchmark baselines;
- train or evaluate internal ranking, anomaly-detection, and risk models;
- publish aggregate findings that do not identify the Contributor without separate permission.

Raw customer content is not accepted under either mode.

## 6. Ownership and license

The Contributor retains ownership of its submitted data. The Contributor grants CAPS a limited license to host, copy, process, analyze, and create derived statistics for the selected data-use purpose.

CAPS retains ownership of the benchmark software, scenario taxonomy, scoring methodology, derived benchmark baselines, and independently created models. Any broader commercial data right should be set out in a separately negotiated agreement.

## 7. Retention and deletion

The Contributor selects a requested retention period. Production policy should define a maximum retention period and backup-deletion schedule.

A deletion request should include the organization ID, project ID, installation ID, configuration fingerprint, submission receipt, and approximate submission time. Legal or security holds may delay deletion where required.

## 8. Security and tenant separation

Production deployments should use:

- TLS in transit and encryption at rest;
- per-tenant credentials rather than a shared token;
- role-based access and immutable audit logs;
- tenant-separated storage and query controls;
- secret rotation and rate limiting;
- regular deletion and access reviews.

The included collector is a development prototype and should be placed behind an authenticated HTTPS gateway before non-local use.

## 9. No safety certification

A submitted result describes only the tested configuration, scenarios, model snapshot, defenses, and attack budget. It is not a guarantee that a model or agent is safe, secure, compliant, or jailbreak-proof.

## 10. Versioning

The CLI records the accepted terms version in every submission. Material changes require a new terms version and renewed acceptance.
