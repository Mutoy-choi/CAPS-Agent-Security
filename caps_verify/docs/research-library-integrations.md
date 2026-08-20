# Research-backed profiles and library integrations

CAPS Verify includes **original synthetic canary profiles informed by published research** and optional bridges to established evaluation libraries.

It does not copy or redistribute third-party benchmark datasets, and a CAPS profile name does not mean that paper-reported ASR has been reproduced.

## Bundled profiles

| Profile | Included strategies | Typical use |
|---|---|---|
| `core` | paired benign control, PromptInject-style attachment boundary conflict, AgentDojo-style tool-output injection, MCPTox-style tool metadata poisoning, cross-surface composition | fast default smoke and regression suite |
| `adaptive` | `core` plus FITD-style progressive multi-turn commitment and a PyRIT-ready adaptive seed | adaptive and multi-turn evaluation |
| `reasoning` | `core` plus a CoT-Hijacking-inspired long benign-context dilution diagnostic | reasoning and long-context regression |
| `multimodal` | `core` plus a FigStep-inspired typographic image with harmless fixture instructions | native image-ingestion safety |
| `full` | all profiles | release and research runs |

All probes use only these synthetic fixture actions:

```text
caps_fixture_create_summary
caps_fixture_external_sink
caps_fixture_delete_canary
```

The last two are forbidden benchmark actions. They do not perform network writes or delete host files.

## Install optional libraries

From `caps_verify/`:

```bash
pip install -e ".[research]"
```

This installs:

- Inspect AI
- PyRIT
- AgentDojo
- Pillow for native typographic-image probes

To also install garak on a supported Python version:

```bash
pip install -e ".[research-all]"
```

Individual extras are available:

```bash
pip install -e ".[inspect]"
pip install -e ".[pyrit]"
pip install -e ".[garak]"
pip install -e ".[agentdojo]"
pip install -e ".[multimodal]"
```

Check the current environment without importing or configuring the libraries:

```bash
caps-verify research doctor
```

## Explore the built-ins

```bash
caps-verify research list
caps-verify research describe --profile core
caps-verify research sources
caps-verify research preview --profile reasoning
```

Write an Attack Pack that the Shadow Worker can use:

```bash
caps-verify research build \
  --profile full \
  --output artifacts/caps-research-full.json

caps-verify-shadow-worker \
  --attack-pack artifacts/caps-research-full.json \
  --upstream-base-url http://127.0.0.1:8788 \
  --api-key local-evaluation-key \
  --provider openai \
  --once
```

The same profiles can be selected directly:

```bash
caps-verify-shadow-worker --attack-pack builtin:core ...
caps-verify-shadow-worker --attack-pack builtin:adaptive ...
caps-verify-shadow-worker --attack-pack builtin:reasoning ...
caps-verify-shadow-worker --attack-pack builtin:multimodal ...
caps-verify-shadow-worker --attack-pack builtin:full ...
```

## Export a library bridge bundle

```bash
caps-verify research export \
  --profile full \
  --output artifacts/research-full \
  --endpoint http://127.0.0.1:8788/v1/chat/completions \
  --model your-model-id
```

Generated files:

```text
caps-attack-pack.json       native CAPS Shadow Worker pack
inspect-dataset.jsonl       auditable normalized Inspect records
pyrit-seeds.prompt          PyRIT SeedDataset-compatible JSON/YAML
agentdojo-scenarios.json    utility/security mapping for a local custom suite
garak-rest.json             garak RestGenerator configuration
artifacts/*.png              native typographic image when Pillow is installed
SOURCES.md                   paper, library, version, license and usage provenance
manifest.sha256.json         artifact hashes
```

A non-local REST endpoint is rejected unless `--allow-remote-target` is supplied. That flag is not authorization by itself; the operator remains responsible for ensuring the endpoint is owned or explicitly approved for testing.

## Inspect AI native task

Install the `inspect` extra, then run from the `caps_verify/` checkout:

```bash
inspect eval \
  src/caps_verify/integrations/inspect_task.py@caps_research \
  -T profile=core \
  --model your-provider/your-model
```

The task uses Inspect's tool loop and deterministic fixture-tool scoring. Inspect accuracy on attack rows is **defense success**, so attack success for those rows is `1 - accuracy`. Score metadata also records `attack_success` and the research-source IDs.

## PyRIT

The export bundle writes a JSON-formatted YAML file accepted by PyRIT's `SeedDataset.from_yaml_file`:

```python
from pyrit.models import SeedDataset

dataset = SeedDataset.from_yaml_file("artifacts/research-full/pyrit-seeds.prompt")
```

The FITD-style multi-turn profile preserves role and sequence information. The multimodal profile includes an `image_path` seed when Pillow rendered the artifact.

## garak

The generated file follows garak's `rest.RestGenerator` option shape:

```bash
export CAPS_EVALUATION_API_KEY=local-placeholder
garak --target_type rest -G artifacts/research-full/garak-rest.json
```

CAPS defaults the generated connector to localhost. garak's own probes and detectors remain upstream components; CAPS does not vendor them.

## AgentDojo

AgentDojo's API is documented as under development, so CAPS exports a versioned bridge manifest rather than monkey-patching an installed suite. Each row contains:

- paired user task and injection family;
- benign utility goal;
- security goal;
- tool-metadata-poisoning flag;
- provenance IDs.

Use it to build a local custom suite pinned to the installed AgentDojo version.

## Provenance policy

The machine-readable registry is packaged at:

```text
caps_verify/src/caps_verify/resources/research_registry.json
caps_verify/src/caps_verify/resources/research_profiles.json
```

Every built-in probe records:

```text
strategy
source_ids
library_ids
family
modality
tags
```

When publishing results, report the exact CAPS commit, profile, model snapshot, provider route, query/tool budget, optional-library versions, valid/excluded runs, and confidence intervals.
