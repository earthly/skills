## Initiatives

* `lunar-config.yml -> initiatives`
* Type: `array`
* Form:
  ```yaml
  initiatives:
    - name: <initiative-name>
      description: <initiative-description>
      owner: <initiative-owner>
      on: [<tag>, <tag>, ...]
    - name: <initiative-name>
      description: <initiative-description>
      owner: <initiative-owner>
      on: [<tag>, <tag>, ...]
    ...
  ```

Initiatives are used to group policies together around a specific goal or compliance requirement. They provide a way to organize policies and make them easier to manage and monitor.

Example initiatives definition:

```yaml
initiatives:
  - name: security
    description: Security policies for all components
    owner: security-team@example.com
    on: [security, backend, frontend]
  - name: performance
    description: Performance optimization policies
    owner: platform-team@example.com
    on: [backend, api]
  - name: documentation
    description: Documentation compliance policies
    owner: docs-team@example.com
    on: [all]
```

## Initiative

* `lunar-config.yml -> initiatives.<initiative-index>`
* Type: `object`
* Form:
  ```yaml
  name: <initiative-name>
  description: <initiative-description>
  owner: <initiative-owner>
  on: [<tag>, <tag>, ...]
  ```

An initiative represents a collection of policies organized around a specific goal or purpose. Initiatives make it easier to manage and track related policies.

### `name`

* `lunar-config.yml -> initiatives.<initiative-index>.name`
* Type: `string`
* Required

The name field is used to specify the unique identifier for the initiative.

### `description`

* `lunar-config.yml -> initiatives.<initiative-index>.description`
* Type: `string`
* Optional

The description field is used to provide a human-readable description of the initiative.

### `owner`

* `lunar-config.yml -> initiatives.<initiative-index>.owner`
* Type: `string`
* Optional

The owner field is used to specify the person or team responsible for the initiative. This is typically an email address.

### `on`

* `lunar-config.yml -> initiatives.<initiative-index>.on`
* Type: `array of strings`
* Optional

The `on` field specifies the tags that the initiative applies to. These tags are used to associate policies with the initiative.

For detailed documentation on tag matching syntax, including domain/component targeting, expressions, and cross-references to other collectors or policies, see [Tag Matching with `on`](./on.md). 