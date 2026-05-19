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

Install with the [`skills`](https://github.com/vercel-labs/skills) CLI:

```bash
# Install all Earthly skills globally
npx skills add earthly/skills -g

# Or install a specific skill globally
npx skills add earthly/skills -g --skill lunar-policy
```

The CLI auto-detects which coding agents you have installed (Claude Code, Codex, Cursor, and 50+ more) and copies the skills to the right location. See the [`skills` CLI docs](https://github.com/vercel-labs/skills) for more commands like `list`, `update`, and `remove`.

Drop `-g` to install into the current project's `.claude/skills/` (or equivalent) instead — useful if you want to commit the skills into a shared team repo.

## Usage

These skills are designed to be used with AI agents that support the Claude/Codex skill format. Each skill contains:

- `SKILL.md` - Main instructions and quick-start guide

Lunar skills also contain:

- `references/` - Curated documentation for the AI to consult first
- Hosted docs backup - Use <https://docs-lunar.earthly.dev/llms.txt> only when `references/` is insufficient; for targeted answers, ask a specific question with `?ask=<question>` on a docs page URL

## Quick Links

- [Lunar Documentation](https://docs-lunar.earthly.dev/)
- [lunar-lib Repository](https://github.com/earthly/lunar-lib) - Reference collectors and policies
- [Earthly Documentation](https://docs.earthly.dev/)
