
## Policies

* `lunar-config.yml -> policies`
* Type: `array`
* Form:
  ```yaml
  policies:
    - <policy-object>
    - <policy-object>
    - ...
  ```

Policies are used to define the rules that Lunar uses to evaluate the health of components.

Example policies definition:

```yaml
policies:
  - uses: github://third-party/some-policy@v1
    on: [my-domain]
    enforcement: block-pr
  - uses: ./security-scanning
    on: [my-domain, another-domain]
    runs_on: [default-branch]
    enforcement: score
  - name: Collect code coverage information
    runPython: |
      from lunar_policy import Check, Path
      with Check("codecov-check", "Verify code coverage was collected") as check:
          check.assert_true(Path(".codecov.was_run"), "Code coverage data should be collected")
    on: [another-domain]
  - name: Should have unit tests
    mainPython: ./unit-tests.py
    on: [another-domain]
    enforcement: block-pr-and-release
```

## Policy

* `lunar-config.yml -> policies.<policy-index>`
* Type: `object`
* Forms:
  * Uses form:
    ```yaml
    name: <policy-name>
    uses: <policy-string>
    include: <include-array>
    exclude: <exclude-array>
    with:
      <input-name>: <input-value>
      ...
    on: <domain-array>
    runs_on: <runs-on-array>
    enforcement: <enforcement-level>
    initiative: <initiative-name>
    image: <docker-image>
    ```
  * Run form:
    ```yaml
    name: <policy-name>
    description: <policy-description>
    run<language>: <code-string>
    on: <domain-array>
    runs_on: <runs-on-array>
    enforcement: <enforcement-level>
    initiative: <initiative-name>
    image: <docker-image>
    ```
  * Main form:
    ```yaml
    name: <policy-name>
    description: <policy-description>
    main<language>: <main-file-path>
    on: <domain-array>
    runs_on: <runs-on-array>
    enforcement: <enforcement-level>
    initiative: <initiative-name>
    image: <docker-image>
    ```

Policies are used to define the rules that Lunar uses to evaluate the health of components. Policies are associated with domains and are automatically inherited by child domains.

### `name`

* `lunar-config.yml -> policies.<policy-index>.name`
* Type: `string`
* Required for Run and Main policy forms, Optional for Uses policy form

The `name` field is used to specify the name of the policy. If a name is not provided in the case of a policy plugin, the name from the policy plugin is used. The name must be unique within the configuration.

### `uses`

* `lunar-config.yml -> policies.<policy-index>.uses`
* Type `string`
* Forms
  * GitHub form: `github://<owner>/<repo>@<version>`
  * Local form: `./<path-to-policy>`
* Required in Uses policy form

