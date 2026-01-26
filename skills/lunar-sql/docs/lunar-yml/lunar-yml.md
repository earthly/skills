
## Component lunar.yml

* `lunar.yml`
* Type: YAML file
* Form:
  ```yaml
  version: 0

  owner: <email>
  domain: <domain-path>
  branch: <branch-name>
  tags: [<tag>, <tag>, ...]
  ciPipelines: [<ci-pipeline>, <ci-pipeline>, ...]
  ```

This page describes the configuration of a component via lunar.yml.

The file lunar.yml is optional and it can be used to define the configuration of a single component. If lunar.yml is not provided, the component configuration can be defined in the Lunar configuration file, [lunar-config.yml](../lunar-config/lunar-config.md). With the exception of the version field, the same fields in `lunar-config.yml -> components.<component-name>` are used in `lunar.yml`.

If a component is defined in both lunar.yml and lunar-config.yml, the settings are merged, and the configuration in lunar-config.yml takes precedence when a scalar field (`owner`, `domain`, `branch`) is defined in both places. The arrays (`tags`, `ci-pipelines`) are appended to each other.

### `version`

* `lunar.yml -> version`
* Type: `numeric`
* Required

The version field is used to specify the version of the component configuration file. The current version is `0`.

### Other Fields

The other fields in `lunar.yml` are the same as those in `lunar-config.yml -> components.<component-name>`. For more information, see the [lunar-config.yml components](../lunar-config/components.md) page.
