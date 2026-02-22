
## Collectors

* `lunar-config.yml -> collectors`
* Type: `array`
* Form:
  ```yaml
  collectors:
    - <collector-object>
    - <collector-object>
    - ...
  ```

Collectors are used to collect live information from various sources to associate with individual components.

Example collectors definition:

```yaml
collectors:
  - uses: github://third-party/some-collector@v1
    on: [auth, frontend]
    hook:
      type: ci-before-command
      pattern: ^go build.*
  - uses: ./my-collector
    on: ["domain:my-domain"]
    hook:
      type: ci-before-job
      pattern: .*
  - uses: ./my-collector
    on: ["domain:foo-product"]
    hook:
      type: code
  - uses: ./another-collector
    on: [go]
    hook:
      type: cron
      schedule: "0 2 * * *"
  - name: Hello world collector
    runBash: lunar collect '.hello' world
    on: [java]
    hook: 
      type: ci-after-command
      pattern: ^mvn install.*
  - name: Example script collector
    mainBash: ./my-script.sh
    on: [python]
    hook:
      type: cron
      schedule: "0 2 * * *"
```

## Collector

* `lunar-config.yml -> collectors.<collector-index>`
* Type: `object`
* Forms
  * Uses form (use an external collector plugin):
    ```yaml
    name: <collector-name>
    uses: <collector-string>
    include: <include-array>
    exclude: <exclude-array>
    with:
      <input-name>: <input-value>
      ...
    on: <domain-array>
    image: <docker-image>
    ```
  * Run form (define a collector inline):
    ```yaml
    name: <collector-name>
    run<language>: <command-string>
    on: <domain-array>
    image: <docker-image>
    hook: <hook-configuration>
    hooks:
      - <hook-configuration>
      - <hook-configuration>
      - ...
    ```
  * Main form (define a collector inline with a main file):
    ```yaml
    name: <collector-name>
    main<language>: <main-file-path>
    on: <domain-array>
    image: <docker-image>
    hook: <hook-configuration>
    hooks:
      - <hook-configuration>
      - <hook-configuration>
      - ...
    ```

Collectors are used to collect live information from various sources to associate with individual components. Collectors can be used to instrument CI/CD pipelines, run cron jobs, or execute arbitrary logic when code changes.

Collectors can either be imported (Uses form), defined as an inline command (Run form), or defined as a script to run (Main form). When a collector is defined inline (Run and Main forms), a hook must be specified to determine when the collector should run.

### `name`

* `lunar-config.yml -> collectors.<collector-index>.name`
* Type: `string`
* Required for Run and Main collector forms, Optional for Uses collector form

The `name` field is used to specify the name of the collector. If a name is not provided in the case of a collector plugin, the name from the collector plugin is used. The name must be unique within the configuration.

### `uses`

* `lunar-config.yml -> collectors.<collector-index>.uses`
* Type: `string`
* Forms
  * GitHub form: `github://<org>/<repo>@<version>`
  * Local form: `./<path-to-collector>`
* Required in Uses collector form

