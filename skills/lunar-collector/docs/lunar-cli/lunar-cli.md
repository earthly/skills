# Lunar CLI Reference

This document provides a comprehensive reference for all available options and commands in the Lunar CLI.

## Global options

#### `--config-dir <config-dir>`, `LUNAR_CONFIG_DIR=<config-dir>`

* Type: `string`
* Optional
* Default: `.`

The path to the directory containing the Lunar configuration files.

#### `--hub-host <hostname>`, `LUNAR_HUB_HOST=<hostname>`

* Type: `string`
* Optional

Override the URL of the Lunar Hub host name. This setting is inferred from the Lunar config if not specified.

#### `--hub-grpc-port <port>`, `LUNAR_HUB_GRPC_PORT=<port>`

* Type: `integer`
* Optional

Override the GRPC port of the Lunar Hub. This setting is inferred from the Lunar config if not specified.

#### `--hub-http-port <port>`, `LUNAR_HUB_HTTP_PORT=<port>`

* Type: `integer`
* Optional

Override the HTTP port of the Lunar Hub. This setting is inferred from the Lunar config if not specified.

#### `--hub-insecure`, `LUNAR_HUB_INSECURE=true`

* Type: `boolean`
* Optional

If true, use insecure HTTP connections to the Hub server.

#### `--no-hub`, `LUNAR_NO_HUB=true`

* Type: `boolean`
* Optional

Skip Hub interactions for dev commands (`lunar collector dev` and `lunar policy dev`). When enabled, the commands will run without connecting to Lunar Hub. Note that `--component-json` is required for `lunar policy dev` when this option is enabled, and `LUNAR_GITHUB_TOKEN` must be set if GitHub access is needed.

#### `LUNAR_HUB_TOKEN`

* Type: `string`
* Required for commands that interact with the Hub server

The Lunar Hub token to use for authentication.

## Config Commands

### `lunar hub pull`

* Form:
  ```bash
  lunar hub pull [--rerun-code-collectors|-r] [--include-pr-commits] [--pr-max-age-days <days>] <repo>
  ```

The `lunar hub pull` command is used to instruct Lunar Hub to pull the latest configuration from a given repository.

#### `<repo>`

* Type: `string`
* Form: `github://<owner>/<repo>@<branch-or-sha>`
* Required

The repository to pull configuration from. This should be the main repository containing your lunar configuration files.

**Examples:**

* `github://acme-corp/lunar@main`
* `github://acme-corp/lunar@de4adbeef`

#### `--rerun-code-collectors` | `-r`

* Type: `boolean`
* Optional

Rerun affected code collectors after applying the configuration.

#### `--include-pr-commits`

* Type: `boolean`
* Optional

Include PR commits when rerunning code collectors.

#### `--pr-max-age-days <days>`

* Type: `integer`
* Optional
* Default: `5`

Ignore PR commits older than this maximum number of days.

## Domain Commands

### `lunar domain ls`

* Form:
  ```bash
  lunar domain ls
  ```

The `lunar domain ls` command is used to list all domains.

## Component Commands

### `lunar component ls`

* Form:
  ```bash
  lunar component ls
  ```

The `lunar component ls` command is used to list all components.

### `lunar component get-json`

* Form:
  ```bash
  lunar component get-json [--git-sha <git-sha>] [--pr <pr-number>] <component-name>
  ```

The `lunar component get-json` command is used to retrieve the component JSON for a specified component.

#### `<component-name>`

* Type: `string`

The name of the component to retrieve the JSON for.

#### `--git-sha <git-sha>`

* Type: `string`
* Optional

The specific git SHA to retrieve the component JSON for. If not specified, the latest component JSON will be retrieved.

#### `--pr <pr-number>`

* Type: `integer`
* Optional

The PR number to retrieve the component JSON for. If not specified, and no git SHA is provided, the component JSON for the primary branch will be retrieved. This is ignored if `--git-sha` is specified.

Example:
```bash
lunar component get-json github.com/my-org/my-repo
```

## Cataloger Commands

### `lunar cataloger get-json`

* Form:
  ```bash
  lunar cataloger get-json [--pr <pr-number>] [--git-sha <git-sha>]
  ```

The `lunar cataloger get-json` command is used to retrieve the catalog JSON.

