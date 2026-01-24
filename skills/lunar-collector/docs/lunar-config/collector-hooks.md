
## Collector Hooks

* `lunar-config.yml -> collectors.<collector-index>.hooks`
* `lunar-collector.yml -> collectors.<collector-index>.hooks`
* Type: `array`
* Form:
  ```yaml
  hooks:
    - <hook-configuration>
    - <hook-configuration>
    - ...
  ```

Hooks defines when a collector should run.

Example hooks definition:

```yaml
hooks:
  - type: ci-before-command
    binary:
      name: go
    args:
      - value: build
  - type: code
  - type: cron
    runs_on: [default-branch]
    schedule: "0 2 * * *"
```

## Collector Hook

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>`
* `lunar-collector.yml -> collectors.<collector-index>.hooks.<hook-index>`
* Type: `object`
* Form:
  ```yaml
  type: <hook-type>
  runs_on: <runs-on-array>
  <options>
  ```

A collector hook defines a trigger point for when a collector should run. Collectors can be triggered by various events such as code changes, CI pipeline events, or cron schedules.

Different hooks will cause the collector to execute in different contexts. For example, `ci-*` hooks will execute the collector in the context of the CI pipeline, while `code` and `cron` hooks will execute on a Lunar runner.

A hook has different configuration options depending on the type of event it is triggered by.

### `type`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.type`
* Type: `string`
* Required

The type of hook. The available values are:

* `ci-before-job` - triggers before a CI job
* `ci-after-job` - triggers after a CI job
* `ci-before-step` - triggers before a CI step
* `ci-after-step` - triggers after a CI step
* `ci-before-command` - triggers before a command is executed
* `ci-after-command` - triggers after a command is executed
* `code` - triggers when code changes
* `cron` - triggers on a schedule

### `runs_on`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.runs_on`
* Type: `array`
* Optional
* Default: `[prs, default-branch]`

Specifies the contexts in which the collector should run. The available values are:

* `prs` - the collector will run on pull requests
* `default-branch` - the collector will run on the default branch

By default, collectors run in both contexts. To restrict a collector to only run on pull requests, use `runs_on: [prs]`. To restrict a collector to only run on the default branch, use `runs_on: [default-branch]`.

## Hook Types

### `ci-before-job` / `ci-after-job`

* Form:
  ```yaml
  type: ci-before-job | ci-after-job
  pattern: <regex-pattern>
  ```

The `ci-before-job` type triggers the collector before a CI job is run. The `ci-after-job` type triggers the collector after a CI job is run. The collector will run if the job name matches the specified regex pattern.

If no pattern is specified, the collector will run before/after every job.

#### `pattern`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.pattern`
* Type: `string`
* Optional
* Default: `.*`

A regex pattern to match against the job name.

### `ci-before-step` / `ci-after-step`

* Form:
  ```yaml
  type: ci-before-step | ci-after-step
  pattern: <regex-pattern>
  ```

The `ci-before-step` type triggers the collector before a CI step is run. The `ci-after-step` type triggers the collector after a CI step is run. The collector will run if the step name matches the specified regex pattern.

If no pattern is specified, the collector will run before/after every step.

#### `pattern`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.pattern`
* Type: `string`
* Optional
* Default: `.*`

A regex pattern to match against the step name.

### `ci-before-command` / `ci-after-command`

* Forms:
  * Simple form:
    ```yaml
    type: ci-before-command | ci-after-command
    binary:
      name: <name-string>
    args:
      - flag: <flag-string>
        value: <value-string>
      - ...
    ```
  * Advanced form:
    ```yaml
    type: ci-before-command | ci-after-command
    binary:
      name[_pattern]: <name-string-or-pattern>
      dir[_pattern]: <dir-string-or-pattern>
      use_path_dirs: <boolean>
    args:
      - flag[_pattern]: <flag-string-or-pattern>
        value[_pattern]: <value-string-or-pattern>
      - ...
    args_pattern: <args-regex-pattern>
    envs:
      - name[_pattern]: <name-string-or-pattern>
        value[_pattern]: <value-string-or-pattern>
      - ...
    include_children_depth: <integer>
    max_process_depth: <integer>
    ```
  * Pattern form (deprecated):
    ```yaml
    type: ci-before-command | ci-after-command
    pattern: <regex-pattern>
    ```

The `ci-before-command` type triggers the collector before a command is run in the CI pipeline. The `ci-after-command` type triggers the collector after a command is run.

The command can be any process within the CI pipeline even if it is wrapped in scripts or called from other commands.

There are two forms for matching commands: the **Simple form** provides a straightforward way to match commands for common use cases, while the **Advanced form** provides additional options for fine-grained control. The Simple form is a subset of the Advanced form. The **Pattern form** is deprecated and may be removed in a future release.

