# Contributing to @open-finance/skills

Thank you for your interest in contributing! This guide covers how to create new skills and submit changes.

## Creating a New Skill

### 1. Start from the template

Copy the `template/` directory to create your skill:

```bash
cp -r template/ skills/my-skill-name/
```

### 2. Skill directory structure

Each skill lives under `skills/<skill-name>/` with this structure:

```
skills/my-skill-name/
  SKILL.md           # Required - Claude Code instructions (loaded into context)
  README.md          # Required - Human-readable documentation
  scripts/           # Optional - Automation scripts
    my_script.py
    requirements.txt # Required if scripts/ has Python files
  references/        # Optional - Reference materials for the skill
    guide.md
```

### 3. SKILL.md frontmatter

Every `SKILL.md` must begin with YAML frontmatter:

```yaml
---
name: my-skill-name          # Required - must match directory name
description: >                # Required - what the skill does and trigger phrases
  A description of this skill.
  Include phrases that should activate it.
---
```

**Required fields:**
- `name` - The skill identifier. Must match the directory name under `skills/`.
- `description` - A description of the skill's purpose. Include trigger phrases or keywords that should cause Claude to activate this skill.

After the frontmatter, write the full instructions that Claude should follow when this skill is active. Use clear headings, step-by-step workflows, and code examples.

### 4. README.md

The skill's `README.md` is for humans browsing the repository. Include:

- What the skill does
- Who it is for
- Key features
- Any dependencies (Python packages, system tools)
- Installation command

### 5. Scripts and dependencies

If your skill includes Python scripts:

- Place them in `scripts/`
- Add a `scripts/requirements.txt` listing all pip dependencies
- Scripts should be executable and include a shebang line

## Validating Your Skill

Before submitting, run the validation script:

```bash
npm run validate
```

This checks that all skills have valid `SKILL.md` frontmatter, required files, and proper structure.

## Pull Request Checklist

Before opening a PR, verify:

- [ ] `SKILL.md` has valid YAML frontmatter with `name` and `description`
- [ ] `README.md` is included with clear documentation
- [ ] Scripts have a `requirements.txt` if Python dependencies are needed
- [ ] `npm run validate` passes without errors
- [ ] Skill name uses lowercase kebab-case
- [ ] No sensitive data, API keys, or credentials are included

## Development Setup

```bash
git clone https://github.com/open-finance-ai/agent-skills.git
cd agent-skills
npm install
```

### Useful commands

```bash
npm run validate          # Validate all skills
npm run build             # Build distributable ZIPs
npm test                  # Run CLI tests
npm run lint              # Lint code
npm run format            # Format code with Prettier
```

## Code of Conduct

We are committed to providing a welcoming and respectful environment for everyone. Please be considerate and constructive in all interactions. Harassment, discrimination, and disrespectful behavior will not be tolerated.
