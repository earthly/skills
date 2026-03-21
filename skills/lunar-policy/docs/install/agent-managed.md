## Managed Runners (GitHub Actions)

If your pipelines run on **GitHub-hosted runners** (the default GitHub Actions infrastructure), use the Lunar CI Action instead of installing the agent manually.

### Setup

Add the Lunar CI Action as a step in your workflow:

```yaml
- name: Run Lunar CI Agent
  uses: earthly/lunar-ci-action@v1
  env:
    LUNAR_HUB_TOKEN: ${{ secrets.LUNAR_HUB_TOKEN }}
    LUNAR_HUB_HOST: your_hub_host
    LUNAR_HUB_GRPC_PORT: "443"
    LUNAR_HUB_HTTP_PORT: "443"
    LUNAR_CI_TYPE: github
```

The action installs both the CLI and agent automatically. GitHub API access is handled via the [Earthly Lunar GitHub App](https://github.com/apps/earthly-lunar) installed on your organization.

### How It Works

Unlike self-hosted runners where the agent wraps the runner process, the action runs **within** the workflow. It instruments the job from the inside, triggering collectors and policies at the appropriate points during execution.

The same [configuration reference](agent-config.md) applies. The only difference is that `LUNAR_RUN_CMD` is not needed — the action handles process supervision internally.