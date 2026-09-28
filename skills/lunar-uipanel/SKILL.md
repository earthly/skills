---
name: lunar-uipanel
description: Author Lunar uiPanels, the SQL-backed tabs that fill dashboard extension points such as the Release Ledger's Release Notes, Compliance and Artifacts tabs. Interviews the user, verifies Component JSON paths against the SQL API, writes and validates the panel file in a fresh clone of the config repo, and opens the pull request. Use when the user mentions uiPanels, UI panels, extension points, dashboard tabs, Release Ledger tabs, release evidence or artifacts panels, or wants a Grafana tab to show data from their collectors.
---

# Lunar uiPanel Skill

Write `uiPanels` for Earthly Lunar: YAML panel files whose tabs run SQL over the SQL API views and render as a table or Markdown inside a dashboard extension point. Two things are hard to get right from the docs alone. Which Component JSON paths exist depends on the collectors this deployment runs, and whether a query works is only known when someone opens the tab, because Lunar validates the file at pull time without executing the SQL. With a logged-in `lunar` CLI next to it, this skill can answer both before anything is pushed.

Work in a fresh clone under `/tmp` from step 3 on. Never edit the user's working copy.

## Quick Start

1. Read [references/uipanels.md](references/uipanels.md) for the panel-file format, parameters, limits and link rules.
2. Skim [references/component-json/structure.md](references/component-json/structure.md) for the paths collectors write.
3. Follow the six steps below. Validate with `lunar hub pull --dry-run` and `scripts/run-tab.py` before opening the PR.

## Step 0: Detect the Environment

```bash
test -f lunar-config.yml && echo "cwd is a config repo"
lunar sql connection-string >/dev/null && echo "live SQL API session"
command -v psql python3 && python3 -c 'import yaml' && echo "run-tab.py prerequisites present"
```

With a live session, steps 2 and 5 run against real data. Without one, rely on the user's paths and the Component JSON references, and say in the PR body which paths were not verified.

## Step 1: Interview

One topic at a time. Use a structured question tool when available.

**Which extension point(s).** Query the docs page for its extension-point table (ID, where it renders, parameters) and present it to the user:

```bash
curl -fsSL https://docs-lunar.earthly.dev/configuration/lunar-config/uipanels.md \
  | awk '/^\| ID +\| Where it appears +\| Parameters +\|/{p=1} p&&/^$/{exit} p'
```

Empty output means the page moved (the docs site answers with HTTP 200 and a "Page Not Found" body, so `curl` alone cannot tell); fall back to the table in [references/uipanels.md](references/uipanels.md).

Then require CLI 4.3.0 or newer, the first release with uiPanels. An older CLI drops the whole `uiPanels:` block unread and reports `Configuration is valid.`, so the dry runs in steps 5 and 6 would check no panel at all and the Hub's pull would be the first real validation:

```bash
v=$(lunar version | cut -d' ' -f1)
[ "$(printf '%s\n' 4.3.0 "$v" | sort -V | head -1)" = 4.3.0 ] && echo "lunar $v ok" || echo "lunar $v predates uiPanels; upgrade before continuing"
```

Stop until the user has upgraded. An extension point the docs page lists but the CLI rejects at dry run (`unknown extension point "<id>" (known ids: ...)`) means the CLI is behind that ID's release, so the same applies.

The CLI version says nothing about the Hub. The Hub validates IDs on the real pull, and an unsupported one fails the whole configuration, including CI pulls of config branches, so the Hub must be upgraded before such an ID is added. The Release Ledger tab itself confirms the Hub knows an ID: until the configuration defines its panel, the tab shows a note naming the `uiPanels.<id>` key to add.

**What to show per point.** Whether the point gets one tab or several, and for each tab whether it is a `table` (one row per signal, or one per artifact) or a `markdown` note, plus the signals or columns the user wants in it.

**Where the data lives.** The Component JSON path behind each signal (for example `.sbom.cicd.cyclonedx.components`) and which collector writes it. With a live session, offer to discover the paths instead of asking for them.

## Step 2: Discover and Verify Data

```sql
-- What the collectors write, and how widely
SELECT k, count(*) FROM components_latest, jsonb_object_keys(component_json) k
WHERE pr IS NULL GROUP BY k ORDER BY 2 DESC;

-- Coverage of one path
SELECT count(*) FILTER (WHERE jsonb_path_exists(component_json, '$.sbom.cicd')) AS with_path, count(*) AS total
FROM components_latest WHERE pr IS NULL;

-- A real release to test against
SELECT component_id, git_sha FROM components_latest
WHERE pr IS NULL AND jsonb_path_exists(component_json, '$.sbom.cicd') LIMIT 1;
```

Run them with `psql "$(lunar sql connection-string)" -X -At -c "..."`. To see the shape of one subtree:

```bash
lunar component get-json <component-id> --git-sha <sha> --pretty | jq .sbom
```

Confirm every user-supplied path the same way. Report a zero-coverage path together with the nearest existing key. Offline, mark unverified paths in the panel file's comments.

## Step 3: Clone the Config Repo and Branch

Default to `origin` of the cwd when it holds a `lunar-config.yml`; otherwise ask for the ref the user passes to `lunar hub pull` (`github://org/repo` or `gitlab://host/group/repo`).

```bash
CLONE=/tmp/lunar-config-uipanels-$(date +%s)
gh repo clone <org>/<repo> "$CLONE"   # or glab repo clone, or git clone <url> "$CLONE"
cd "$CLONE" && git switch -c uipanels/<extension-point-id>
```

## Step 4: Write the Panel File and Wire It

Write `uipanels/<extension-point-id>.yml` in the clone. Start from the closest example and follow its patterns:

