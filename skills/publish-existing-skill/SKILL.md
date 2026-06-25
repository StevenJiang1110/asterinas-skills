---
name: publish-existing-skill
description: Publish an existing local Codex skill into a GitHub-hosted skill collection. Use when Codex needs to copy a skill from $CODEX_HOME/skills or another source, preserve its folder structure, add or update repository installation documentation, validate SKILL.md metadata, commit the change, and push it to a remote repository.
---

# Publish Existing Skill

## Overview

Use this workflow to import an already-authored skill into a shared repository without changing the source skill in place. Keep repository-level documentation outside individual skill folders.

## Workflow

1. Confirm the source skill path and destination repository path.
2. Inspect the source skill:

   ```bash
   find <source-skill> -maxdepth 3 -type f -print | sort
   sed -n '1,120p' <source-skill>/SKILL.md
   ```

3. Copy the skill directory under `skills/<skill-name>/` in the destination repository. Preserve bundled `agents/`, `scripts/`, `references/`, and `assets/` directories.
4. Remove only generated caches or local build artifacts. Do not remove files that are part of the skill contract.
5. Validate each imported or edited skill:

   ```bash
   python3 /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name>
   ```

   If validation fails because the host Python cannot import PyYAML, retry from
   a temporary virtual environment instead of installing packages globally:

   ```bash
   python3 /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name> 2>/tmp/skill-validate.err || {
     if grep -q "No module named 'yaml'" /tmp/skill-validate.err; then
       python3 -m venv /tmp/skill-validate-venv
       /tmp/skill-validate-venv/bin/python -m pip install PyYAML
       /tmp/skill-validate-venv/bin/python /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name>
     else
       cat /tmp/skill-validate.err >&2
       exit 1
     fi
   }
   ```

   Keep the direct validation failure visible for non-PyYAML errors. A virtual
   environment is only a dependency fallback, not a way to bypass invalid skill
   metadata.

6. Update the repository README with installation instructions and the skill list. Include the exact destination path for installation.
7. Check the repository diff, commit atomically, and push.

## Repository Layout

Use this layout for skill collection repositories:

```text
README.md
skills/
  <skill-name>/
    SKILL.md
    agents/openai.yaml
```

Add optional skill-owned resources only inside that skill folder. Keep collection docs, migration notes, and installation instructions in the repository root.

## GitHub Push

Prefer `gh` for authentication checks and remote setup:

```bash
gh auth status
git remote add origin <github-url>
git status --short
git add README.md skills/<skill-name>
git commit -m "Add <skill-name> skill"
git push -u origin main
```

If the remote repository is empty, create a `main` branch locally before pushing. If the remote already has content, fetch and integrate it before committing.
