
## Components

* `lunar-config.yml -> components`
* Type: `object`
* Form:
  ```yaml
  components:
    <component-name>: <component-object>
    <component-name>: <component-object>
    ...
  ```

Components are the individual units of code that are monitored by Lunar. They represent a complete software deliverable, such as a microservice, binary, or a library. Components can be an entire repository, or a subdirectory within a repository in the case of monorepos.

The name of a component is the repository URL or a pattern that matches multiple repositories. For example, `github.com/my-org/my-repo` or `github.com/my-org/*`.

Each component automatically receives the special tag `component:<component-id>`. For example, the component `github.com/my-org/my-repo` will receive the tag `component:github.com/my-org/my-repo`. This tag can be used in [tag matching expressions](./on.md) to target specific components.

Components can be defined here, in the Lunar configuration file, or in a separate file, `lunar.yml`, in the root of the component directory. Both definitions can co-exist, complementing each other (some components can be defined centrally in `lunar-config.yml`, while others can be defined via `lunar.yml`).

Example components definition:

```yaml
components:
  github.com/my-org/my-repo:
    owner: jane@example.com
    domain: widget-product.frontend
    branch: prod
    tags: [go, backend, pii]
  github.com/my-org/my-monorepo/*:
    tags: [tier1]
  github.com/my-org/my-monorepo/proj1:
    owner: jacqueline@example.com
    domain: widget-product.data-processing
    tags: [java, backend]
    meta:
      "pagerduty-escalation-policy": "P1"
  github.com/my-org/ui-*:
    tags: [frontend]
  github.com/my-org/ui-components:
    owner: jack@example.com
    domain: ui-common
    tags: [react, typescript]
```

## Component

* `lunar-config.yml -> components.<component-name>`
* Type: `object`
* Form:
  ```yaml
  owner: <email>
  domain: <domain-path>
  branch: <branch-name>
  tags: [<tag>, <tag>, ...]
  ciPipelines: [<ci-pipeline>, <ci-pipeline>, ...]
  meta:
    <meta-key>: <meta-value>
    <meta-key>: <meta-value>
    ...
  ```

A single component is a unit of code that is monitored by Lunar. It represents a complete software deliverable, such as a microservice, binary, or a library.

As an alternative to defining components in `lunar-config.yml`, they may also be defined in a separate file, `lunar.yml`, in the root of the component directory. The fields in `lunar.yml` are the same as those in `lunar-config.yml -> components.<component-name>`. For more information, see the [lunar.yml](../lunar-yml/lunar-yml.md) page.

### `owner`

* `lunar-config.yml -> components.<component-name>.owner`
* Type: `string`
* Optional

The email address of the owner of the component.

### `domain`

* `lunar-config.yml -> components.<component-name>.domain`
* Type: `string`
* Optional

A component can only belong to one domain. This field specifies the domain that the component belongs to.

To associate a component with a subdomain, specify the entire domain path. For example, to associate a component with the domain `bar`, which is under the domain `foo`, use the domain `foo.bar`.

If a domain is not specified, the component is placed in the `other` domain.

When a component is associated with a domain, it automatically gets the tag `domain:<domain-name>`. See [Tag Matching with `on`](./on.md) for more details on how to use these tags.

### `branch`

* `lunar-config.yml -> components.<component-name>.branch`
* Type: `string`
* Optional

The branch that the component is monitored on. If not specified, the default branch is used.

### `tags`

* `lunar-config.yml -> components.<component-name>.tags`
* Type: `array`
* Optional

A list of tags that to apply to the component. Tags can be used to associate collectors and policies to specific components.

### `ciPipelines`

* `lunar-config.yml -> components.<component-name>.ciPipelines`
* Type: `array`
* Optional - defaults to all CI pipelines in the repository

A list of CI pipeline names that are associated with the component. The CI pipelines are used to trigger the collection of data for the component. A single CI pipeline may be associated with multiple components at a time. If no CI pipelines are specified, then all CI pipelines within the repository are associated with the component.

This setting can be useful in monorepos, when certain CI pipelines might not be relevant to a specific component.

The pipeline name in GitHub Actions is the name of the GitHub Actions job. In GitLab CI it is the name of the GitLab CI job. In Buildkite, it is the name of the Buildkite pipeline.

### `meta`

* `lunar-config.yml -> components.<component-name>.meta`
* Type: `object`
* Optional

A key-value store of arbitrary metadata for the component. This metadata is not used by Lunar, but can be used by collectors and policies.