| Example | Extension point | Shape |
|---|---|---|
| [examples/release-evidence.yml](examples/release-evidence.yml) | `release-evidence` | One `VALUES` row per signal with present/detail columns |
| [examples/release-artifacts.yml](examples/release-artifacts.yml) | `release-artifacts` | One row per element of a Component JSON array |
| [examples/release-notes.yml](examples/release-notes.yml) | `release-notes` | The releases since the previous approved deployment, a table tab and a Markdown tab |

Patterns the examples share:

- A `resolved` CTE picks the default-branch row for `:component` and `:sha`, accepting an exact match or a prefix of six or more characters, `ORDER BY timestamp DESC LIMIT 1`. Use `public.components`, not `components_latest`: the release being viewed need not be the newest commit.
- `coalesce((SELECT j FROM resolved), '{}'::jsonb)` so a signal table still has rows, each saying what is missing, when nothing was collected.
- `->>` with explicit casts; `coalesce(..., '[]'::jsonb)` before `jsonb_array_length` or `jsonb_array_elements`.
- Every tab references `:component` and `:sha`; a tab that omits one shows the same rows for every component or release.
- Only `public.*` views, so what `run-tab.py` checks with the SQL API role is what the dashboard runs.
- Fixed `width` on short columns, the free-text column unsized. `link`, `color` and `alignment` are optional.
- For `release-notes`, how far back the notes reach is the panel's decision. The example takes the newest release before `:sha` with an approved attempt under `.deployment.attempts` as the baseline, and covers everything up to `:sha` when there is none.

Then wire it into the clone's `lunar-config.yml` (or the `lunar-config.d/` fragment the repo uses):

```yaml
uiPanels:
  <extension-point-id>: uipanels/<extension-point-id>.yml
```

## Step 5: Validate in the Clone

```bash
lunar hub pull --dry-run "$CLONE"   # reads the working tree; the CLI accepts a local path
```

This runs the Hub's panel-file checks with no Hub connection: unknown ID, unknown parameter, duplicate tab names, missing `columns`/`sqlId`, unsafe `link` templates, the 64 KiB cap. It warns when no tab uses an available parameter. It needs `LUNAR_GITHUB_TOKEN`/`LUNAR_GITLAB_TOKEN` or a logged-in CLI to resolve private `uses:` plugins.

Then run each tab the way the dashboard does, against the `(component, sha)` from step 2:

```bash
python3 <skill-dir>/scripts/run-tab.py uipanels/<id>.yml --component <component-id> --sha <sha>
# any further parameter the docs page lists for the point:
python3 <skill-dir>/scripts/run-tab.py uipanels/<id>.yml --component <id> --sha <sha> --param <name>=<value>
```

`run-tab.py` substitutes each `:name` as a quoted literal, strips a trailing `;`, wraps the SQL as a read-only subquery, checks that every declared `sqlId` comes back, applies the 200-row cap and prints a row preview or the Markdown. It reads the connection string from `lunar sql connection-string` (`--conn <dsn>` overrides; admins can pass `--grafana` for the wider dashboard role) and exits non-zero on any failing tab. Fix and re-run until both commands are clean.

## Step 6: Commit, Push, Open the PR

After the user confirms:

```bash
git add -A && git commit -m "Add <extension-point-id> uiPanel"
git push -u origin uipanels/<extension-point-id>
gh pr create --fill   # or glab mr create
lunar hub pull --dry-run github://<org>/<repo>@uipanels/<extension-point-id>   # the form the config repo's CI runs
```

The PR body lists the extension point(s), the tabs, each Component JSON path with its coverage count from step 2, and the validation commands run. Report the clone path and leave it in place.

## Gotchas

- `::text` is a cast; `:name` is a parameter. A tab naming a parameter the extension point lacks fails the pull; a parameter no tab uses only warns.
- Syntax errors and unknown table names surface on the dashboard, not at pull time. Nothing but `run-tab.py` executes the SQL before publishing.
- A table tab returns at most 200 rows and flags truncation; add `ORDER BY` when order matters. A panel file may not exceed 64 KiB.
- `:sha` may be a prefix. Match with `git_sha::text = :sha OR (length(:sha) >= 6 AND git_sha::text LIKE :sha || '%')`.
- `link` URLs must start with `http://`, `https://` or `/`. `${col}` alone takes the whole URL from another, possibly undisplayed, column.
- Cell values render as text; use symbols (`✅`, `❌`, `—`) rather than icons.
- Publishing a panel exposes whatever the dashboard connection can read to everyone who can view the dashboard. Stay on `public.*` and filter by `:component`.

## Reference Documentation

- [references/uipanels.md](references/uipanels.md): the `uiPanels` docs page (extension points, panel-file format, limits, security note), refreshed nightly
- [references/component-json/structure.md](references/component-json/structure.md) and [conventions.md](references/component-json/conventions.md): Component JSON paths and conventions
- [examples/](examples/): ready-made panel files for the three Release Ledger extension points

## Hosted Documentation Backup

Only if the references do not answer the question, fetch:

- <https://docs-lunar.earthly.dev/configuration/lunar-config/uipanels.md>: the live page
- <https://docs-lunar.earthly.dev/configuration/lunar-config/validation.md>: `lunar hub pull --dry-run`
- <https://docs-lunar.earthly.dev/sql-api/views/components.md>: the `components` / `components_latest` columns
- <https://docs-lunar.earthly.dev/llms.txt>: index of every page

If a page still lacks enough context, ask the docs a specific, self-contained question with `?ask=<question>` on that page URL:

```text
GET https://docs-lunar.earthly.dev/configuration/lunar-config/uipanels.md?ask=Which%20parameters%20does%20release-notes%20receive%3F
```
