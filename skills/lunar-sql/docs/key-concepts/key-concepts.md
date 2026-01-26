
This page describes the most important concepts in Lunar.

At a high-level, your software is organized into components (services or libraries), which often map to code repositories, or subdirectories in monorepos. The engineering processes of each software component in your system is instrumented by collectors. The collectors gather the information into a component JSON. Policies are then defined to create guardrails around your engineering practices. The policies are evaluated against the component JSON and create checks that have a pass or fail outcome.

## Domains

Domains are used to group related components together. Domains are hierarchical and can contain other domains.

Domains are useful to model complex inter-related systems, like multi-service applications, or hierarchical teams in large organizations.

## Components

Components are the building blocks of Lunar. They represent the entities that Lunar monitors. Components are independent pieces of software, such as microservices, or libraries.

Components usually correspond to git repositories, but they may also correspond to subdirectories in a monorepo.

## Component JSON

The Component JSON is an object that contains collected SDLC (software development lifecycle) metadata about a component. Collectors associated with a component contribute to the component JSON metadata via "metadata deltas". Together, all these deltas form a complete picture of the component in a merged JSON representation.

Examples of information that can be collected include:

* Project configuration information
* Project ownership information
* Code access control and branch protection configuration
* Detailed build and test status, including coverage reports
* Security scan results
* Software bill of materials (SBOM)
* Software composition analysis (SCA) results
* Infrastructure information
* Production deliverables and their metadata

For more information about the component JSON, see the [Component JSON](./component-json.md) page.

## Collectors

Collectors are SDLC (software development lifecycle) instrumentation configurations. They are used to collect live information from the SDLC to associate with individual components.

Collectors are of different **types** that vary depending on the **hook** used. They can be based on code, cron schedules, or CI/CD hooks.

Once a hook is triggered, the collector **executes its custom logic**, which collects data from the SDLC. The data is later on merged to form the component metadata JSON.

Collectors may execute in different **contexts**, depending on the type - for example, in the context of a CI pipeline, or standalone in an ephemeral runner reacting to code changes. The Lunar CI Agent and the Lunar Runner are some of the pieces of the Lunar framework that facilitate the triggering and executions of collectors in such contexts.

To read more about how to configure collectors, see the [Collectors](../lunar-config/collectors.md) page.

### Earthly Lunar CI Agent

The Earthly Lunar CI Agent allows you to trigger and execute collectors related to CI/CD pipelines running on a CI runner. The agent is installed on the self-hosted runner of the CI (e.g. GitHub Actions, GitLab CI, Jenkins, Buildkite) and is responsible for instrumenting the pipelines executing on that host and running arbitrary logic defined by relevant collectors.

Installation on managed CI runners is also possible, although it requires additional setup in each project via the definition of the CI pipelines (typically the YAML definition). Earthly Lunar comes out of the box with policies to verify that the agent is installed properly in such situations.

The Lunar CI Agent is able to instrument individual processes executing within CI pipelines and is able to surgically inject custom logic safely in a way that does not interfere with the CI pipeline's normal execution. Special hooks are defined to trigger collectors to execute the in the context of specific processes, no matter how deep in the process tree hierarchy these appear.

### Earthly Lunar Runner

The Earthly Lunar Runner is a standalone ephemeral runner that can be used to execute code-based or cron-based collectors.

You can think of the Lunar Runner as "global CI" where the logic is defined centrally via the Lunar configuration, and not specified within each project's CI pipeline definition. This allows a central platform team to collect information about the entire organization's codebases, running arbitrary logic, and using arbitrary scanners, tools, and scripts, without needing to modify each project's CI pipeline or needing to request permission from individual app teams.

## Policies

Policies are used to define the rules that Lunar uses to evaluate the health of components. Policies receive the component metadata as input and return checks. The checks can then be reported to a scorecarding system or monitored via the Lunar UI.

Some policies may help provide immediate feedback to developers via the PR status. In such a situation, Lunar typically shows up as a commit status check entry in the PR (similarly to how a CI might report status in a PR), showing the health of the component based on the policies.

Similarly, policies can also be used to block deployments based on the health of the component. This is useful to prevent deploying components that do not meet certain engineering standards of the organization.

For more information on how to configure policies, see the [Policies](../lunar-config/policies.md) page.

## Checks

Checks are the results of evaluating a policy against a component. You can think of Lunar checks as individual line item policies that appear in the final scorecard of a component.

Checks might have different outcomes, such as:

* `pass` - the policy check passes successfully
* `fail` - the policy check is failing
* `pending` - the data required by the policy check is still pending (e.g. a collector has not finished executing yet)
* `error` - the policy check failed due to an error in the policy itself

## Catalogers

Catalogers are used to synchronize component and/or domain data from external systems, such as other code repositories, databases, REST APIs, or IDPs, such as Backstage.

To read more about how to configure catalogers, see the [Catalogers](../lunar-config/catalogers.md) page.

## Catalog JSON

The Catalog JSON is an object that contains the component and domain data collected by the catalogers.

To read more about the Catalog JSON, see the [Catalog JSON](./catalog-json.md) page.
