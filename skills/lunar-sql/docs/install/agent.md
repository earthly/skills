## Installing the Lunar CI Agent

The Lunar CI Agent is used to instrument CI/CD pipelines and collect metadata during builds, tests, scans, and deployments. It is typically installed as a step in your CI configuration.

### GitHub Actions (Managed Runners)

To instrument pipelines on GitHub Actions (managed runners), insert the following step in your workflow.

Include the required environment variables for your installation (see below for the full list and their descriptions):

```yaml
- name: Run Lunar CI Agent
  uses: earthly/lunar-ci-action@v1
  env:
    LUNAR_GITHUB_TOKEN: ${{ secrets.LUNAR_GITHUB_TOKEN }}
    LUNAR_HUB_TOKEN: ${{ secrets.LUNAR_HUB_TOKEN }}
    # See below for the full list of environment variables and optional settings
```

### Self-Hosted Runners

For self-hosted runners (including GitHub Actions self-hosted), you'll need to
manually install the Lunar CI Agent from a GitHub release and run it using the
binary `lunar`. Follow these steps:

1. Download the latest release (replace with appropriate download command):

   ```bash
   curl -LO https://github.com/earthly/lunar-dist/releases/download/v1.0.0/lunar-linux-amd64
   ```

2. Move the binary to somewhere on your path and make it executable:

   ```bash
   sudo chmod +x lunar-linux-amd64 && mv ./lunar-linux-amd64 /usr/local/bin/lunar
   ```

3. Set required and optional environment variables:

   The Lunar CI Agent requires several environment variables to function properly. Set them in your environment or in a file:

   ```bash
   # Required
   export LUNAR_GITHUB_TOKEN=your_github_token
   export LUNAR_HUB_TOKEN=your_hub_token
   export LUNAR_HUB_HOST=your_hub_host
   export LUNAR_HUB_GRPC_PORT=your_grpc_port
   export LUNAR_HUB_HTTP_PORT=your_http_port

   # Optional: logs integration
   export LUNAR_ELASTIC_URL=your_elastic_url
   export LUNAR_ELASTIC_API_KEY=your_elastic_api_key
   export LUNAR_TENANT_ID=your_tenant_id

   # Optional (defaults shown)
   export LUNAR_STATE_DIR=/var/lib/lunar
   export LUNAR_LOG_LEVEL=info
   export LUNAR_LOG_FORMAT=json
   export LUNAR_UPDATE_PERIOD=60s
   ```

4. Configure the CI Agent:

   See the [below section](#configuring-the-ci-agent) for full details.

5. Start the Lunar CI Agent:

   ```bash
   LUNAR_RUN_CMD="/path/to/github/runner/run.sh" lunar
   ```

   {% hint style='info' %}
   For production usage, consider running and monitoring the `lunar` process with a process supervisor such as `systemd`. This helps ensure the agent is automatically restarted if it fails. See [the Systemd configuration page](systemd.md) for guidance on creating a unit file.
   {% endhint %}

### GitHub Token Permissions

The agent's GitHub token (`LUNAR_GITHUB_TOKEN`) is used for runner registration,
CI workflow introspection, and fetching snippet configuration. The table below
lists the minimum permissions required.

#### Fine-Grained PAT / GitHub App

| Scope | Level | Purpose |
|---|---|---|
| **Organization: Self-hosted runners** | Write | Register self-hosted runners (`POST /orgs/{org}/actions/runners/registration-token`) |
| **Repository: Actions** | Read | Read workflow run details |
| **Repository: Contents** | Read | Read workflow and action definition files, clone snippet/plugin repos |
| **Repository: Metadata** | Read | Read repository metadata (e.g. default branch) |

{% hint style='info' %}
Contents and Actions read access must cover all repositories referenced by your
workflows (including third-party action repos, if private). Public action
repositories do not require additional permissions.
{% endhint %}

#### Classic PAT

| Scope | Purpose |
|---|---|
| `repo` | Repository contents, actions, and metadata |
| `admin:org` | Organization admin permissions |

### Configuring the CI Agent

The CI Agent will communicate with Hub and update its local copy of the
configuration as updates become available.

---

## Next Steps

Once installed, you can begin configuring:

- [Collectors](../lunar-config/collectors.md) to gather SDLC data
- [Policies](../lunar-config/policies.md) to enforce standards
- [Domains and Components](../key-concepts/key-concepts.md) to organize your software landscape

For questions or enterprise onboarding, [contact the Earthly team](https://earthly.dev/earthly-lunar/demo).
