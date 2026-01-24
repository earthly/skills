## Collector Bash SDK

The Collector Bash SDK is a set of Lunar CLI subcommands that allow you to collect SDLC metadata from within a collector, or from external systems, such as your CI system directly.

### Collector environment

Earthly Lunar executes collectors in an environment set up with the following variables:

- `LUNAR_HUB_HOST`: The host of the Lunar Hub.
- `LUNAR_HUB_INSECURE`: Whether to skip SSL verification of the Lunar Hub.
- `LUNAR_BIN_DIR`: The directory where the Lunar CLI is installed.
- `LUNAR_COLLECTOR_NAME`: The name of the collector.
- `LUNAR_COLLECTOR_CI_PIPELINE`: The CI pipeline of the component that the collector is running for (if this is a CI collector).
- `LUNAR_COMPONENT_ID`: The ID of the component that the collector is running for in `github.com/.../...` format.
- `LUNAR_COMPONENT_DOMAIN`: The domain of the component.
- `LUNAR_COMPONENT_OWNER`: The owner of the component.
- `LUNAR_COMPONENT_HEAD_BRANCH`: The head branch of the PR (branch that contains the changes), if applicable.
- `LUNAR_COMPONENT_BASE_BRANCH`: The base branch of the PR (branch to merge the changes into), if applicable.
- `LUNAR_COMPONENT_PR`: The PR number of the component, if applicable.
- `LUNAR_COMPONENT_TAGS`: The tags of the component.
- `LUNAR_COMPONENT_GIT_SHA`: The Git SHA of the component that the collector is running for.
- `LUNAR_COMPONENT_META`: The metadata of the component as a JSON object.
- `LUNAR_SECRET_<name>`: Any secret set in the Lunar Hub for the collectors, via `HUB_COLLECTOR_SECRETS=<name>=<value>;...`.

#### CI collector environment

For `ci-{before,after}-job`, `ci-{before,after}-step` and `ci-{before,after}-command` hooks the following entries are also available:

- `LUNAR_CI`: The CI prodiver indentifier (github, buildkite, ...).
- `LUNAR_CI_PIPELINE_RUN_ID`: Unique identifier for the current pipeline run. Pipeline are the top-level units of execution in a CI system. Also known as "workflow" in some CIs.
- `LUNAR_CI_PIPELINE_RUN_ATTEMPT`: Pipeline run attempt (1-based).
- `LUNAR_CI_PIPELINE_DEFINITION_REF`: URL to the pipeline source code.
- `LUNAR_CI_PIPELINE_NAME`: Name of the pipeline, if available.
- `LUNAR_CI_JOB_ID`: Job id. Jobs are units of parallel execution within a pipeline. Also known as "stages" in some CIs.
- `LUNAR_CI_JOB_NAME`: Job name, if available.

For `ci-{before,after}-step` and `ci-{before,after}-command` hooks the following entries are also available:

- `LUNAR_CI_STEP_INDEX`: Step index (1-based). Steps are the sequential units of execution within a job. 
- `LUNAR_CI_STEP_NAME`: Step name, if available.
- `LUNAR_CI_STEP_ID`: Step ID, if available.
- `LUNAR_CI_STEP_USES`: Reference to the step definition, for reusable step definitions.
- `LUNAR_CI_STEP_RUN`: Step source code, for inline definitions.

For `ci-{before,after}-command` hooks the following entries are also available:

- `LUNAR_CI_COMMAND`: Command and arguments of the hooked command.
- `LUNAR_CI_COMMAND_PID`: Process ID of the hooked command.
- `LUNAR_CI_COMMAND_PPID`: Parent process PID of the hooked command.


### `lunar collect` CLI command

* Form:
  ```bash
  lunar collect [--component <component-name>] [--json] [--array-append] <json-path> <value>
  ```

The `lunar collect` command is used to collect SDLC metadata from within a collector. The command takes a JSON path and a value as arguments. The JSON path is used to specify the location in the JSON object where the value should be stored.

#### `--component <component-name>`

* Type: `string`
* Optional

The `--component` flag is used to specify the name of the component that the value should be associated with. If the flag is not provided, the component is inferred from the context in which the command is executed (environment variables set by the collector).

If the collect command is executed outside of a collector, the component name must be provided.

#### `--json`

The `--json` flag is used to specify that the value should be interpreted as a JSON object, JSON array, or JSON scalar (string, number, etc). If the flag is not provided, the value is interpreted as a raw string.

Example:

```bash
lunar collect --json '.foo.bar1' 'true'        # interprets as a JSON scalar
lunar collect '.foo.bar2' 'true'               # interprets as a raw string
lunar collect '.foo.bar3' '{"baz": "value 3"}' # interprets as a JSON object
lunar collect '.foo.bar4' '["value 4"]'        # interprets as a JSON array
```

Will result in:

```json
{
  "foo": {
    "bar1": true,
    "bar2": "true",
    "bar3": {"baz": "value 3"},
    "bar4": ["value 4"]
  }
}
```

#### `--array-append`

The `--array-append` flag is used to specify that the value should be appended to an array at the specified JSON path. If the path does not exist, a new array will be created. If the path exists and is not an array, the value will be replaced with a new array containing the existing value and the new value.

Since arrays are concatenated during the component JSON merge, using `--array-append` is equivalent to wrapping the value in a JSON array. The following two commands are equivalent:

```bash
lunar collect --array-append '.foo.bar' 'a value'
lunar collect --json '.foo.bar' '["a value"]'
```

Example:

```bash
lunar collect --json --array-append '.foo.bar' '{"baz": "value 1"}'
lunar collect --json --array-append '.foo.bar' '{"baz": "value 2"}'
```

Will result in:

```json
{
  "foo": {
    "bar": [
      {"baz": "value 1"},
      {"baz": "value 2"}
    ]
  }
}
```

#### `<json-path>`

* Type: `string`

The JSON path is used to specify the location in the JSON object where the value should be stored. The path is specified using dot notation, where each level of the object is separated by a dot. For example, `.foo.bar.baz` would specify the `baz` property of the `bar` object, which is a property of the `foo` object.

#### `<value>`

By default, the value is interpreted as a raw string. If the `--json` flag is provided, the value is interpreted as a JSON object, JSON array, or JSON scalar (string, number, etc).

If the value is `-`, the value is read from standard input. This is useful for piping the output of a command into the `lunar collect` command.