For the hook to trigger, all specified matchers (`binary`, `args`, `envs`) must match. This is an AND operation. To implement OR logic (e.g., matching both `-f` and `--file` flags), use regex patterns with alternation (e.g., `flag_pattern: ^(-f|--file)$`).

#### Matching Limitations

The argument matching algorithm operates on raw argument strings and does not have semantic knowledge of the command being executed. Specifically:

* The `flag` + `value` construct matches consecutive arguments (e.g., `--file foo.txt`) or arguments joined with `=` (e.g., `--file=foo.txt`). It does not know whether a command's flag actually accepts a value.
* In ambiguous cases, incorrect matches may occur. For example, given `mycommand --file --verbose`, a matcher with `flag: --verbose` would match, even though `--verbose` might actually be the value of `--file` (if `--file` accepts any string as its value).
* Positional argument matchers match in order but cannot distinguish between a true positional argument and a flag's value. For example, `value: build` would match both `go build ./...` (where `build` is a subcommand) and `go run ./cmd/mycmd.go --type build` (where `build` is the value of `--type`).

For most common CLI tools and usage patterns, these limitations do not cause issues. However, be aware of edge cases when matching commands with unusual argument structures.

For advanced edge cases, use `args_pattern` instead of `args`.

#### `binary`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.binary`
* Type: `object`
* Optional

Specifies how to match the command's binary. All specified fields must match for the binary to be considered a match.

##### `name[_pattern]`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.binary.name[_pattern]`
* Type: `string`
* Optional

Specifies how to match the binary name. Use `name` for an exact match, or `name_pattern` for a regex pattern. The two fields are mutually exclusive.

##### `dir[_pattern]`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.binary.dir[_pattern]`
* Type: `string`
* Optional

Specifies how to match the binary's directory. Use `dir` for an exact match, or `dir_pattern` for a regex pattern. The two fields are mutually exclusive with each other and with `use_path_dirs`. If none of `dir`, `dir_pattern`, or `use_path_dirs` is provided, the hook matches any directory.

##### `use_path_dirs`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.binary.use_path_dirs`
* Type: `boolean`
* Optional

By default (if `dir`, `dir_pattern` or `use_path_dirs` are not provided), the hook matches any directory.

If this field is set to `true`, restricts matching to binaries located in directories that are present in the `PATH` environment variable. Mutually exclusive with `dir` and `dir_pattern`.

#### `args`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.args`
* Type: `array`
* Optional

An array of argument matchers. All specified matchers must match for the hook to trigger.

Each argument matcher can specify a flag and/or a value. The `flag` and `value` fields work together to match arguments in both space-separated form (`--foo bar`) and equals form (`--foo=bar`).

**Ordering rules:**
* Matchers with only `value` (or `value_pattern`) and no `flag` are positional arguments and must be defined in the order they appear in the command.
* Matchers with `flag` (or `flag_pattern`) can be defined in any order, regardless of where they appear in the actual command.

##### `flag[_pattern]`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.args.<arg-index>.flag[_pattern]`
* Type: `string`
* Optional

Specifies how to match the flag name. Use `flag` for an exact match (e.g., `-t`, `--tag`), or `flag_pattern` for a regex pattern (e.g., `^(-f|--file)$` to match both short and long forms). The two fields are mutually exclusive. Flag matchers can be defined in any order.

If neither `flag` nor `flag_pattern` is provided, the matcher is treated as a positional argument and only the value is matched. Positional matchers must be defined in the order they appear in the command.

**Note:** Only use `flag` for actual flags (arguments starting with `-` or `--`). For positional arguments like subcommands (e.g., `get` in `kubectl get pod`), use only `value` without `flag`.

For boolean flags (e.g., `--verbose`), provide only `flag` (or `flag_pattern`) without `value` or `value_pattern`. See the `value[_pattern]` documentation below for details on how boolean flags are matched.

##### `value[_pattern]`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.args.<arg-index>.value[_pattern]`
* Type: `string`
* Optional

Specifies how to match the argument value. Use `value` for an exact match, or `value_pattern` for a regex pattern. The two fields are mutually exclusive.

* If neither `value` nor `value_pattern` is provided, the matcher assumes this is a boolean flag (a flag that takes no value, such as `--verbose`). In this case, `--flag` matches, but `--flag=` and `--flag=anything` do not match. Note that `--flag anything` would match because `anything` is treated as a separate argument, not a value for `--flag`.
* If `value` is set to an empty string (`""`), matches arguments with an explicitly empty value (e.g., `--flag=`), but not boolean flags without a value (e.g., `--flag`).