The `uses` field is used to import an external (plugin) policy from a GitHub repository or a local file. The policy is then associated with a domain. Browse the [100+ available guardrails](https://earthly.dev/lunar/guardrails/) to find policies for your standards.

### `with`

* `lunar-config.yml -> policies.<policy-index>.with`
* Type: `object`
* Optional

The `with` field specifies the inputs to pass to the policy plugin. The inputs are defined in the policy's configuration file.

### `include`

* `lunar-config.yml -> policies.<policy-index>.include`
* Type: `array`
* Optional

The `include` field specifies which sub-policies to include from an imported policy plugin. When a policy is imported via `uses`, it may define (or import) multiple sub-policies. Use `include` to control which of those sub-policies are used.

If neither `include` nor `exclude` is specified, all sub-policies are included by default.

### `exclude`

* `lunar-config.yml -> policies.<policy-index>.exclude`
* Type: `array`
* Optional

The `exclude` field specifies which sub-policies to exclude from an imported policy plugin. Use `exclude` when you want to include most sub-policies but skip a few specific ones.

If neither `include` nor `exclude` is specified, all sub-policies are included by default.

For example, if a policy called `security` includes sub-policies named `vulnerability-scan`, `license-check`, and `dependency-audit`:

```yaml
policies:
  # Include only the vulnerability-scan sub-policy
  - uses: ./dir/security
    include: [vulnerability-scan]

  # Include all except license-check
  - uses: ./dir/security
    exclude: [license-check]

  # Include vulnerability-scan and license-check only
  - uses: ./dir/security
    include: [vulnerability-scan, license-check]
```

### `description`

* `lunar-config.yml -> policies.<policy-index>.description`
* Type: `string`
* Optional

The `description` field is used to specify a description of the policy. If a description is not provided in the case of a policy plugin, the description from the policy plugin is used.

### `run<language>`

* `lunar-config.yml -> policies.<policy-index>.run<language>`
* Type: `string`
* Required in Run policy form

Defines the command to execute when the policy is invoked. Only `Python` is supported. So `runPython` is the only valid field.

Running Bash supports [installing dependencies](../bash-sdk/dependencies.md).

#### `runPython`

* `lunar-config.yml -> policies.<policy-index>.runPython`
* Type: `string`

The `runPython` field specifies the python policy script to run. Running Python supports [installing dependencies](../python-sdk/dependencies.md).

### `main<language>`

* `lunar-config.yml -> policies.<policy-index>.main<language>`
* Type: `string`
* Required in Main policy form

Defines the main file path used to execute when the policy is invoked. Only `Python` is supported. So `mainPython` is the only valid field.

The file path is relative to the root of the Lunar configuration repository. In the case of an external plugin definition, the path is relative to the plugin directory.

Running Bash supports [installing dependencies](../bash-sdk/dependencies.md).

#### `mainPython`

* `lunar-config.yml -> policies.<policy-index>.mainPython`
* Type: `string`

The `mainPython` field specifies the path to the python main file to run. Running Python supports [installing dependencies](../python-sdk/dependencies.md).

### `on`

* `lunar-config.yml -> policies.<policy-index>.on`
* Type: `array`
* Required

The `on` field specifies the tags that the policy should be associated with. The policy will apply when the component has one or more of the specified tags.

For detailed documentation on tag matching syntax, including domain/component targeting, expressions, and cross-references to other collectors or policies, see [Tag Matching with `on`](./on.md).

### `runs_on`

* `lunar-config.yml -> policies.<policy-index>.runs_on`
* Type: `array`
* Default: `[prs, default-branch]`

Specifies the contexts in which the policy should run. The available values are:

* `prs` - the policy will run on pull requests
* `default-branch` - the policy will run on the default branch

By default, policies run in both contexts. To restrict a policy to only run on pull requests, use `runs_on: [prs]`. To restrict a policy to only run on the default branch, use `runs_on: [default-branch]`.

### `enforcement`

* `lunar-config.yml -> policies.<policy-index>.enforcement`
* Type: `string`. One of `draft`, `score`, `report-pr`, `block-pr`, `block-release`, `block-pr-and-release`
* Optional - defaults to `report-pr`

The `enforcement` field specifies the enforcement level of the policy. It determines how the policy affects the component.

The following enforcement levels are supported:

* `draft` - the policy is still under development and does not affect the score, and is not enforced or shown to application teams
* `score` - the checks under this policy only contribute to the score of the component, but are not reported in PRs
* `report-pr` - the checks under this policy report the results in PRs, but do not block them
* `block-pr` - the checks under this policy block PRs from being merged
* `block-release` - the checks under this policy block releases, but not PRs. This level may be useful for checks that don't necessarily run in PRs due to performance reasons, but are nevertheless important to gate the release process.
* `block-pr-and-release` - the checks under this policy block both PRs and releases

When `block-release` or `block-pr-and-release` levels are used, the Lunar CLI command `lunar policy ok-release <component> <git_sha>` will return a non-zero exit code of `1` if the associated policy is failing for the given component. This command may be used in CD or release pipelines to prevent a deployment to production, or a release package to be published.

When `block-pr` or `block-pr-and-release` levels are used, the Lunar CLI command `lunar policy ok-pr <component> <git_sha>`will return a non-zero exit code of `1` if the associated policy is failing for the given component. This command may be used wherever needed to block PR merges or prevent PR deployment pipelines to staging environments.

### `initiative`

* `lunar-config.yml -> policies.<policy-index>.initiative`
* Type: `string`
* Optional - defaults to `default`

The `initiative` field specifies the initiative that the policy belongs to. Initiatives are used to group related policies together for easier management and reporting. If not specified, the policy will be associated with the built-in "default" initiative.

For information on how to configure initiatives, see [initiatives](./initiatives.md).

### `image`

* `lunar-config.yml -> policies.<policy-index>.image`
* Type: `string`
* Optional

The `image` field specifies the Docker image to use when running the policy. When set, the policy runs inside a container instead of natively on the host.

Use the special value `native` to explicitly run the policy without a container, even when a default image has been configured.

Example:

```yaml
policies:
  # Run in a container
  - uses: ./my-policy
    image: earthly/lunar-scripts:1.0.0
    on: [my-tag]

  # Run natively (override any default image)
  - mainPython: ./local-policy.py
    image: native
    on: [my-tag]
```

For more information about default images and container execution, see [Images](./images.md).
