
## Cataloger Plugins

* `lunar-cataloger.yml`
* Type: YAML file
* Form:
  ```yaml
  version: 0

  name: <cataloger-name>
  description: <cataloger-description>
  author: <author-name>

  default_image: <default-image>

  catalogers:
    - <cataloger-object>
    - <cataloger-object>
    - ...

  inputs:
    <input-name>:
      description: <input-description>
      default: <input-default-value>
  ```

This page describes the configuration of a cataloger plugin. Cataloger plugins are used to synchronize software catalog information from external systems. Cataloger plugins can be imported from the Lunar configuration file, `lunar-config.yml` via the `uses` cataloger form.

Cataloger plugins can be defined either in a separate repository or in the same repository as the Lunar configuration, in a dedicated directory. Either way, the cataloger plugin must contain a `lunar-cataloger.yml` file in the root of the repository or directory. This file is used to configure the behavior of the cataloger plugin.

When using catalogers in the Main or Run forms, you can also install dependencies. See [installing dependencies in the Bash SDK](../bash-sdk/dependencies.md) for more details.

## `version`
* `lunar-cataloger.yml -> version`
* Type: `numeric`
* Required

The version field is used to specify the version of the cataloger configuration file. The current version is `0`.

## `name`

* `lunar-cataloger.yml -> name`
* Type: `string`
* Required

The name field is used to specify the name of the cataloger.

## `description`

* `lunar-cataloger.yml -> description`
* Type: `string`
* Optional

The description field is used to specify a description of the cataloger.

## `author`

* `lunar-cataloger.yml -> author`
* Type: `string`
* Required

The author field is used to specify the author of the cataloger.

## `default_image`

* `lunar-cataloger.yml -> default_image`
* Type: `string`
* Optional

The default Docker image to use for all catalogers in this plugin. This overrides the global `default_image_catalogers` setting from `lunar-config.yml`.

Individual catalogers can still override this plugin default using the `image` field. Use the special value `native` to explicitly run without a container.

For more information about default images and container execution, see [Images](../lunar-config/images.md).

## `catalogers`

* `lunar-cataloger.yml -> catalogers`
* Type: `array`
* Required

The catalogers field is used to specify the configuration of the cataloger. The format of a cataloger is the same as in `lunar-config.yml`. To learn more about the configuration of a cataloger, see the [catalogers](../lunar-config/catalogers.md) page.

**Note:** When consumers import this plugin via `uses`, they can selectively include or exclude specific catalogers using the [`include`](../lunar-config/catalogers.md#include) field. This allows consumers to use only the catalogers they need from a plugin that defines multiple catalogers.

## `inputs`

* `lunar-cataloger.yml -> inputs`
* Type: `object`
* Optional

The inputs field is used to specify the inputs required by the cataloger. Each input is defined as a key-value pair, where the key is the input name.

Inputs are passed to the cataloger when invoked as environment variables with the prefix `LUNAR_VAR_` and the input name in uppercase. For example, an input named `api_url` is accessible as `$LUNAR_VAR_API_URL`.

### `description`

* `lunar-cataloger.yml -> inputs.<input-name>.description`
* Type: `string`
* Optional

The description field is used to specify a description of the input.

### `default`

* `lunar-cataloger.yml -> inputs.<input-name>.default`
* Type: `string`
* Optional

The default field is used to specify the default value of the input. If no default value is specified, the input is required.