The `uses` field specifies an external (plugin) collector to use. The collector can be a third-party collector, or a local collector defined in a subdirectory. Browse the [30+ available integrations](https://earthly.dev/lunar/integrations/) to find collectors for your tools.

### `with`

* `lunar-config.yml -> collectors.<collector-index>.with`
* Type: `object`
* Optional

The `with` field specifies the inputs to pass to the collector plugin. The inputs are defined in the collector's configuration file.

### `include`

* `lunar-config.yml -> collectors.<collector-index>.include`
* Type: `array`
* Optional

The `include` field specifies which subcollectors to include from an imported collector plugin. When a collector is imported via `uses`, it may define (or import) multiple subcollectors. Use `include` to control which of those subcollectors are used.

If neither `include` nor `exclude` is specified, all subcollectors are included by default.

### `exclude`

* `lunar-config.yml -> collectors.<collector-index>.exclude`
* Type: `array`
* Optional

The `exclude` field specifies which subcollectors to exclude from an imported collector plugin. Use `exclude` when you want to include most subcollectors but skip a few specific ones.

If neither `include` nor `exclude` is specified, all subcollectors are included by default.

For example, if a collector called `go` includes subcollectors named `version`, `dependencies`, and `build-info`:

```yaml
collectors:
  # Include only the version subcollector
  - uses: ./dir/go
    include: [version]

  # Include all except version
  - uses: ./dir/go
    exclude: [version]

  # Include version and dependencies only
  - uses: ./dir/go
    include: [version, dependencies]
```

### `run<language>`

* `lunar-config.yml -> collectors.<collector-index>.run<language>`
* Type: `string`
* Required in Run collector form

Defines the command to execute when the collector is invoked. Only `Bash` and `Python` are supported. So `runBash` and `runPython` are the only valid fields.

Running Bash supports [installing dependencies](../bash-sdk/dependencies.md).

#### `runBash`

* `lunar-config.yml -> collectors.<collector-index>.runBash`
* Type: `string`

The `runBash` field specifies the bash collector script to run.

#### `runPython`

* `lunar-config.yml -> collectors.<collector-index>.runPython`
* Type: `string`

The `runPython` field specifies the python collector script to run. Running Python supports [installing dependencies](../python-sdk/dependencies.md).

### `main<language>`

* `lunar-config.yml -> collectors.<collector-index>.main<language>`
* Type: `string`
* Required in Main collector form

Defines the main file path used to execute when the collector is invoked. Only `Bash` and `Python` are supported. So `mainBash` and `mainPython` are the only valid field.

The file path is relative to the root of the Lunar configuration repository. In the case of an external plugin definition, the path is relative to the plugin directory.

Running Bash supports [installing dependencies](../bash-sdk/dependencies.md).

#### `mainBash`

* `lunar-config.yml -> collectors.<collector-index>.mainBash`
* Type: `string`

The `mainBash` field specifies the path to the bash main file to run.

#### `mainPython`

* `lunar-config.yml -> collectors.<collector-index>.mainPython`
* Type: `string`

The `mainPython` field specifies the path to the python main file to run. Running Python supports [installing dependencies](../python-sdk/dependencies.md).

### `on`

* `lunar-config.yml -> collectors.<collector-index>.on`
* Type: `array`
* Required

The `on` field specifies the tags that the collector should be associated with. The collector will only run when the component has one or more of the specified tags.

For detailed documentation on tag matching syntax, including domain/component targeting, expressions, and cross-references to other collectors or policies, see [Tag Matching with `on`](./on.md).

### `hook`

* `lunar-config.yml -> collectors.<collector-index>.hook`
* Type: `object`
* One of `hook` or `hooks` is required in Run collector form

Using `hook` is equivalent to using a single hook in the `hooks` field. The `hook` field specifies when the collector should run.

For more information about hook definitions see the [hooks configuration page](./collector-hooks.md).

### `hooks`

* `lunar-config.yml -> collectors.<collector-index>.hooks`
* Type: `array`
* One of `hook` or `hooks` is required in Run collector form

The `hooks` field specifies when the collector should run.

For more information about hook definitions see the [hooks configuration page](./collector-hooks.md).

### `image`

* `lunar-config.yml -> collectors.<collector-index>.image`
* Type: `string`
* Optional

The `image` field specifies the Docker image to use when running the collector. When set, the collector runs inside a container instead of natively on the host.

Use the special value `native` to explicitly run the collector without a container, even when a default image has been configured.

Example:

```yaml
collectors:
  # Run in a container
  - runBash: lunar collect .file-count "$(find . | wc -l)"
    image: earthly/lunar-scripts:1.0.0
    hook:
      type: code
    on: [my-tag]

  # Run natively (override any default image)
  - runBash: lunar collect .ci-info "$CI_JOB_ID"
    image: native
    hook:
      type: ci-before-command
      pattern: ^.*
    on: [my-tag]
```

For more information about default images and container execution, see [Images](./images.md).
