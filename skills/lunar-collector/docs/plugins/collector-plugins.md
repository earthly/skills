
## Collector Plugin

* `lunar-collector.yml`
* Type: YAML file
* Form:
  ```yaml
  version: 0

  name: <collector-name>
  description: <collector-description>
  author: <author-name>

  default_image: <default-image>
  default_image_ci_collectors: <default-image-ci>
  default_image_non_ci_collectors: <default-image-non-ci>

  collectors:
    - <collector-configuration>
    - <collector-configuration>
    - ...

  inputs:
    <input-name>:
      description: <input-description>
      default: <default-value>
    ...
  ```

This page describes the configuration of a collector plugin. Collector plugins are used to collect live information from various sources to associate with individual components. Collector plugins can be imported from the Lunar configuration file, `lunar-config.yml` via the `uses` collector form.

Collector plugins can be defined either in a separate repository or in the same repository as the Lunar configuration, in a dedicated directory. Either way, the collector plugin must contain a `lunar-collector.yml` file in the root of the repository or directory. This file is used to configure the behavior of the collector plugin.

When using collectors in the Main or Run forms, you can also install dependencies. See [installing dependencies in the Bash SDK](../bash-sdk/dependencies.md) or [installing dependencies in the Python SDK](../python-sdk/dependencies.md) for more details.

## `version`

* `lunar-collector.yml -> version`
* Type: `numeric`
* Required

The version field is used to specify the version of the collector configuration file. The current version is `0`.

## `name`

* `lunar-collector.yml -> name`
* Type: `string`
* Required

The name field is used to specify the name of the collector.

## `description`

* `lunar-collector.yml -> description`
* Type: `string`
* Optional

The description field is used to specify a description of the collector.

## `author`

* `lunar-collector.yml -> author`
* Type: `string`
* Required

The author field is used to specify the author of the collector.

## Default Images

Collector plugins can define default Docker images that override the global defaults from `lunar-config.yml`. These settings apply to all collectors defined within the plugin.

### `default_image`

* `lunar-collector.yml -> default_image`
* Type: `string`
* Optional

The default image to use for all collectors in this plugin. Overrides the global `default_image` setting.

### `default_image_ci_collectors`

* `lunar-collector.yml -> default_image_ci_collectors`
* Type: `string`
* Optional

The default image for CI collectors (hooks: `ci-before-command`, `ci-after-command`, `ci-before-job`, `ci-after-job`). Overrides the global `default_image_ci_collectors` setting.

### `default_image_non_ci_collectors`

* `lunar-collector.yml -> default_image_non_ci_collectors`
* Type: `string`
* Optional

The default image for non-CI collectors (hooks: `code`, `cron`, `repo`). Overrides the global `default_image_non_ci_collectors` setting.

Individual collectors can still override these plugin defaults using the `image` field.

For more information about default images and container execution, see [Images](../lunar-config/images.md).

## `collectors`

* `lunar-collector.yml -> collectors`
* Type: `array`
* Required

The collectors field is used to specify the configuration of the collector. The format of a collector is the same as in `lunar-config.yml`, except that the `on` field is not allowed. To learn more about the configuration of a collector, see the [collectors](../lunar-config/collectors.md) page.

**Note:** When consumers import this plugin via `uses`, they can selectively include or exclude specific collectors using the [`include`](../lunar-config/collectors.md#include) field. This allows consumers to use only the collectors they need from a plugin that defines multiple collectors.

## `inputs`

* `lunar-collector.yml -> inputs`
* Type: `object`
* Optional

The inputs field is used to specify the inputs required by the collector. Each input is defined as a key-value pair, where the key is the input name.

Inputs are passed to the collector when invoked in the form of environment variables.

### `description`

* `lunar-collector.yml -> inputs.<input-name>.description`
* Type: `string`
* Optional

The description field is used to specify a description of the input.

### `default`

* `lunar-collector.yml -> inputs.<input-name>.default`
* Type: `string`
* Optional

The default field is used to specify the default value of the input. If no default value is specified, the input is required.
