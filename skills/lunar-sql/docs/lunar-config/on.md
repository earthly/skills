## Tag Matching with `on`

The `on` field is used by collectors, policies, and initiatives to specify which components they apply to. It supports two forms: an array form for simple matching, and an expression form for complex logic.

### Array Form

The array form accepts a list of tags. A component matches if it has **any** of the specified tags (OR logic):

```yaml
on: [tag1, tag2, tag3]
```

### Expression Form

The expression form accepts a string with `AND`, `OR`, and `NOT` operators for complex matching logic:

```yaml
on: "tag1 OR tag2 AND NOT tag3"
```

Only the keywords `AND`, `OR`, and `NOT` are allowed as operators.

#### Operator Precedence

Operators are evaluated with standard precedence:
1. `NOT` (highest precedence)
2. `AND`
3. `OR` (lowest precedence)

For example:
- `"a OR b AND c"` is evaluated as `"a OR (b AND c)"`
- `"a AND NOT b"` is evaluated as `"a AND (NOT b)"`

### Special Tags

#### Domain Tags

Use `domain:<domain-name>` to match components in a specific domain (and its sub-domains):

```yaml
on: ["domain:engineering"]
```

To match a nested domain, use dot notation:

```yaml
on: ["domain:engineering.payments"]
```

In expression form:

```yaml
on: "domain:engineering AND NOT domain:engineering.experimental"
```

#### Component Tags

Use `component:<component-id>` to match a specific component by its identifier:

```yaml
on: ["component:github.com/foo/bar"]
```

#### Collector Reference

Use `collector:<collector-name>` to apply to the same components that another collector applies to:

```yaml
on: ["collector:foo"]
```

This is useful when you want one collector or policy to follow the same targeting rules as an existing collector.

#### Policy Reference

Use `policy:<policy-name>` to apply to the same components that another policy applies to:

```yaml
on: ["policy:foo"]
```

### Combining Array and Expression Forms

The array form is equivalent to an OR expression. These two are identical:

```yaml
on: [tag1, tag2, tag3]
```

```yaml
on: "tag1 OR tag2 OR tag3"
```

Use the array form for simple OR-based matching, and the expression form when you need AND, NOT, or complex combinations.

### Examples

#### All components in a domain

```yaml
on: ["domain:engineering"]
```

#### Components with specific tags

```yaml
on: [backend, api]
```

#### All components except those with a specific tag

```yaml
on: "NOT internal"
```

Matches all components that do **not** have the `internal` tag.

#### All except a specific component

```yaml
on: "NOT component:github.com/foo/bar"
```

Matches all components except the one specified.

#### Domain with exclusions

```yaml
on: "domain:engineering AND NOT domain:engineering.payments"
```

Matches all components in the `engineering` domain and its sub-domains, **except** those in the `engineering.payments` sub-domain.

#### Include back after exclusion

```yaml
on: "NOT internal OR soc2"
```

This matches:
- All components that are **not** tagged `internal`, OR
- All components tagged `soc2`

This means an `internal` component that is **also** tagged `soc2` **will** be included.

#### Components that must have multiple tags

```yaml
on: "production AND soc2"
```

Matches components that have **both** the `production` and `soc2` tags.

#### Domain filtering with required tag

```yaml
on: "domain:engineering AND NOT domain:engineering.experimental AND production"
```

Matches components that:
1. Are in the `engineering` domain (or its sub-domains)
2. Are **not** in the `engineering.experimental` sub-domain
3. Have the `production` tag

#### Complex targeting across domains

```yaml
on: "domain:engineering.payments OR domain:engineering.api AND soc2"
```

Matches components in `engineering.payments` (regardless of other tags) OR components in `engineering.api` that also have the `soc2` tag.
