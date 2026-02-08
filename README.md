# @open-finance/skills

**Open-source Claude Code agent skills for financial analysis**

[![npm version](https://img.shields.io/npm/v/@open-finance/skills)](https://www.npmjs.com/package/@open-finance/skills)
[![license](https://img.shields.io/badge/license-Apache--2.0-blue)](./LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/open-finance-ai/agent-skills/ci.yml)](https://github.com/open-finance-ai/agent-skills/actions/workflows/ci.yml)

A curated collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) agent skills focused on financial analysis. Install skills to give Claude domain-specific knowledge and tools for working with financial data.

## Skill Catalog

| Name | Description | Category | Tags |
|------|-------------|----------|------|
| `bank-account-analysis` | Israeli bank account analysis with Hebrew PDF reports | Finance | `banking`, `israel`, `hebrew`, `pdf` |

## Quick Start

### Option 1: Run directly with npx

```bash
npx @open-finance/skills install bank-account-analysis
```

### Option 2: Install globally

```bash
npm install -g @open-finance/skills
openfinance-skills install bank-account-analysis
```

### Option 3: Clone and install manually

```bash
git clone https://github.com/open-finance-ai/agent-skills.git
cd agent-skills
npm install
```

Then copy the skill's `SKILL.md` into your project's `.claude/skills/` directory.

## CLI Usage

```bash
# List all available skills
openfinance-skills list

# Show detailed info about a skill
openfinance-skills info bank-account-analysis

# Install a skill into your Claude Code project
openfinance-skills install bank-account-analysis

# Update a previously installed skill
openfinance-skills update bank-account-analysis

# Remove a skill from your project
openfinance-skills uninstall bank-account-analysis
```

## How It Works

Each skill is a self-contained package that includes:

- **SKILL.md** - Instructions and knowledge that get loaded into Claude's context
- **README.md** - Human-readable documentation
- **scripts/** - Optional automation scripts (Python, shell, etc.)
- **references/** - Supporting reference materials

When you install a skill, the CLI copies the skill's `SKILL.md` file into your project's `.claude/skills/` directory, where Claude Code automatically picks it up.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on creating new skills and submitting pull requests.

## License

[Apache 2.0](./LICENSE)
