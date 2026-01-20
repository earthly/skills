
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
    pattern: ^go build.*
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

### Common options

These options can be applied to any hook type:

#### `runs_on`

* Type: `array`
* Default: `[prs, default-branch]`

Specifies the contexts in which the collector should run. The available values are:

* `prs` - the collector will run on pull requests
* `default-branch` - the collector will run on the default branch

By default, collectors run in both contexts. To restrict a collector to only run on pull requests, use `runs_on: [prs]`. To restrict a collector to only run on the default branch, use `runs_on: [default-branch]`.

### Hook types

#### `ci-before-job`

* Form:
  ```yaml
  type: ci-before-job
  pattern: <regex-pattern>
  ```

The `ci-before-job` type triggers the collector before a CI job is run. The collector will run if the job name matches the specified regex pattern.

If no pattern is specified, the collector will run before every job.

#### `ci-after-job`

* Form:
  ```yaml
  type: ci-after-job
  pattern: <regex-pattern>
  ```

The `ci-after-job` type triggers the collector after a CI job is run. The collector will run if the job name matches the specified regex pattern.

If no pattern is specified, the collector will run after every job.

#### `ci-before-step`

* Form:
  ```yaml
  type: ci-before-step
  pattern: <regex-pattern>
  ```

The `ci-before-step` type triggers the collector before a CI step is run. The collector will run if the step name matches the specified regex pattern.

If no pattern is specified, the collector will run before every step.

#### `ci-after-step`

* Form:
  ```yaml
  type: ci-after-step
  pattern: <regex-pattern>
  ```

The `ci-after-step` type triggers the collector after a CI step is run. The collector will run if the step name matches the specified regex pattern.

If no pattern is specified, the collector will run after every step.

#### `ci-before-command`

* Form:
  ```yaml
  type: ci-before-command
  pattern: <regex-pattern>
  ```

The `ci-before-command` type triggers the collector before a command is run in the CI pipeline. The collector will run if the command line matches the specified regex pattern.

The command can be any process within the CI pipeline even if it is wrapped in scripts or called from other commands.

#### `ci-after-command`

* Form:
  ```yaml
  type: ci-after-command
  pattern: <regex-pattern>
  ```

The `ci-after-command` type triggers the collector after a command is run in the CI pipeline. The collector will run if the command line matches the specified regex pattern.

The command can be any process within the CI pipeline even if it is wrapped in scripts or called from other commands.

#### `code`

* Form:
  ```yaml
  type: code
  ```

The `code` type triggers the collector when the code of the component changes (i.e. there are new commits).

#### `cron`

* Form:
  ```yaml
  type: cron
  clone-code: <boolean>
  schedule: <cron-schedule>
  ```

The `cron` type triggers the collector on a cron schedule. The collector will run according to the specified cron schedule.

If the `clone-code` option is set to `true`, the collector will execute in the context of the code repository. This means that the collector will have access to a git clone of the code repository and to interact with.
