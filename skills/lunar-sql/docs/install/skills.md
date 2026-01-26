# Installing AI Skills

The [earthly/skills](https://github.com/earthly/skills) repository provides AI agent skills for building Lunar collectors and policies. These skills enable AI assistants to help you create custom plugins using the Bash and Python SDKs.

## Available Skills

| Skill | Description |
|-------|-------------|
| [lunar-collector](https://github.com/earthly/skills/tree/main/skills/lunar-collector) | Create Lunar collector plugins (Bash scripts) that gather SDLC metadata |
| [lunar-policy](https://github.com/earthly/skills/tree/main/skills/lunar-policy) | Create Lunar policy plugins (Python scripts) that enforce engineering standards |

## Installation

### Option 1: Manual Installation

Clone the repository and copy the skill folders to your agent's skills directory:

```bash
git clone https://github.com/earthly/skills.git
cp -r skills/skills/lunar-{collector,policy} ~/.codex/skills/
```

### Option 2: Using Earthly

If you have [Earthly](https://github.com/earthly/earthly) installed:

```bash
earthly github.com/earthly/skills+install-skills
```

## Usage

These skills are designed to be used with AI agents that support the Claude/Codex skill format. Each skill contains:

- `SKILL.md` - Main instructions and quick-start guide
- `references/` - Summarized documentation for the AI to consult as needed
- `docs/` - A full copy of the documentation for the skill

Once installed, your AI assistant will automatically detect and use these skills when you ask it to create Lunar collectors or policies.

## Related Resources

- [Bash SDK](../bash-sdk/bash-sdk.md) - Manual reference for building collectors
- [Python SDK](../python-sdk/python-sdk.md) - Manual reference for building policies
- [lunar-lib Repository](https://github.com/earthly/lunar-lib) - Reference collectors and policies
