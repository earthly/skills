# Earthly Skills

Agent skills for working with Earthly tools and platforms.

## Available Skills

| Skill | Description |
|-------|-------------|
| [lunar-collector](skills/lunar-collector/) | Create Lunar collector plugins (Bash scripts) that gather SDLC metadata |
| [lunar-policy](skills/lunar-policy/) | Create Lunar policy plugins (Python scripts) that enforce engineering standards |
| [earthfile](skills/earthfile/) | Write Earthfiles for repeatable, containerized builds with Earthly |

## Installation

Copy the skill folders from `skills/` to your agent's skills directory:

```bash
git clone https://github.com/earthly/skills.git
cp -r skills/skills/* ~/.codex/skills/
```

Or if you have [Earthly](https://earthly.dev/earthfile) installed:

```bash
earthly github.com/earthly/skills+install-skills
```

## Usage

These skills are designed to be used with AI agents that support the Claude/Codex skill format. Each skill contains:

- `SKILL.md` - Main instructions and quick-start guide
- `references/` - Summarized documentation for the AI to consult as needed
- `docs/` - A full copy of the documentation for the skill

## Quick Links

- [Lunar Documentation](https://docs-lunar.earthly.dev/)
- [lunar-lib Repository](https://github.com/earthly/lunar-lib) - Reference collectors and policies
- [Earthly Documentation](https://docs.earthly.dev/)
