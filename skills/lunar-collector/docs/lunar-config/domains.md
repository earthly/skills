
## Domains

* `lunar-config.yml -> domains`
* Type: `object`
* Form:
  ```yaml
  domains:
    <domain-path>: <domain-object>
    <domain-path>: <domain-object>
    ...
  ```

Domains are used to group related components together. Domains are hierarchical and can contain other domains.

A domain's path is a string that uniquely identifies the domain. If a domain `bar` is within the domain `foo`, then the domain path is `foo.bar`.

Components under a domain receive the special tag `domain:<domain-name>` automatically. For example, components in the domain `foo.bar` will receive the tag `domain:foo.bar`. This tag can be used in [tag matching expressions](./on.md) to target components by domain.

Example domains defintion:

```yaml
domains:
  saas-product:
    description: Acme's SaaS product
    owner: roberto@example.com
  saas-product.frontend:
    description: The frontend of Acme's SaaS product
    owner: jacqueline@example.com
  saas-product.frontend.ui-components:
    description: Common UI components for the frontend
    owner: jill@example.com
  saas-product.frontend.ui-common:
    description: Common UI code for the frontend
    owner: jane@example.com
  saas-product.frontend.ui-dashboard:
    description: The dashboard for the frontend
    owner: mary@example.com
  saas-product.frontend.ui-login:
    description: The login page for the frontend
    owner: jessica@example.com
  saas-product.backend:
    description: The backend of Acme's SaaS product
    owner: john@example.com
  saas-product.backend.auth:
    description: The authentication service for the backend
    owner: jesse@example.com
  saas-product.backend.rev-proxy:
    description: The reverse proxy for the backend
    owner: mike@example.com
  saas-product.backend.gateway:
    description: The gateway for the backend
    owner: larry@example.com
  widget-product:
    description: Acme's widget product
    owner: noah@example.com
  widget-product.frontend:
    description: The frontend of Acme's widget product
    owner: corey@example.com
  widget-product.data-processing:
    description: Data processing for Acme's widget product
    owner: ann@example.com
  common-infra:
    description: Common infrastructure
    owner: alice@example.com
    meta:
      "okta-team": "infra"
  common-infra.monitoring:
    description: Monitoring for common infrastructure
    owner: bob@example.com
  common-infra.logging:
    description: Logging for common infrastructure
    owner: todd@example.com
```

Domains are associated with components using the `domain` field in the [component definition](./components.md).

## Domain

* `lunar-config.yml -> domains.<domain-path>`
* Type: `object`
* Form:
  ```yaml
  description: <description>
  owner: <email>
  meta:
    <meta-key>: <meta-value>
    <meta-key>: <meta-value>
    ...
  ```

A domain is a group of related components. Domains are hierarchical and can contain other domains.

### `description`

* `lunar-config.yml -> domains.<domain-path>.description`
* Type: `string`
* Optional

A description of the domain.

### `owner`

* `lunar-config.yml -> domains.<domain-path>.owner`
* Type: `string`
* Optional

The email address of the owner of the domain.

### `meta`

* `lunar-config.yml -> domains.<domain-path>.meta`
* Type: `object`
* Optional

A key-value store of arbitrary metadata for the domain. This metadata is not used by Lunar, but can be used by collectors and policies.
