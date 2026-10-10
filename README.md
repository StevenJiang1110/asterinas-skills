# Asterinas Skills

A personal collection of Codex skills maintained by StevenJiang1110 for Asterinas and systems development workflows. This repository is not an official Asterinas project and is not maintained or endorsed by the Asterinas organization.

## Available Skills

- `asterinas-validate-workflow`: chooses the right Asterinas validation and commit hygiene workflow after code changes.
- `asterinas-regression-test`: writes and reviews Asterinas regression tests using the project's macro conventions and Linux/Asterinas validation workflow.
- `publish-existing-skill`: imports an existing local Codex skill into this GitHub skill collection and pushes it.
- `technical-writing`: drafts technical documents with concrete problem statements, causal explanations, precise semantic distinctions, and actionable proposals.
- `linux-source-reader`: locates, fetches, navigates, and explains Linux kernel source code and its build/configuration wiring.
- `ai-code-antipatterns`: reviews, judges, or fixes recurring AI-generated code anti-patterns using an embedded evidence catalog.

## Install

Clone the repository and create your Codex skills directory:

```bash
git clone https://github.com/StevenJiang1110/asterinas-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
```

To install individual skills, copy the ones you want:

```bash
cp -a asterinas-skills/skills/asterinas-validate-workflow "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -a asterinas-skills/skills/asterinas-regression-test "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -a asterinas-skills/skills/publish-existing-skill "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -a asterinas-skills/skills/technical-writing "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -a asterinas-skills/skills/linux-source-reader "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -a asterinas-skills/skills/ai-code-antipatterns "${CODEX_HOME:-$HOME/.codex}/skills/"
```

To install every skill in this repository:

```bash
cp -a asterinas-skills/skills/* "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart Codex after copying skills so they are rediscovered.

## Repository Layout

```text
skills/
  <skill-name>/
    SKILL.md
    agents/openai.yaml
```

Each skill is self-contained. Repository-level installation and maintenance notes belong in this README.
