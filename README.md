# Asterinas Skills

Codex skills for Asterinas development workflows.

## Available Skills

- `asterinas-validate-workflow`: chooses the right Asterinas validation and commit hygiene workflow after code changes.
- `publish-existing-skill`: imports an existing local Codex skill into this GitHub skill collection and pushes it.
- `technical-writing`: drafts technical documents with concrete problem statements, causal explanations, precise semantic distinctions, and actionable proposals.
- `linux-source-reader`: locates, fetches, navigates, and explains Linux kernel source code and its build/configuration wiring.
- `ai-code-antipatterns`: reviews, judges, or fixes recurring AI-generated code anti-patterns using an embedded evidence catalog.

## Install

Clone the repository and copy the skills you want into your Codex skills directory:

```bash
git clone https://github.com/StevenJiang1110/asterinas-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -a asterinas-skills/skills/asterinas-validate-workflow "${CODEX_HOME:-$HOME/.codex}/skills/"
```

To install `technical-writing` and `linux-source-reader`:

```bash
cp -a asterinas-skills/skills/technical-writing "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -a asterinas-skills/skills/linux-source-reader "${CODEX_HOME:-$HOME/.codex}/skills/"
```

To install the AI code anti-pattern skill at
`${CODEX_HOME:-$HOME/.codex}/skills/ai-code-antipatterns`:

```bash
cp -a asterinas-skills/skills/ai-code-antipatterns "${CODEX_HOME:-$HOME/.codex}/skills/"
```

To install every skill in this repository:

```bash
git clone https://github.com/StevenJiang1110/asterinas-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
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
