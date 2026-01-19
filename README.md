# Lunar Skills

Agent skills for creating Earthly Lunar collectors and policies.

## Available Skills

| Skill | Description |
|-------|-------------|
| [lunar-collector](lunar-collector/) | Create collector plugins (Bash scripts) that gather SDLC metadata |
| [lunar-policy](lunar-policy/) | Create policy plugins (Python scripts) that enforce engineering standards |

## What is Lunar?

Earthly Lunar is a guardrails engine for your engineering stack. It automatically enforces your organization's engineering standards across all code repositories and CI/CD pipelines by delivering contextual feedback directly in pull requests.

**Collectors** gather data from repositories, CI pipelines, and external APIs, writing it to a Component JSON. **Policies** evaluate that data and produce pass/fail checks.

## Usage

These skills are designed to be used with AI agents that support the Codex skill format. Each skill contains:

- `SKILL.md` - Main instructions and quick-start guide
- `references/` - Detailed documentation for the AI to consult as needed

## Quick Links

- [Lunar Documentation](https://docs-lunar.earthly.dev/)
- [lunar-lib Repository](https://github.com/earthly/lunar-lib) - Reference collectors and policies
