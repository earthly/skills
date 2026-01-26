# Getting Started with Lunar

This guide will help you understand the basic concepts of Lunar and get started with monitoring your engineering practices.

## Prerequisites

Before you begin, make sure you have:

1. Installed Lunar following the [installation guide](../install/install.md)
2. Access to your code repositories
3. Basic understanding of your CI/CD pipeline setup

## Basic Concepts

Lunar operates on a few key concepts:

1. **Components**: These are your software projects (services, libraries, repositories)
2. **Collectors**: These gather information about your components
3. **Policies**: These define rules and standards for your components
4. **Checks**: These are the results of policy evaluations

## Your First Lunar Setup

### 1. Populate your Lunar Configuration

Start by creating a `lunar-config.yml` file in your project root:

```yaml
hub:
  host: <host>:<port>

# Use the official Lunar image for running scripts in containers
default_image: earthly/lunar-scripts:1.0.0

domains:
  team1:
    name: My Organization
    description: Main organization domain

components:
  github.com/my-org/my-service:
    owner: jane@example.com
    domain: team1

collectors:
  - name: readme-lines
    runBash: |-
      if [ -f ./README.md ]; then
        lunar collect -j \
          "repo.readme_exists" true \
          "repo.readme_num_lines" "$(wc -l < ./README.md)"
      else
        lunar collect -j "repo.readme_exists" false
      fi
    hook:
      type: code
```

The `default_image` setting runs all collectors and policies inside Docker containers using the official `earthly/lunar-scripts` image. This image includes Python, Bash, the `lunar` CLI, and the `lunar-policy` package pre-installed. For more details on image configuration, see [Images](../lunar-config/images.md).

You will need to replace `github.com/my-org/my-service` with a real repository you want to monitor.

{% hint style='info' %}
##### Note

Lunar can also auto-discover components from external systems like GitHub, Backstage, and other sources using catalogers. See the [catalogers documentation](../lunar-config/catalogers.md) for details on setting up automated component discovery. For now, this example will focus on manually declared components.
{% endhint %}

Commit this code to a new repository called `lunar`. To apply this configuration, run the following command:

```bash
lunar hub pull -r github.com://my-org/lunar@main
```

You should be able to see the new domain, the new component, and its component JSON being populated in the Lunar UI.

### 2. Define Your First Policy

Add a policy to check your component:

```yaml
policies:
  - name: readme
    description: "README.md standards"
    on: ["domain:team1"]
    runPython: |-
      from lunar_policy import Check
      with Check("readme-exists", "Repository should have a README.md file") as c:
        c.assert_true(c.get(".repo.readme_exists"), "README.md file not found")
```

Since we're using the official `earthly/lunar-scripts` image (via `default_image`), the [Lunar Policy SDK](../python-sdk/policy.md) is already pre-installed—no `requirements.txt` needed.

Commit the code, and apply the new configuration:

```bash
lunar hub pull -r github.com://my-org/lunar@main
```

You should be able to see the new policy, and the checks being populated for this component in the Lunar UI.

Congratulations! You've just set up your first Lunar collector and policy.

## See also

1. Learn more about [key concepts](../key-concepts/key-concepts.md)
2. Explore [configuration options](../lunar-config/lunar-config.md)
3. Install [AI skills](../install/skills.md) for Claude Code, Codex, or Cursor to help build collectors and policies
