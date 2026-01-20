
## Component JSON

* Type: `JSON`

The Component JSON is a JSON object that contains SDLC metadata associated with a component. The JSON object is formed by collecting metadata deltas via the different collectors.

The Component JSON is meant to represent the point-in-time state of a component. The JSON object is stored in the database and is used to evaluate the health of the component via policies.

The structure of the component JSON is arbitrary. The JSON object acts as an interface layer between the collectors and the policies. It can have any structure, as needed to convey the information used by the policies, or to track the state of a certain metric or characteristic over time for a given component or set of components.

To view the component JSON for a given component, you can use the `lunar component get-json` command:

```bash
lunar component get-json github.com/my-org/my-repo
```

To read more about how to configure the collectors that contribute deltas to the component JSON, see the [collectors](../lunar-config/collectors.md) page.

To read more about how to query the component JSONs via the SQL API see the [components view](../sql-api/views/components.md) page.
