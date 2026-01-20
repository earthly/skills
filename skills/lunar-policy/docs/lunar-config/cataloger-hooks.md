
## Cataloger Hook

* `lunar-config.yml -> catalogers.<cataloger-index>.hook`
* `lunar-cataloger.yml -> catalogers.<cataloger-index>.hook`
* Type: `object`
* Form:
  ```yaml
  type: <hook-type>
  <options>
  ```

A cataloger hook defines a trigger point for when a cataloger should run. Catalogers can be triggered by various events such as code changes, or cron schedules.

A hook has different configuration options depending on the type of event it is triggered by.

### Hook types

#### `cron`

* Form:
  ```yaml
  type: cron
  schedule: <cron-schedule>
  ```

The `cron` type triggers the cataloger on a specified schedule. The schedule is defined using a cron expression.

#### `repo`

* Form:
  ```yaml
  type: repo
  repo: github://<org>/<repo>
  ```

The `repo` type triggers the cataloger when a commit is made to a specified repository. The repository is defined using the GitHub URL format. This cataloger type is most useful for centralized repositories that contain information about domains and/or components.

#### `component-repo`

* Form:
  ```yaml
  type: component-repo
  ```

The `component-repo` type triggers the cataloger when a commit is made to a component repository. This cataloger type is most useful when additional information about components is available in each of the respective repositories.

Although this cataloger type cannot be used to define new components, it can be used to augment the metadata (such as owner, description and tags) associated with existing components.
