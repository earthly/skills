
## Catalogers

* `lunar-config.yml -> catalogers`
* Type: `array`
* Form:
  ```yaml
  - <cataloger-object>
  - <cataloger-object>
  - ...
  ```

Catalogers are used to synchronize software catalog information, such as domains, and components, with external systems.

The catalog information resulting from catalogers is merged in the order in which the catalogers are defined. This means that if two catalogers define the same field (e.g. `owner`) within the same component, the last one will take precedence.

After the cataloger information is merged, the information collected from any [`lunar.yml`](../lunar-yml/lunar-yml.md) files, and any component and domain information from [`lunar-config.yml`](./lunar-config.md), is merged to form the final catalog JSON, which is then used by Lunar to form the structure of domains and components internally.

Example catalogers definition:

```yaml
catalogers:
  - name: GitHub repos
    runBash: |-
        gh repo list <my-org> --json | ... | \
        lunar catalog --json '.components' -
    hook:
      type: cron
      schedule: "0 2 * * *"
  - name: Backstage sync
    runBash: |-
        curl <curl-options> https://<backstage endpoint>/api/catalog/entities/by-query ... | ... | \
        lunar catalog --json '.components' -
    hook:
      type: cron
      schedule: "0 2 * * *"
  - name: DB sync
    runBash: |-
        psql ... -c 'COPY (select * FROM services WHERE ...) TO STDOUT WITH CSV HEADER' | \
        csvjson --no-header-row | ... | \
        lunar catalog --json '.components' -
    hook:
      type: cron
      schedule: "0 2 * * *"
  - name: Pick up catalog files from some central repo
    runBash: |-
      cat verticals.toml | ... | lunar catalog --json '.domains' -
      cat services.toml | ... | lunar catalog --json '.components' -
    hook:
      type: repo
      repo: github.com/foo/software-catalog
  - name: Label any repo that has a certain CI pipeline as "production"
    runBash: |-
      if grep -r --include="*.yaml" --include="*.yml" '^name: Deploy$' ./.github/workflows ; then
        lunar catalog component --tag production
      fi
    hook:
      type: component-rep
  - name: Complex operation
    mainBash: ./my-script.sh
    hook:
      type: cron
      schedule: "0 2 * * *"
  - name: Use an external cataloger
    uses: github://third-party/some-cataloger@v1
```

## Cataloger

* `lunar-config.yml -> catalogers.<cataloger-index>`
* Type: `object`
* Forms
  * Uses form (use an external cataloger plugin):
    ```yaml
    name: <cataloger-name>
    uses: <cataloger-repo>
    include: <include-array>
    exclude: <exclude-array>
    with:
        <input-name>: <input-value>
        ...
    image: <docker-image>
    ```
  * Run form (define a cataloger inline):
    ```yaml
    name: <cataloger-name>
    run<language>: <script>
    hook: <hook-configuration>
    image: <docker-image>
    ```
  * Main form (define a cataloger inline with a main file):
    ```yaml
    name: <cataloger-name>
    main<language>: <script>
    hook: <hook-configuration>
    image: <docker-image>
    ```

Catalogers are used to dynamically import information about components and domains from external systems. They are run on a schedule or in response to certain events, such as a commit to a repository.

Catalogers can either be imported (Uses form), defined as an inline command (Run form), or defined as a script with a main file (Main form). When a cataloger is defined inline (Run and Main forms), a hook must be specified to determine when the cataloger should run.

### `name`

* `lunar-config.yml -> catalogers.<cataloger-index>.name`
* Type: `string`
* Required for Run and Main cataloger forms, Optional for Uses cataloger form

The name of the cataloger. This is used to identify the cataloger in the Lunar UI and logs.

### `uses`

* `lunar-config.yml -> catalogers.<cataloger-index>.uses`
* Type: `string`
* Forms
  * GitHub form: `github://<org>/<repo>@<version>`
  * Local form: `./<path-to-cataloger>`