#### `--pr <pr-number>`

* Type: `integer`
* Optional

The PR number to retrieve the catalog JSON for. If not specified, and no git SHA is provided, the catalog JSON for the primary branch will be retrieved. This is ignored if `--git-sha` is specified.

#### `--git-sha <git-sha>`

* Type: `string`
* Optional

The specific git SHA to retrieve the catalog JSON for. If not specified, the latest catalog JSON will be retrieved.

### `lunar cataloger run`

* Form:
  ```bash
  lunar cataloger run [--output-json]
  ```

The `lunar cataloger run` command is used to run the catalogers and apply changes to the catalog. This command triggers execution in the cloud via Lunar Hub.

#### `--output-json`

Output the resulting catalog JSON.

### `lunar cataloger dev`

* Form:
  ```bash
  lunar cataloger dev
  ```

{% hint style='warn' %}
##### Warning

Please note that catalogers can be highly environment-dependent. Please be mindful of "works on my machine" types of issues.
{% endhint %}

The `lunar cataloger dev` command is used to run the catalogers in development mode without applying changes to the catalog. This command executes locally on the user's machine and outputs the resulting catalog JSON.

## Collector Commands

### `lunar collector run`

* Form:
  ```bash
  lunar collector run [--output-json] [--pr <pr-number>] \
    [--git-sha <git-sha>] [--only-code] [--only-cron] \
    [--collector <collector-name>] [--pr-max-age-days <days>] <component-name>
  ```

The `lunar collector run` command is used to rerun code and cron collectors for a given component. This command triggers execution in the cloud via Lunar Hub.

#### `<component-name>`

* Type: `string`

The name of the component to rerun collectors for.

#### `--pr <pr-number>`

* Type: `integer`
* Optional

The PR number to rerun collectors for. If not specified, collectors will be run for the component's primary branch.

#### `--git-sha <git-sha>`

* Type: `string`
* Optional

The specific git SHA to rerun collectors for. If specified, this takes precedence over `--pr`.

#### `--only-code`

Run only code collectors.

#### `--only-cron`

Run only cron collectors.

#### `--collector <collector-name>`

* Type: `string`
* Optional
* Repeatable

Run only the specified collector. This flag can be repeated to run multiple specific collectors.

#### `--pr-max-age-days <days>`

* Type: `integer`
* Optional
* Default: `5`

Ignore PR commits older than this maximum number of days.

#### `--output-json`

Output the results in JSON format.

Example:
```bash
# Rerun all collectors for all components for all PRs, limitting to 1 day old PRs
lunar collector run --pr-max-age-days 1
# Rerun collectors for a component (primary branch)
lunar collector run github.com/my-org/my-repo
# Rerun collectors for a specific PR
lunar collector run --pr 123 github.com/my-org/my-repo
# Rerun collectors for a specific git SHA
lunar collector run --git-sha abc123 github.com/my-org/my-repo
# Run only code collectors
lunar collector run --only-code github.com/my-org/my-repo
# Run only a specific collector
lunar collector run --collector collector-name github.com/my-org/my-repo
```

### `lunar collector dev`

* Name Form:
  ```bash
  lunar collector dev [--pr <pr-number>] [--git-sha <git-sha>] \
    [--component <component-name> | --component-dir <path>] \
    [--fake-ci-cmd <bash-command>] \
    <collector-name>
  ```
* Script Form:
  ```bash
  lunar collector dev \
    [--pr <pr-number>] [--git-sha <git-sha>] \
    [--component <component-name> | --component-dir <path>] \
    [--fake-ci-cmd <bash-command>] \
    --script <path-to-collector-script>
  ```

{% hint style='warn' %}
##### Warning

Please note that collectors can be highly environment-dependent. Please be mindful of "works on my machine" types of issues.
{% endhint %}

The `lunar collector dev` command is used to run a collector for a given component in development mode without applying changes. This command executes locally on the user's machine and outputs the resulting component JSON.

#### `<collector-name>`

* Type: `string`
* Required in Name Form

#### `--script <path-to-collector-script>`

* Type: `string`
* Required in Script Form

#### `--component <component-name>`

* Type: `string`

The name of the component to run collectors for. Mutually exclusive with `--component-dir`.

#### `--component-dir <path>`

* Type: `string`

