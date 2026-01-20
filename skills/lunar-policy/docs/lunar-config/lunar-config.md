
## Lunar Configuration

* `lunar-config.yml`
* Type: YAML file
* Form:
  ```yaml
  version: 0

  default_image: <default-image>
  default_image_ci_collectors: <default-image-ci>
  default_image_non_ci_collectors: <default-image-non-ci>
  default_image_policies: <default-image-policies>
  default_image_catalogers: <default-image-catalogers>

  hub:
    host: <hub-host>
    grpc_port: <grpc-port>
    http_port: <http-port>
    insecure: <insecure-flag>
  
  catalogers:
    - <cataloger-object>
    - <cataloger-object>
    - ...

  domains:
    <domain-name>: <domain-object>
    <domain-name>: <domain-object>
    ...
  
  components:
    <component-name>: <component-object>
    <component-name>: <component-object>
    ...
  
  collectors:
    - <collector-object>
    - <collector-object>
    - ...
  
  initiatives:
    - <initiative-object>
    - <initiative-object>
    - ...

  policies:
    - <policy-object>
    - <policy-object>
    - ...
  ```

The file `lunar-config.yml` file is used to configure the behavior of Lunar. It is recommended that you create a new code repository for all Lunar configuration and place this file in the root of it.

At a high-level, the file contains information about how the Lunar primitives are configured, ranging from how information is collected from the SDLC via collectors, to how components are organized into domains, and how the health of components is evaluated via policies.

## `version`

* `lunar-config.yml -> version`
* Type: `numeric`
* Required

The version field is used to specify the version of the configuration file. The current version is `0`.

## Default Images

* `lunar-config.yml -> default_image*`
* Optional

These fields configure the default Docker images used to run collectors, policies, and catalogers. When set, scripts will run inside containers instead of natively on the host.

A common configuration is:

```yaml
default_image: earthly/lunar-scripts:1.0.0
default_image_ci_collectors: native
```

This runs most scripts in containers while keeping CI collectors native for direct access to CI environments.

For detailed documentation on default images, image resolution order, and the official `earthly/lunar-scripts` image, see [Images](./images.md).

## `hub`

* `lunar-config.yml -> hub`
* Type: `object`
* Required

The `hub` object contains configuration for the Lunar Hub server.

### `host`

* `lunar-config.yml -> hub.host`
* Type: `string`
* Required

The host field is used to specify the host of the Lunar Hub server.

### `grpc_port`

* `lunar-config.yml -> hub.grpc_port`
* Type: `integer`
* Required

The grpc_port field is used to specify the port of the Lunar Hub server for GRPC connections.

### `http_port`

* `lunar-config.yml -> hub.http_port`
* Type: `integer`
* Required

The http_port field is used to specify the port of the Lunar Hub server for HTTP connections.

### `insecure`

* `lunar-config.yml -> hub.insecure`
* Type: `boolean`
* Optional
* Default: `false`

The insecure field is used to specify whether to use insecure HTTP connections to the Lunar Hub server.

## `catalogers`

* `lunar-config.yml -> catalogers`
* Type: `array`
* Optional

Catalogers are used to synchronize software catalog information (such as domains, and components) with external systems.

For information on how to configure catalogers, see [catalogers](./catalogers.md).

## `domains`

* `lunar-config.yml -> domains`
* Type: `object`
* Optional

Domains are used to group related components together. Domains are hierarchical and can contain other domains.

For information on how to configure domains, see [domains](./domains.md).

## `components`

* `lunar-config.yml -> components`
* Type: `object`
* Optional

Components are the units of code that Lunar monitors. A component can represent either a code repository, or a subdirectory in the case of a monorepo.

Components are associated with domains and can have tags. Through the tagging system, components are associated with collectors, and policies.

For information on how to configure components, see [components](./components.md).

## `collectors`

* `lunar-config.yml -> collectors`
* Type: `array`
* Required

Collectors are used to collect live information from various sources to associate with individual components.

For information on how to configure collectors, see [collectors](./collectors.md).

## `initiatives`

* `lunar-config.yml -> initiatives`
* Type: `array`
* Optional

Initiatives are used to group components together. Initiatives are associated with domains and can have tags.

For information on how to configure initiatives, see [initiatives](./initiatives.md).

## `policies`

* `lunar-config.yml -> policies`
* Type: `array`
* Required

Policies are used to define the rules that Lunar uses to evaluate the health of components. Policies are associated with domains and can be inherited by child domains.

For information on how to configure policies, see [policies](./policies.md).
