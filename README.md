# Earthly Skills

Agent skills for working with Earthly tools and platforms.

## Available Skills

| Skill | Description |
|-------|-------------|
| [lunar-cataloger](skills/lunar-cataloger/) | Create Lunar cataloger plugins (Bash scripts) that sync software catalog information from external systems |
| [lunar-collector](skills/lunar-collector/) | Create Lunar collector plugins (Bash scripts) that gather SDLC metadata |
| [lunar-config](skills/lunar-config/) | Edit `lunar-config.yml` — wire together components, domains, collectors, policies, catalogers, and initiatives |
| [lunar-policy](skills/lunar-policy/) | Create Lunar policy plugins (Python scripts) that enforce engineering standards |
| [lunar-sql](skills/lunar-sql/) | Query Lunar's SQL API for components, checks, policies, domains, and PRs |
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

- `SKILL.md` — Main instructions and quick-start guide (hand-authored in this repo)
- `references/` — Summarized documentation for the AI to consult as needed (generated)
- `docs/` — A full copy of the documentation for the skill (generated)

## Updating the Bundled Docs & References

Each skill's `docs/` and `references/` folders are **generated**, not hand-edited:

- `docs/` is synced from the Lunar product documentation (`earthly/lunar`).
- `references/` is synced from `earthly/lunar-lib`'s `ai-context/` directory.

The [`update-lunar-content.yml`](.github/workflows/update-lunar-content.yml) workflow runs `earthly +update-all` nightly (and on demand) to refresh them. **Any edit to `docs/` or `references/` will be overwritten on the next sync — change the upstream source instead.** The hand-authored, skill-owned content lives in each skill's `SKILL.md`.

## Quick Links

- [Lunar Documentation](https://docs-lunar.earthly.dev/)
- [lunar-lib Repository](https://github.com/earthly/lunar-lib) - Reference collectors and policies
- [Earthly Documentation](https://docs.earthly.dev/)
