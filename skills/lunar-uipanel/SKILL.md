---
name: lunar-uipanel
description: Author Earthly Lunar uiPanels, the SQL-backed tabs that fill dashboard extension points such as the Release Ledger's Release Notes, Compliance and Artifacts tabs. Use when the user mentions uiPanels, UI panels, extension points, dashboard tabs, Release Ledger tabs, release evidence or artifacts panels, or wants a Grafana tab to show data from their collectors in Earthly Lunar.
---

# Lunar uiPanel Skill

Write `uiPanels` for Earthly Lunar: YAML panel files whose tabs run SQL over the SQL API views and render as a table or Markdown in a dashboard extension point. [references/uipanels.md](references/uipanels.md) is the docs page: extension points and their parameters, panel-file format, limits and link rules. The live copy is <https://docs-lunar.earthly.dev/configuration/lunar-config/uipanels.md>.

## Prerequisites

- `lunar` CLI 4.3.0 or later (`lunar version`), connected to the Hub: `lunar whoami` succeeds, after `lunar login` or with `LUNAR_HUB_HOST`/`LUNAR_HUB_TOKEN` set. Do not continue without it. Older CLI versions ignore `uiPanels:` and report the configuration valid.
- `psql`, for executing the tabs through `lunar sql connection-string`.
- A Hub that supports the extension-point ID. An unsupported ID fails the whole configuration pull. Until a panel is defined, the tab shows a note naming the `uiPanels.<id>` key to add, which confirms the Hub knows it.

Clone the configuration repository into a temporary directory (`mktemp -d`), work there, and delete it when done. The current directory is not necessarily that repository.

## Writing the Panel

1. Ask the user which extension point(s) to build, showing them the table in [references/uipanels.md](references/uipanels.md) (ID, where it appears, parameters). Do not pick for them.
2. Understand what the extension point is for, and ask the user what information they want rendered in it.
3. Look at the Component JSONs in the Hub, with `lunar component get-json <component-id> --git-sha <sha> --pretty` or through the SQL API (`psql "$(lunar sql connection-string)"`, `component_json` in `public.components`), and propose where to read each piece of information from: the path, and the components where you saw it. [references/component-json/structure.md](references/component-json/structure.md) describes what the lunar-lib collectors write.
4. Iterate with the user on the shape of the tab (`table` columns or a `markdown` note) and on the query that returns it, running the query against the SQL API as you go (see [Validation](#validation)). Write the panel file once they agree.

[examples/](examples/) holds a ready-made panel file per extension point, named after it. Start from the one for the point you are filling and keep its shape:

- Resolve the release with a CTE over `public.components` matching `:component` and `:sha` (exact, or a prefix of six or more characters), `pr IS NULL`, `ORDER BY timestamp DESC LIMIT 1`. Not `components_latest`: the release being viewed need not be the newest commit.
- `coalesce` the resolved JSON to `'{}'::jsonb`, so a tab still renders rows saying what is missing.
- Every tab references `:component` and `:sha`.
- Only `public.*` views, filtered by `:component`. Cells render as text, so use symbols (`✅`, `❌`, `—`), not icons.

Then wire the file into `lunar-config.yml`:

```yaml
uiPanels:
  <extension-point-id>: uipanels/<extension-point-id>.yml
```

## Validation

`lunar hub pull --dry-run <checkout>` runs the Hub's panel-file checks with no Hub connection: unknown ID or parameter, duplicate tab names, missing `columns`/`sqlId`, unsafe `link` templates, the 64 KiB cap. It does not execute the SQL, so syntax errors and unknown columns would only appear on the dashboard.

Then execute each tab the way the dashboard does: take the tab's `sql`, replace every `:name` parameter with its value as a quoted string literal (a `::type` cast is not a parameter), run it read-only through `lunar sql connection-string` for a component and SHA that have the data, and check that every declared `sqlId` is among the returned columns. For a `markdown` tab, the first row's `sqlId` value is what renders. A table shows at most 200 rows, so add `ORDER BY` when order matters. `psql -v component="'<id>'" -v sha="'<sha>'"` performs that substitution with the same rules.
