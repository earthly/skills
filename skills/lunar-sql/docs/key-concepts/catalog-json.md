
## Catalog JSON

* Type: `JSON`
* Form:
  ```json
  {
    "domains": {
      "<domain-name>": {
        "description": "<description>",
        "owner": "<owner>",
        "meta": {
          "<meta-key>": "<meta-value>",
          ...
        }
      },
      ...
    },
    "components": {
      "<component-name>": {
        "owner": "<owner>",
        "domain": "<domain>",
        "branch": "<branch>",
        "tags": ["<tag1>", "<tag2>", ...],
        "ciPipelines": ["<ci-pipeline1>", "<ci-pipeline2>", ...],
        "meta": {
          "<meta-key>": "<meta-value>",
          ...
        }
      },
      ...
    }
  }
  ```

The Catalog JSON is a JSON object that contains information about the domains and components.

The Catalog JSON, unlike the Component JSON, has a pre-defined structure. The semantics of the fields are defined in the [domains](../lunar-config/domains.md) and [components](../lunar-config/components.md) pages. The same fields used to configure domains and components in `lunar-config.yml` are used to define the structure of the Catalog JSON.

The JSON object is formed by collecting information from the catalogers, and then merging that information with any data from `lunar.yml` and `lunar-config.yml`. The precedence in which the information is used is as follows:

1. The information from `lunar-config.yml` in the `domains` and `components` section.
2. The information from `lunar.yml` in each component directory.
3. The information from the catalogers, applied in the **reverse order** in which the catalogers are defined in `lunar-config.yml`.

So, for example, if a cataloger emits a component with the same name as a component defined in `lunar-config.yml`, the fields would be combined, and any fields that exist in both would be overridden by the `lunar-config.yml` values.

If you would like to inspect the Catalog JSON, you can do so by running the following command:

```bash
lunar cataloger get-json
```

If you would like to execute the catalogers in development mode, and see the Catalog JSON that would be generated, you can do so by running the following command (needs to be run in the root of the Lunar configuration repository):

```bash
lunar cataloger dev --output-json
```
