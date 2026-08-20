# CAPS Verify architecture

## Trust boundaries

```text
Production server
├── Probe: passive inventory and trace export
└── Gateway: fail-closed action enforcement

Isolated evaluation plane
├── Configuration fingerprint
├── Digital twin builder
├── Scenario registry
├── Target adapter
├── Mutation planner
├── Fixture MCP servers
├── Deterministic predicates
└── Evidence bundle
```

Active attacks belong only in the isolated evaluation plane. The production plane may observe and block, but it must not inject jailbreak content into a live user session.

## Core objects

### Artifact

An attachment or context artifact such as PDF, image, audio, video, `CLAUDE.md`, Skill reference, or MCP result.

### Capability

An MCP tool, plugin integration, Skill, script, or other callable capability. Store its provider, version, permissions, declared side effects, actual side effects, and trust state.

### Action

A candidate tool invocation with data sources, sensitivity, destination, side effect, user approval, and provenance.

### Run result

A complete trace, policy decisions, state-before/state-after snapshots, and deterministic attack/utility outcomes.

## Defense ablations

| Mode | Meaning |
|---|---|
| `none` | No runtime policy enforcement |
| `prompt_only` | Contextual policy only; no hard action boundary |
| `action_gateway` | Deterministic policy before every synthetic action |
| `full_stack` | Capability preflight plus action gateway |

## Evidence integrity

Every run writes canonical JSON/JSONL and a SHA-256 manifest. A later milestone should add Sigstore/SLSA-style attestations, runner-container digests, and a signed Security Card.
