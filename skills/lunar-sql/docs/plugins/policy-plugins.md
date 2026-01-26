
## Policy Plugin

* `lunar-policy.yml`
* Type: YAML file
* Form:
  ```yaml
  version: 0

  name: <policy-name>
  description: <policy-description>
  author: <author-name>

  default_image: <default-image>

  policies:
    - <policy-configuration>
    - <policy-configuration>
    - ...

  inputs:
    <input-name>:
      description: <input-description>
      default: <default-value>
    ...
  ```

This page describes the configuration of a policy plugin. Policy plugins are used to define the rules that Lunar uses to evaluate the health of components. Policy plugins can be imported from the Lunar configuration file, `lunar-config.yml` via the `uses` policy form.

Policy plugins can be defined either in a separate repository or in the same repository as the Lunar configuration, in a dedicated directory. Either way, the policy plugin must contain a `lunar-policy.yml` file in the root of the repository or directory. This file is used to configure the behavior of the policy plugin.

When using policies in the Main or Run forms, you can also install dependencies. See [installing dependencies in the Python SDK](../python-sdk/dependencies.md) for more details.

## `version`

* `lunar-policy.yml -> version`
* Type: `numeric`
* Required

The version field is used to specify the version of the policy configuration file. The current version is `0`.

## `name`

* `lunar-policy.yml -> name`
* Type: `string`
* Required

The name field is used to specify the name of the policy.

## `description`

* `lunar-policy.yml -> description`
* Type: `string`
* Optional

The description field is used to specify a description of the policy.

## `author`

* `lunar-policy.yml -> author`
* Type: `string`
* Required

The author field is used to specify the author of the  policy.

## `default_image`

* `lunar-policy.yml -> default_image`
* Type: `string`
* Optional

The default Docker image to use for all policies in this plugin. This overrides the global `default_image_policies` setting from `lunar-config.yml`.

Individual policies can still override this plugin default using the `image` field. Use the special value `native` to explicitly run without a container.

For more information about default images and container execution, see [Images](../lunar-config/images.md).

## `policies`

* `lunar-policy.yml -> policies`
* Type: `array`
* Required

The policies field is used to specify the configuration of the policy. The format of a policy is the same as in `lunar-config.yml`, except that the `on` and `level` fields are not allowed (these are configured in `lunar-config.yml` only). To learn more about the configuration of a policy, see the [policies](../lunar-config/policies.md) page.

**Note:** When consumers import this plugin via `uses`, they can selectively include or exclude specific policies using the [`include`](../lunar-config/policies.md#include) field. This allows consumers to use only the policies they need from a plugin that defines multiple policies.

## `inputs`

* `lunar-policy.yml -> inputs`
* Type: `object`
* Optional

The inputs field is used to specify the inputs that the policy requires. Each input is defined as a key-value pair, where the key is the input name.

Inputs are accessed in policies using the `variable_or_default` function from the `lunar_policy` SDK. For example, an input named `threshold` is accessible as `variable_or_default("threshold", "10")` where the second argument is the fallback default value.

### `description`

* `lunar-policy.yml -> inputs.<input-name>.description`
* Type: `string`
* Optional

The description field is used to specify a description of the input.

### `default`

* `lunar-policy.yml -> inputs.<input-name>.default`
* Type: `string`
* Optional

The default field is used to specify the default value of the input. If no default value is specified, the input is required.
