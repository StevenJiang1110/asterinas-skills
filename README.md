# Asterinas Skills

Codex skills for Asterinas development workflows.

## Available Skills

- `asterinas-validate-workflow`: chooses the right Asterinas validation and commit hygiene workflow after code changes.
- `publish-existing-skill`: imports an existing local Codex skill into this GitHub skill collection and pushes it.

## Install

Clone the repository and copy the skills you want into your Codex skills directory:

```bash
git clone https://github.com/StevenJiang1110/asterinas-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -a asterinas-skills/skills/asterinas-validate-workflow "${CODEX_HOME:-$HOME/.codex}/skills/"
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