#### `args_pattern`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.args_pattern`
* Type: `string`
* Optional

A regex pattern to match against all command arguments as a single space-concatenated string. This is an alternative to the `args` array for advanced matching scenarios where the structured `args` matchers are insufficient.

For example, if a command is invoked as `mycommand --flag value arg1 arg2`, the `args_pattern` would match against the string `--flag value arg1 arg2`.

The `args` array and `args_pattern` can be used together; both must match for the hook to trigger.

#### `envs`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.envs`
* Type: `array`
* Optional

An array of environment variable matchers. All specified matchers must match for the hook to trigger.

##### `name[_pattern]`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.envs.<env-index>.name[_pattern]`
* Type: `string`
* Optional

Specifies how to match the environment variable name. Use `name` for an exact match, or `name_pattern` for a regex pattern. The two fields are mutually exclusive.

##### `value[_pattern]`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.envs.<env-index>.value[_pattern]`
* Type: `string`
* Optional

Specifies how to match the environment variable value. Use `value` for an exact match, or `value_pattern` for a regex pattern. The two fields are mutually exclusive.

#### `max_process_depth`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.max_process_depth`
* Type: `integer`
* Optional
* Default: infinite

Defines the maximum depth of the process itself in the process tree for which the hook will trigger. For example, if set to `1`, the hook will only trigger on top-level processes in the CI/CD pipeline.

#### `include_children_depth`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.include_children_depth`
* Type: `integer`
* Optional
* Default: `0`

If set to a value greater than zero, the hook will also trigger on child processes of the matched command, up to the specified depth. By default (`0`), the hook only triggers on the matched command itself.

#### `pattern` (deprecated)

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.pattern`
* Type: `string`
* Required in Pattern form
* Deprecated

A regex pattern to match against the full command line. This form is deprecated; use the Simple or Advanced form instead.

#### Examples

Match `go build` commands:

```yaml
type: ci-before-command
binary:
  name: go
args:
  - value: build
```

Match `kubectl get pod` (positional arguments in order):

```yaml
type: ci-before-command
binary:
  name: kubectl
args:
  - value: get
  - value: pod
```

Match `docker build` with any tag:

```yaml
type: ci-before-command
binary:
  name: docker
args:
  - value: build
  - flag_pattern: ^(-t|--tag)$
    value_pattern: .*
```

Match `npm run`, `npm test`, or `npm build`:

```yaml
type: ci-before-command
binary:
  name: npm
args:
  - value_pattern: ^(run|test|build)$
```

Match `pytest` with verbose flag:

```yaml
type: ci-after-command
binary:
  name: pytest
args:
  - flag: --verbose
```

Match commands with either `-f` or `--file` flag:

```yaml
type: ci-before-command
binary:
  name: mycommand
args:
  - flag_pattern: ^(-f|--file)$
    value_pattern: .*\.txt$
```

Match any Python binary in a specific directory:

```yaml
type: ci-before-command
binary:
  name_pattern: python[0-9]*
  dir: /usr/local/bin
```

Match `go` commands resolved via PATH:

```yaml
type: ci-before-command
binary:
  name: go
  use_path_dirs: true
args:
  - value_pattern: ^(build|test|run)$
```

Match commands with specific environment variable:

```yaml
type: ci-before-command
binary:
  name: make
envs:
  - name: DEBUG
    value: "1"
```

Match using `args_pattern` for advanced argument matching:

```yaml
type: ci-before-command
binary:
  name: terraform
args_pattern: (plan|apply).*-var-file=.*production
```

Match top-level `make` commands and their immediate children:

```yaml
type: ci-before-command
binary:
  name: make
max_process_depth: 1
include_children_depth: 1
```

Match using pattern form (deprecated):

```yaml
type: ci-before-command
pattern: ^go build.*
```

### `code`

* Form:
  ```yaml
  type: code
  ```

The `code` type triggers the collector when the code of the component changes (i.e. there are new commits).

### `cron`

* Form:
  ```yaml
  type: cron
  clone-code: <boolean>
  schedule: <cron-schedule>
  ```

The `cron` type triggers the collector on a cron schedule. The collector will run according to the specified cron schedule.

#### `schedule`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.schedule`
* Type: `string`
* Required

A cron expression specifying when the collector should run (e.g., `"0 2 * * *"` for daily at 2am).

#### `clone-code`

* `lunar-config.yml -> collectors.<collector-index>.hooks.<hook-index>.clone-code`
* Type: `boolean`
* Optional
* Default: `false`

If set to `true`, the collector will execute in the context of the code repository. This means that the collector will have access to a git clone of the code repository to interact with.
