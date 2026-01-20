## Cataloger Bash SDK

The Cataloger Bash SDK is a set of Lunar CLI subcommands that allow you to save catalog-related information from within a cataloger.

### Cataloger environment

Earthly Lunar executes catalogers in an environment set up with the following variables:

- `LUNAR_HUB_HOST`: The host of the Lunar Hub.
- `LUNAR_HUB_INSECURE`: Whether to skip SSL verification of the Lunar Hub.
- `LUNAR_BIN_DIR`: The directory where the Lunar CLI is installed.
- `LUNAR_CATALOGER_NAME`: The name of the cataloger.
- `LUNAR_CATALOGER_OWNER`: The owner of the cataloger.
- `LUNAR_SECRET_<name>`: Any secret set in the Lunar Hub for the cataloger, via `HUB_CATALOGER_SECRETS=<name>=<value>;...`.

### `lunar catalog` CLI command

* Forms:
  * Raw form:
    ```bash
    lunar catalog raw [--json] <json-path> <value>
    ```
  * Component form:
    ```bash
    lunar catalog component [--name <n>] [--owner <owner>] [--branch <branch>] [--domain <domain>] [--tag <tag>] [--ci-pipeline <ci-pipeline>] [--meta <key>=<value>] [--meta-json <key>=<value>] [<json-value>]
    ```
  * Domain form:
    ```bash
    lunar catalog domain [--name <n>] [--description <description>] [--owner <owner>] [--meta <key>=<value>] [--meta-json <key>=<value>] [<json-value>]
    ```

The `lunar catalog` command is used to save catalog-related information from within a cataloger. The command takes a JSON path and a value as arguments. The JSON path is used to specify the location in the JSON object where the value should be stored.

#### `--json`

The `--json` flag is used to specify that the value should be interpreted as a JSON object, JSON array, or JSON scalar (string, number, etc). If the flag is not provided, the value is interpreted as a raw string.

#### `<json-path>`

* Type: `string`

The JSON path is used to specify the location in the JSON object where the value should be stored. The path is specified using dot notation, where each level of the object is separated by a dot. For example, `.foo.bar.baz` would specify the `baz` property of the `bar` object, which is a property of the `foo` object.

#### `<value>`

By default, the value is interpreted as a raw string. If the `--json` flag is provided, the value is interpreted as a JSON object, JSON array, or JSON scalar (string, number, etc).

If the value is `-`, the value is read from standard input. This is useful for piping the output of a command into the `lunar catalog` command.

### `--name <name>`

* Type: `string`
* Optional

The `--name` flag is used to specify the name of the component or domain.

When using the `component-repo` cataloger hook, the name of the component and the domain will be inferred automatically from the cataloger context in which the command is executed.

In Component and Domain forms, the name must be provided either via this flag, via the cataloger context (`component-repo` hook only), or via the JSON value.

### `--owner <owner>`

* Type: `string`
* Optional

The `--owner` flag is used to specify the owner of the component or domain.

### `--branch <branch>`

* Type: `string`
* Optional

The `--branch` flag is used to specify the branch of the component.

### `--domain <domain>`

* Type: `string`
* Optional

The `--domain` flag is used to specify the domain of the component. The domain must be specified in the format `foo.bar`, where `foo` is the parent domain and `bar` is the child domain.

### `--tag <tag>`

* Type: `string`
* Optional

The `--tag` flag is used to specify the tag of the component. This flag may be specified multiple times to add multiple tags to the component.

### `--ci-pipeline <ci-pipeline>`

* Type: `string`
* Optional

The `--ci-pipeline` flag is used to specify the CI pipeline of the component. This flag may be specified multiple times to add multiple CI pipelines to the component.

### `--meta <key>=<value>`

* Type: `string`
* Optional

The `--meta` flag is used to specify a metadata key-value pair for the component or domain. This flag may be specified multiple times to add multiple metadata entries. The value is interpreted as a raw string.

### `--meta-json <key>=<value>`

* Type: `string`
* Optional

The `--meta-json` flag is used to specify a metadata key-value pair for the component or domain where the value is interpreted as JSON. This flag may be specified multiple times to add multiple metadata entries. The value must be valid JSON (object, array, or scalar).

### `--description <description>`

* Type: `string`
* Optional

The `--description` flag is used to specify the description of the domain.

### `<json-value>`

* Type: `JSON string`
* Optional

The JSON value is used to specify the value to be stored in the JSON object.