* Required for Uses cataloger form

The `uses` field specifies an external (plugin) cataloger to use. The cataloger can be a third-party cataloger, or a local cataloger defined in a subdirectory.

### `with`

* `lunar-config.yml -> catalogers.<cataloger-index>.with`
* Type: `object`
* Optional

The `with` field specifies the inputs to pass to the cataloger plugin. The inputs are defined in the cataloger's configuration file.

### `include`

* `lunar-config.yml -> catalogers.<cataloger-index>.include`
* Type: `array`
* Optional

The `include` field specifies which sub-catalogers to include from an imported cataloger plugin. When a cataloger is imported via `uses`, it may define (or import) multiple sub-catalogers. Use `include` to control which of those sub-catalogers are used.

If neither `include` nor `exclude` is specified, all sub-catalogers are included by default.

### `exclude`

* `lunar-config.yml -> catalogers.<cataloger-index>.exclude`
* Type: `array`
* Optional

The `exclude` field specifies which sub-catalogers to exclude from an imported cataloger plugin. Use `exclude` when you want to include most sub-catalogers but skip a few specific ones.

If neither `include` nor `exclude` is specified, all sub-catalogers are included by default.

For example, if a cataloger called `backstage` includes sub-catalogers named `components`, `domains`, and `users`:

```yaml
catalogers:
  # Include only the components sub-cataloger
  - uses: ./dir/backstage
    include: [components]

  # Include all except users
  - uses: ./dir/backstage
    exclude: [users]

  # Include components and domains only
  - uses: ./dir/backstage
    include: [components, domains]
```

### `run<language>`

* `lunar-config.yml -> catalogers.<cataloger-index>.run<language>`
* Type: `string`
* Required in Run cataloger form

Defines the command to execute when the cataloger is invoked. Only `Bash` is supported currently. So `runBash` is the only valid fields.

Running Bash supports [installing dependencies](../bash-sdk/dependencies.md).

#### `runBash`

* `lunar-config.yml -> catalogers.<cataloger-index>.runBash`
* Type: `string`

The `runBash` field specifies the bash cataloger script to run.

### `main<language>`

* `lunar-config.yml -> catalogers.<cataloger-index>.main<language>`
* Type: `string`
* Required in Main cataloger form

Defines the main file path used to execute when the cataloger is invoked. Only `Bash` is supported currently. So `mainBash` is the only valid field.

The file path is relative to the root of the Lunar configuration repository. In the case of an external plugin definition, the path is relative to the plugin directory.

Running Bash supports [installing dependencies](../bash-sdk/dependencies.md).

#### `mainBash`

* `lunar-config.yml -> catalogers.<cataloger-index>.mainBash`
* Type: `string`

The `mainBash` field specifies the bash cataloger script to run.

### `hook`

* `lunar-config.yml -> catalogers.<cataloger-index>.hook`
* Type: `object`
* Required for Run and Main cataloger forms

The `hook` field specifies when the cataloger should run. The hook can be a cron job, a repository event, or a component event.

For more information on how to configure hooks, see [hooks](./cataloger-hooks.md).

### `image`

* `lunar-config.yml -> catalogers.<cataloger-index>.image`
* Type: `string`
* Optional

The `image` field specifies the Docker image to use when running the cataloger. When set, the cataloger runs inside a container instead of natively on the host.

Use the special value `native` to explicitly run the cataloger without a container, even when a default image has been configured.

Example:

```yaml
catalogers:
  # Run in a container
  - name: Sync from external system
    runBash: curl https://api.example.com/services | lunar catalog --json '.components' -
    image: earthly/lunar-scripts:1.0.0
    hook:
      type: cron
      schedule: "0 2 * * *"

  # Run natively (override any default image)
  - name: Local sync
    mainBash: ./sync-local.sh
    image: native
    hook:
      type: cron
      schedule: "0 3 * * *"
```

For more information about default images and container execution, see [Images](./images.md).
