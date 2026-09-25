> For the complete documentation index, see [llms.txt](https://docs-lunar.earthly.dev/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs-lunar.earthly.dev/configuration/lunar-config/uipanels.md).

# uiPanels

Configure SQL-backed tabs for Lunar dashboard extension points through the uiPanels section of lunar-config.yml.

* `lunar-config.yml -> uiPanels`
* Type: `object`
* Optional
* Form:

  ```yaml
  uiPanels:
    <extension-point-id>: <panel-file-path>
    <extension-point-id>: <panel-file-path>
    ...
  ```

UI panels add SQL-backed content to Lunar dashboard extension points. Lunar currently provides three: the **Release Notes**, **Compliance** and **Artifacts** tabs in the Release Ledger dashboard. Use them to display data recorded by your collectors or other data available to the bundled dashboards.

Each `uiPanels` entry maps a supported extension-point ID to a YAML [panel file](#panel-file) in the configuration repository. The file declares one or more tabs. Each tab runs a read-only query through Grafana's database connection and renders the result as a table or Markdown.

Lunar validates and stores the panel file with the manifest. Publishing or rolling back the configuration updates the panel at the same time.

Example uiPanels definition:

{% code title="lunar-config.yml" %}

```yaml
uiPanels:
  release-notes: uipanels/release-notes.yml
  release-evidence: uipanels/release-evidence.yml
  release-artifacts: uipanels/release-artifacts.yml
```

{% endcode %}

## Extension point

* `lunar-config.yml -> uiPanels.<extension-point-id>`
* Type: `string`
* Form: `<extension-point-id>: <panel-file-path>`

The key is the ID of an extension point, and the value is the path of its panel file relative to the configuration repository root. The supported IDs are as follows:

| ID                  | Where it appears                                           | Parameters                        |
| ------------------- | ---------------------------------------------------------- | --------------------------------- |
| `release-notes`     | The **Release Notes** tab of the Release Ledger dashboard. | `:component`, `:sha`, `:from_sha` |
| `release-evidence`  | The **Compliance** tab of the Release Ledger dashboard.    | `:component`, `:sha`              |
| `release-artifacts` | The **Artifacts** tab of the Release Ledger dashboard.     | `:component`, `:sha`              |

The dashboard passes the listed parameters to every tab's SQL. Extension-point IDs are validated by the Hub version handling the pull. Upgrade the Hub before adding an ID introduced by a newer release: an unsupported ID fails the entire configuration pull, including pulls of configuration-repository branches in CI, so it cannot be staged on a branch ahead of the Hub upgrade. Until the configuration defines a panel, the tab shows a note naming the key to add.

`:from_sha` is the baseline the Release Ledger's **From** control selects: the release the notes are measured against, so the natural range for a `release-notes` query is every release after `:from_sha` up to and including `:sha`. The control offers previous releases that recorded an approved deployment attempt, and is empty when none qualify — treat an empty `:from_sha` as "no baseline", covering every release up to `:sha`.

## Panel file

* Type: YAML file
* Form:

  ```yaml
  tabs:
    - <tab-object>
    - <tab-object>
    - ...
  ```

A panel file declares the tabs of one extension point. It must declare at least one, and a file with a single tab renders its content without a tab bar. The file may not exceed 64 KiB because Lunar stores it with the manifest and sends it to the browser on every panel view.

This minimal release-evidence panel shows the release commit and collection time in a table, then renders a note for the same commit as Markdown:

{% code title="uipanels/release-evidence.yml" %}

```yaml
tabs:
  - name: Commit
    type: table
    sql: |
      SELECT git_sha::text AS commit, timestamp
      FROM public.components
      WHERE component_id = :component
        AND git_sha = :sha
        AND pr IS NULL
      ORDER BY timestamp DESC
      LIMIT 1
    columns:
      - sqlId: commit
        name: Commit
        width: 120
      - sqlId: timestamp
        name: Collected at
  - name: Notes
    type: markdown
    sql: |
      SELECT 'Release `' || left(:sha, 7) || '`.' AS content
    sqlId: content
```

{% endcode %}

For complete replacements for the former built-in tabs, copy the ready-made panel files from [`hub/uipanel/examples/`](https://github.com/earthly/lunar/tree/main/hub/uipanel/examples). Adjust them to match the collectors you run.

## Tab

* `<panel-file> -> tabs.<tab-index>`
* Type: `object`
* Forms:
  * Table form:

    ```yaml
    name: <tab-title>
    type: table
    sql: <query>
    columns:
      - <column-object>
      - ...
    ```
  * Markdown form:

    ```yaml
    name: <tab-title>
    type: markdown
    sql: <query>
    sqlId: <sql-output-column>
    ```

Each tab defines one query and how Lunar renders its result. Tabs fail independently at view time: one tab can show an error while the others render.

### `name`

* `<panel-file> -> tabs.<tab-index>.name`
* Type: `string`
* Required

The tab's title. Names must be unique within the file.

### `type`

* `<panel-file> -> tabs.<tab-index>.type`
* Type: `string`
* Values: `table`, `markdown`
* Required

Controls how Lunar renders the query result. A `table` tab displays each returned row with the columns listed in `columns`. A `markdown` tab renders the `sqlId` column from the first row as Markdown.

### `sql`

* `<panel-file> -> tabs.<tab-index>.sql`
* Type: `string`
* Required

The read-only SQL query. Unqualified table names resolve in `public`, where Lunar exposes the documented [SQL API](/sql-api/sql-api.md) views. Qualify names in other schemas.

Refer to extension-point parameters as `:name`. Lunar substitutes each parameter as a quoted SQL string literal, so its value remains data. A `::type` cast is not a parameter.

A query that names an unsupported parameter fails the pull. Lunar warns when no tab uses an available parameter, since omitting `:component` shows the same rows for every component.

Lunar does not execute SQL during configuration validation. Syntax errors and unknown table names appear on the dashboard when the tab loads.

### `columns`

* `<panel-file> -> tabs.<tab-index>.columns`
* Type: `array`
* Required in Table form

The columns to show, in order, each naming a query output column. Output columns not listed are not displayed but can be used in `link` templates. See [Column](#column).

### `sqlId`

* `<panel-file> -> tabs.<tab-index>.sqlId`
* Type: `string`
* Required in Markdown form

The query output column holding the Markdown. Lunar renders headings, paragraphs, bullet lists, **bold**, *italics*, `code`, and links. It displays raw HTML as text. Links follow the same URL rules as a column's [`link`](#link). No rows means an empty tab.

## Column

* `<panel-file> -> tabs.<tab-index>.columns.<column-index>`
* Type: `object`
* Form:

  ```yaml
  sqlId: <sql-output-column>
  name: <header>
  width: <pixels>
  alignment: <left | center | right>
  color: <css-color>
  link: <url-template>
  ```

### `sqlId`

* `<panel-file> -> tabs.<tab-index>.columns.<column-index>.sqlId`
* Type: `string`
* Required

The query output column to show. It must be unique within the tab. A column the query does not return is reported on the tab.

### `name`

* `<panel-file> -> tabs.<tab-index>.columns.<column-index>.name`
* Type: `string`
* Optional

The header text. Defaults to `sqlId`.

### `width`

* `<panel-file> -> tabs.<tab-index>.columns.<column-index>.width`
* Type: `integer`
* Optional

The column width in pixels, applied exactly. Values that do not fit are cut with an ellipsis and shown in full on hover. Columns without a width share the remaining space and wrap, so leave the free-text column unsized.

### `alignment`

* `<panel-file> -> tabs.<tab-index>.columns.<column-index>.alignment`
* Type: `string`
* Values: `left`, `center`, `right`
* Optional

The text alignment of the column.

### `color`

* `<panel-file> -> tabs.<tab-index>.columns.<column-index>.color`
* Type: `string`
* Optional

A CSS color for the cell text: a `#hex` value, a color keyword, or an `rgb()` / `hsl()` function.

### `link`

* `<panel-file> -> tabs.<tab-index>.columns.<column-index>.link`
* Type: `string`
* Optional

A URL template that turns each cell into a link. Inside a larger template, `${col}` is replaced per row with that query column's percent-encoded value:

```yaml
link: https://tracker.example/browse/${ticket}
```

When the whole template is exactly `${col}`, that column supplies the complete URL. This can link one displayed column using a URL returned in another, undisplayed query column:

```yaml
columns:
  - sqlId: ref
    link: ${url}
```

The URL must start with `http://`, `https://`, or `/` for a path on the Grafana host (`/d/<uid>/...` links to another dashboard). Lunar rejects other schemes and protocol-relative `//host` URLs at render time; it also validates every link whose scheme is present in the template at pull time.

## What a tab can read

Tabs use Grafana's database connection and inherit the bundled dashboards' read access. This includes:

* the documented [SQL API](/sql-api/sql-api.md) views in `public`, including [`public.components`](/sql-api/views/components.md) and `public.checks`;
* views and helper functions in the `grafana` schema;
* the internal Hub schemas used by the bundled dashboards.

Lunar runs tab queries read-only.

{% hint style="warning" %}
**Publishing Lunar configuration can expose dashboard-readable data.** A panel can select any data available to the bundled dashboards and render it for dashboard viewers. Treat permission to publish configuration as permission to choose which of that data panels expose.
{% endhint %}

## Validation

Use [`lunar hub pull --dry-run`](/configuration/lunar-config/validation.md) to run the same panel-file checks without publishing the configuration. A validation error stops the pull, and the last published configuration stays active.

## Query limits

A table tab returns at most 200 rows and indicates when the result is truncated. This limit controls what reaches the browser, not the database work. Add an `ORDER BY` clause when row order matters.

A query that omits its `:component` filter can scan a whole table whenever someone views the panel. Self-hosted operators can limit query duration; see [Limit Grafana query time](/install/lunar-hub/self-hosted/day-2-operations.md#limit-grafana-query-time).


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation dynamically by asking a question.

Perform an HTTP GET request on the current page URL with the `ask` query parameter, and the optional `goal` query parameter:

```
GET https://docs-lunar.earthly.dev/configuration/lunar-config/uipanels.md?ask=<question>&goal=<endgoal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is optional and describes the broader end goal you are ultimately trying to accomplish on behalf of the user. GitBook uses it to tailor the answer towards what is most useful for that goal.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