Local directory containing the component to run collectors for. The directory must be a git repository. The component name is derived from the git remote URL. Mutually exclusive with `--component`.

#### `--pr <pr-number>`

* Type: `integer`
* Optional

The PR number to run collectors for. If not specified, collectors will be run for the component's primary branch.

#### `--git-sha <git-sha>`

* Type: `string`
* Optional

The specific git SHA to run collectors for. If specified, this takes precedence over `--pr`.

#### `<collector-name>`

* Type: `string`
* Optional

The name of the collector to run. If not specified, all collectors will be run.

The path to a bash collector script file to run in development mode.

#### `--fake-ci-cmd <bash-command>`

* Type: `string`
* Optional

A command that the CI would have executed, that would cause lunar instrumentation to trigger an event for. This command is not actually executed, it is merely used to test collector triggering logic (e.g. would the collector trigger regex match the command line). This option is used for testing CI collectors locally without requiring an actual CI pipeline execution.

#### Examples

```bash
# Run collectors in development mode for a component (primary branch)
lunar collector dev --component github.com/my-org/my-repo
# Run collectors in development mode for a specific PR
lunar collector dev --component github.com/my-org/my-repo --pr 123
# Run a specific collector
lunar collector dev --component github.com/my-org/my-repo collector-name
# Run a specific collector script file
lunar collector dev --component github.com/my-org/my-repo --script ./path/to/collector.sh
# Test a CI collector with a fake CI command
lunar collector dev --component github.com/my-org/my-repo --fake-ci-cmd "npm test" ci-collector-name
# Run collectors against a local directory
lunar collector dev --component-dir ./my-local-repo collector-name
# Run collectors against a local directory with a specific git SHA
lunar collector dev --component-dir ./my-local-repo --git-sha abc123 collector-name
```

## Policy Commands

### `lunar policy ls`

* Form:
  ```bash
  lunar policy ls
  ```

The `lunar policy ls` command is used to list all policies.

### `lunar policy check ls`

* Form:
  ```bash
  lunar policy check ls
  ```

The `lunar policy check ls` command is used to list all checks.

### `lunar policy run`

* Form:
  ```bash
  lunar policy run [--output-json] [--pr <pr-number>] \
    [--git-sha <git-sha>] [--policy <policy-name>] \
    [--initiative <initiative-name>] <component-name>
  ```

The `lunar policy run` command is used to rerun all policies for a given component. This command triggers execution in the cloud via Lunar Hub.

#### `<component-name>`

* Type: `string`
The name of the component to rerun policies for.

#### `--pr <pr-number>`

* Type: `integer`
* Optional

The PR number to rerun policies for. If not specified, policies will be run for the component's primary branch.

#### `--git-sha <git-sha>`

* Type: `string`
* Optional

The specific git SHA to rerun policies for. If specified, this takes precedence over `--pr`.

#### `--policy <policy-name>`

* Type: `string`
* Optional
* Repeatable

Run only the specified policy. This flag can be repeated to run multiple specific policies.

#### `--initiative <initiative-name>`

* Type: `string`
* Optional
* Repeatable

Run only policies under the specified initiative. This flag can be repeated to run policies under multiple initiatives.

#### `--output-json`

Output the results in JSON format.

Example:
```bash
# Rerun policies for a component (primary branch)
lunar policy run github.com/my-org/my-repo
# Rerun policies for a specific PR
lunar policy run --pr 123 github.com/my-org/my-repo
# Rerun policies for a specific git SHA
lunar policy run --git-sha abc123 github.com/my-org/my-repo
# Run only a specific policy
lunar policy run --policy policy-name github.com/my-org/my-repo
# Run policies under a specific initiative
lunar policy run --initiative initiative-name github.com/my-org/my-repo
```

### `lunar policy dev`

* Name Form:
  ```bash
  lunar policy dev [--component <component-name>] [--component-json <path-to-json-or-stdin>] \
    [--pr <pr-number>] [--git-sha <git-sha>] \
    <policy-name>
  ```
* Script Form:
  ```bash
  lunar policy dev [--component <component-name>] [--component-json <path-to-json-or-stdin>] \
    [--pr <pr-number>] [--git-sha <git-sha>] \
    --script <path-to-policy-script>
  ```
{% hint style='warn' %}
##### Warning

