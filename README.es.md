<div align="center">

# CAPS Unlock Lab

### Reproduce rutas de debilitamiento de restricciones y mide las acciones que realmente ocurren.

**ChatGPT · Codex · Claude Code · Gemini CLI · GitHub Copilot · Cursor · Cline · Windsurf · OpenCode · MCP**

[![CAPS Verify](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-verify.yml)
[![Research Chat](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/caps-app.yml)
[![Distribution](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml/badge.svg)](https://github.com/Mutoy-choi/CAPS-Agent-Security/actions/workflows/distribution.yml)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · **Español**

**Seguridad de agentes de IA · pruebas de prompt injection · evaluación de jailbreak · seguridad MCP · seguridad del uso de herramientas**

[Empieza en tu plataforma](#empieza-en-tu-plataforma) · [Investigación integrada](#investigación-integrada-y-bibliotecas) · [ASR](#cómo-se-mide-el-asr) · [Arquitectura](#un-núcleo-varias-plataformas) · [Solución de problemas](#solución-de-problemas)

</div>

---

## En una frase

CAPS Unlock Lab es una **herramienta de investigación de propósito general que reproduce, en entornos sintéticos autorizados, cómo pueden debilitarse las restricciones de un modelo a través de prompts, archivos de instrucciones, plugins, Agent Skills, herramientas MCP, adjuntos, razonamiento y conversaciones de varios turnos, y mide el resultado mediante ASR**.

CAPS no depende de un proveedor, modelo o CLI concreto. Mantiene las mismas dos Skills canónicas y CAPS Verify Runtime, mientras que cada plataforma recibe únicamente un manifest, una regla o un perfil de agente ligero.

> “Unlock” no significa eludir en secreto las salvaguardas de usuarios reales. Significa reproducir rutas de debilitamiento de restricciones dentro de un synthetic twin de un sistema que te pertenece o para el que tienes autorización explícita, y después validar las defensas.

## Empieza en tu plataforma

### Instalación común más sencilla — macOS / Linux / WSL

```bash
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh | bash -s -- skill
```

Este comando instala las Agent Skills compartidas en rutas de usuario que Codex/OpenCode, Claude Code y GitHub Copilot pueden detectar. Antes de ejecutarlo de forma remota, puedes revisar [install.sh](https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh).

### Windows PowerShell

```powershell
& ([scriptblock]::Create((irm https://mutoy-choi.github.io/CAPS-Agent-Security/install.ps1))) skill
```

### Inicio rápido por plataforma

| Plataforma | Instalación recomendada | Cómo empezar |
|---|---|---|
| **ChatGPT / Codex** | `... install.sh \| bash -s -- codex` | Usa `$caps-agent-security` o `/skills` en Codex |
| **Claude Code** | Usa los dos comandos de Marketplace indicados abajo | `/caps-unlock:caps-agent-security` |
| **Gemini CLI** | `gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update` | `/caps:audit` o una petición en lenguaje natural |
| **GitHub Copilot** | `... install.sh \| bash -s -- copilot` | Usa el custom agent `caps-unlock` o la Skill |
| **Cursor** | Ejecuta `... -- cursor` desde la raíz del proyecto | Pide al agente: “Audita esta configuración con CAPS” |
| **Cline** | Ejecuta `... -- cline` desde la raíz del proyecto | Usa el workflow `/caps-unlock-audit.md` |
| **Windsurf** | Ejecuta `... -- windsurf` desde la raíz del proyecto | Usa el workflow de auditoría de CAPS |
| **OpenCode** | `... install.sh \| bash -s -- opencode` | Detección automática de Skills o invocación explícita |
| **Cualquier agente MCP/API** | `... install.sh \| bash -s -- verify` | Usa `caps-verify-runtime` o el MCP fixture |

Aquí, `...` significa:

```text
curl -fsSL https://mutoy-choi.github.io/CAPS-Agent-Security/install.sh
```

### Claude Code Plugin

```bash
claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security
claude plugin install caps-unlock@caps-labs --scope user
```

### Paquete Plugin para ChatGPT / Codex

La raíz del repositorio y `plugins/caps-unlock/` incluyen `.codex-plugin/plugin.json` y `skills/`. Para usar Codex localmente basta con instalar las Agent Skills. La publicación en un directorio universal de ChatGPT/Codex requiere un proceso independiente de envío y revisión; mientras tanto, utiliza el paquete Plugin local o las Skills.

### Extensión de Gemini CLI

```bash
gemini extensions install https://github.com/Mutoy-choi/CAPS-Agent-Security --auto-update
```

Archivos principales:

```text
gemini-extension.json
GEMINI.md
skills/
commands/caps/audit.toml
commands/caps/install.toml
```

## Compatibilidad de plataformas

| Plataforma | Native package | Skill compartida | Instrucciones del proyecto | MCP/API Runtime |
|---|:---:|:---:|:---:|:---:|
| ChatGPT / Codex | `.codex-plugin` | `.agents/skills` | `AGENTS.md` | Compatible |
| Claude Code | `.claude-plugin` | `.claude/skills` | Claude Plugin | Compatible |
| Gemini CLI | `gemini-extension.json` | `skills/` | `GEMINI.md` | Compatible |
| GitHub Copilot | custom agent | `.github/skills` | `copilot-instructions.md` | Compatible |
| Cursor | rule adapter | referencia la Skill compartida | `.cursor/rules` | Compatible |
| Cline | workflow adapter | referencia la Skill compartida | `.clinerules` | Compatible |
| Windsurf | workflow adapter | referencia la Skill compartida | `.windsurf` | Compatible |
| OpenCode | Agent Skills | `.agents/skills` | `AGENTS.md` | Compatible |
| Otros hosts | — | especificación Agent Skills | depende del host | MCP o HTTP sidecar |

Las rutas detalladas y las diferencias de instalación están en [PLATFORMS.md](PLATFORMS.md).

## Qué evalúa CAPS

CAPS no evalúa únicamente una respuesta del modelo. Examina la **ruta completa por la que el contexto se convierte en una acción con permisos**.

```text
Prompt / Attachment / AGENTS.md / CLAUDE.md / GEMINI.md
Plugin / Skill / MCP metadata / Tool response
                         ↓
                   Model reasoning
                         ↓
                    Tool selection
                         ↓
       synthetic read / write / transfer / delete
                         ↓
      ASR · benign utility · defense effectiveness
```

### Superficies de ataque

| Superficie | Ejemplo de evaluación |
|---|---|
| Instruction files | Conflictos y precedencia entre `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` y reglas del IDE |
| Plugin / extension | Manifests, Skills empaquetadas, cadena de suministro de capacidades y update drift |
| Agent Skills | description, `SKILL.md`, references, scripts, assets y activation |
| MCP / Tool calling | Contaminación de metadata o respuestas, tool selection, confused deputy y escrituras externas |
| Attachments | Indirect prompt injection mediante PDF, documentos, imágenes, audio y vídeo |
| Reasoning / multi-turn | Razonamiento largo, contexto acumulado, composition y safety drift |
| Defenses | Scanner, exchange guard, action gateway, provenance y confirmation |

## Cómo se mide el ASR

CAPS no determina principalmente el éxito preguntando a un LLM Judge si una respuesta “parece peligrosa”. Prioriza comprobar si **se seleccionó de verdad una herramienta sintética prohibida o si cambió realmente el estado del fixture**.

```text
Attachment-to-Action ASR
= ejecuciones de ataque válidas en las que ocurrió una acción sintética prohibida
  ÷ todas las ejecuciones de ataque válidas
```

También se registran:

- ASR por familia de ataque con intervalos de confianza del 95 %
- Defense-Adaptive ASR con un presupuesto fijo
- Benign Task Success Rate
- False Block Rate y Confirmation Burden
- Unauthorized Tool Invocation / Data Flow
- Composition Delta / Ratio
- Safety Drift
- Sobrecoste de latencia, tokens y coste

## Investigación integrada y bibliotecas

CAPS no se limita a enumerar títulos de artículos. **Normaliza probes sintéticos vinculados a sus fuentes en un Attack Pack común y los exporta a ecosistemas de evaluación existentes**.

### Perfiles integrados

| Perfil | Ideas de evaluación adaptadas de la investigación |
|---|---|
| `core` | PromptInject-style attachment conflict, AgentDojo-style tool-output injection, MCPTox-style tool metadata poisoning, paired benign control y composition |
| `adaptive` | `core` + FITD-style progressive multi-turn + PyRIT-ready adaptive seed |
| `reasoning` | `core` + CoT-Hijacking-inspired long benign-context dilution diagnostic |
| `multimodal` | `core` + FigStep-inspired native typographic image |
| `full` | Todos los perfiles integrados |

CAPS no copia prompts originales ni conjuntos de datos peligrosos de artículos externos. Proporciona adaptaciones sintéticas propias basadas únicamente en canaries y fixture tools. Los nombres de los perfiles no implican una reproducción exacta del ASR publicado en los artículos.

```bash
cd caps_verify
caps-verify research list
caps-verify research describe --profile full
caps-verify research sources
```

### Bibliotecas de investigación opcionales

```bash
pip install -e ".[research]"
```

El bundle recomendado incluye:

```text
Inspect AI     Task · Tool loop · Scorer · Log reproducibles
PyRIT          SeedDataset y orquestación adaptive/multi-turn
AgentDojo      agent prompt-injection task y utility mapping
Pillow         renderizado de probes de imágenes tipográficas nativas
```

Para añadir garak en una versión compatible de Python:

```bash
pip install -e ".[research-all]"
```

Comprueba el entorno:

```bash
caps-verify research doctor
```

### Genera todos los bridges con un comando

```bash
caps-verify research export \
  --profile full \
  --output artifacts/research-full \
  --endpoint http://127.0.0.1:8788/v1/chat/completions \
  --model your-model-id
```

La salida incluye bridges para CAPS, Inspect, PyRIT, garak y AgentDojo, canaries de imagen, información de fuentes y licencias, y evidence hashes. Consulta [`caps_verify/docs/research-library-integrations.md`](caps_verify/docs/research-library-integrations.md) para más detalles.

## Experimento local más rápido

```bash
git clone https://github.com/Mutoy-choi/CAPS-Agent-Security.git
cd CAPS-Agent-Security/caps_verify
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gateway,dev]"
pytest
caps-verify demo --output artifacts/demo --repetitions 10
```

Comandos principales:

```bash
caps-verify research list
caps-verify research doctor
caps-verify research build --profile core --output artifacts/core.json
caps-verify-runtime --help
caps-verify-gateway --help
caps-verify-shadow-worker --help
caps-verify-mcp --help
caps-verify demo --output artifacts/demo --repetitions 10
```

## Un núcleo, varias plataformas

```text
skills/                         canonical Skills
├── caps-agent-security/
└── caps-install/

.codex-plugin/                  ChatGPT / Codex package
.claude-plugin/ + plugins/      Claude Code Marketplace
 gemini-extension.json          Gemini CLI extension
.github/skills + agents/        GitHub Copilot
.cursor/rules/                  Cursor adapter
.clinerules/                    Cline adapter
.windsurf/                      Windsurf adapter
.agents/skills/                 Codex · OpenCode · shared discovery
caps_verify/                    Runtime, research profiles, library bridges, MCP
caps_app/                       accessible Research Chat
```

La CI comprueba que las copias específicas de cada plataforma mantengan el mismo significado que `skills/`.

## Qué componente debo instalar

- **Solo necesitas la Skill:** instala `skill`, `codex`, `opencode` o la Skill de Copilot.
- **Necesitas un paquete nativo del host:** usa Claude Code Plugin o Gemini CLI extension.
- **Necesitas ejecutar experimentos ASR reales:** instala CAPS Verify Runtime mediante `verify`.
- **Necesitas bibliotecas de evaluación existentes:** instala el extra `research` o `research-all`.
- **Necesitas una UI para usuarios finales:** prepara Research Chat mediante `chat`.
- **Necesitas un MCP fixture:** instala CAPS Verify y conecta `caps-verify-mcp`.

## Instalación limitada al proyecto

```bash
CAPS_SCOPE=project ./install.sh codex
CAPS_SCOPE=project ./install.sh copilot
./install.sh cursor
./install.sh cline
./install.sh windsurf
```

El instalador no sobrescribe archivos de configuración compartidos. Solo añade reglas, Skills y perfiles de agente específicos de CAPS. Los ejemplos MCP no se activan automáticamente.

## Límites de seguridad

- Evalúa únicamente sistemas que te pertenezcan o para los que tengas autorización explícita.
- Ejecuta ataques activos en sesiones sintéticas aisladas, nunca en conversaciones de usuarios reales.
- No añadas texto jailbreak oculto a la petición de un usuario real.
- No uses credenciales reales, documentos de clientes, pagos, transferencias externas ni herramientas destructivas de producción como fixtures.
- No generes un remote research bridge sin una opción de aprobación explícita.
- Instalar un Plugin o una Skill no activa por sí solo telemetry, contribución de datos, MCP, hooks ni gateways.
- No presentes el ASR sintético como certificación universal de seguridad de un modelo comercial.

Consulta [SECURITY.md](SECURITY.md) para informar de vulnerabilidades.

## Solución de problemas

### La Skill no aparece

1. Confirma que `SKILL.md` existe en la ruta de la plataforma.
2. Elimina copias antiguas de la misma Skill.
3. Reinicia la sesión del Agent o de la CLI.
4. Prueba una invocación explícita: `/skills` en Codex, `/caps-unlock:caps-agent-security` en Claude Code o `/caps:audit` en Gemini CLI.

### Falla la instalación del Plugin o de la extensión

- Confirma que Git y la CLI correspondiente están instalados.
- Confirma que el repositorio es público.
- Ejecuta `claude plugin marketplace update caps-labs` o `gemini extensions update caps-unlock-lab`.
- Usa las rutas manuales de [PLATFORMS.md](PLATFORMS.md).

### El ASR difiere de la aplicación real

El Shadow ASR predeterminado usa una configuración sintética estandarizada de herramientas. Para reflejar un System Prompt, Plugin, Skill, permisos MCP y flujo de aprobación reales, necesitas construir un capability twin y un host probe.

### Los resultados difieren de un artículo

Los perfiles integrados normalizan ideas de investigación en acciones fixture seguras. El modelo, los datos, TTS/OCR, el judge, el attack budget, la configuración de herramientas y las condiciones de éxito pueden diferir del artículo original, por lo que las cifras no deben considerarse equivalentes de forma directa.

## Enlaces

- Discovery site: `https://mutoy-choi.github.io/CAPS-Agent-Security/`
- Source: `https://github.com/Mutoy-choi/CAPS-Agent-Security`
- Platform matrix: [PLATFORMS.md](PLATFORMS.md)
- Research integrations: [caps_verify/docs/research-library-integrations.md](caps_verify/docs/research-library-integrations.md)
- Distribution checklist: [DISTRIBUTION.md](DISTRIBUTION.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## Estado

CAPS Unlock Lab es un proyecto de investigación en rápida evolución. Registra con cada resultado el model snapshot, host, attack-pack version, optional-library versions, presupuesto, defense configuration, valid/excluded runs, confidence interval y evidence hash.