Please note that policies can be highly environment-dependent. Please be mindful of "works on my machine" types of issues.
{% endhint %}

The `lunar policy dev` command is used to run a policy against a component for local testing purposes. This command executes locally on the user's machine and outputs the check results in JSON format.

#### `<policy-name>`

* Type: `string`
* Required in Name Form

#### `--script <path-to-policy-script>`

* Type: `string`
* Required in Script Form

#### `--component <component-name>`

* Type: `string`

The name of the component to run the policy against.

#### `--component-json <path-to-json-or-stdin>`

* Type: `string`

The path to the component JSON file or `-` to read from stdin.

#### `--pr <pr-number>`

* Type: `integer`
* Optional

The PR number to run the policy against. If not specified, the policy will be run against the component's primary branch.

#### `--git-sha <git-sha>`

* Type: `string`
* Optional

The specific git SHA to run the policy against. If specified, this takes precedence over `--pr`.

####Example

```bash
# Run policy with component JSON from file
lunar policy dev --component-json path/to/component.json --script ./path/to/policy.py
# Run policy by specifying component directly
lunar policy dev --component github.com/my-org/my-repo --script ./path/to/policy.py
# Run policy with component JSON from stdin
lunar component get-json --git-sha ... github.com/my-org/my-repo | \
  lunar policy dev --component-json - --script ./path/to/policy.py
# Run specific policy from config
lunar policy dev --component github.com/my-org/my-repo my-policy
# Run policy for a specific PR
lunar policy dev --component github.com/my-org/my-repo --pr 123 --script ./path/to/policy.py
```

### `lunar policy ok-release`

* Form:
  ```bash
  lunar policy ok-release <component> <git_sha>
  ```

The `lunar policy ok-release` command is used to check if a component at a specific git SHA passes its release policies.

#### `<component>`

* Type: `string`

The name of the component to check.

#### `<git_sha>`

* Type: `string`

The git SHA to check.

### `lunar policy ok-pr`

* Form:
  ```bash
  lunar policy ok-pr <component> <git_sha>
  ```

The `lunar policy ok-pr` command is used to check if a component at a specific git SHA passes its PR policies.

#### `<component>`

* Type: `string`

The name of the component to check.

#### `<git_sha>`

* Type: `string`

The git SHA to check.

## SDK Commands

### `lunar catalog`

Saves catalog-related information from within a cataloger.

For detailed documentation on the `lunar catalog` command and all its options, see the [Cataloger Bash SDK](../bash-sdk/cataloger.md) page.

### `lunar collect`

Collects SDLC metadata from within a collector or external systems.

For detailed documentation on the `lunar collect` command and all its options, see the [Collector Bash SDK](../bash-sdk/collector.md) page.

## SQL Commands

### `lunar sql connection-string`

* Form:
  ```bash
  lunar sql connection-string
  ```

The `lunar sql connection-string` command returns the PostgreSQL connection string that can be used with any PostgreSQL client. The access is **read-only** and restricted to only the views described in the [SQL API](../sql-api/sql-api.md) documentation.

Example:
```bash
# Get the connection string
lunar sql connection-string
# Connect using psql (interactive)
psql $(lunar sql connection-string)
# Export checks data as CSV
psql $(lunar sql connection-string) -c "COPY (
  SELECT *
  FROM checks
  WHERE component_id = 'github.com/my-org/my-repo'
    AND status = 'fail'
) TO STDOUT WITH CSV HEADER" > failed_checks.csv
# Export component data as JSON
psql $(lunar sql connection-string) -c "
  SELECT json_agg(row_to_json(c))
  FROM (
    SELECT *
    FROM components
    WHERE tags @> '{\"team\":\"ui\"}'
  ) c" > platform_components.json
# Make decisions based on check results
psql $(lunar sql connection-string) -t -c "
  SELECT COUNT(*)
  FROM checks c
  JOIN components comp ON c.component_id = comp.component_id
  WHERE comp.domain = 'payments'
    AND c.status = 'fail'
    AND c.enforcement IN ('block-pr-and-release', 'block-release')" | \
  grep -q "^0$" || \
  (echo "Release blocking checks are failing in payments domain!" && exit 1)
```

For more examples of the SQL API in action, see the [SQL API](../sql-api/sql-api.md) documentation.
