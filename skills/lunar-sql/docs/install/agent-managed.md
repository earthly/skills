---
description: Use the Lunar CI Action to instrument GitHub-hosted and self-hosted GitHub Actions runners with the Lunar CI Agent.
---

# Lunar CI Action (GitHub Actions)

The Lunar CI Action is the easiest way to add the Lunar CI Agent to your GitHub Actions workflows. It works with both **GitHub-hosted** and **self-hosted** runners.

For **GitHub-hosted runners** (managed runners), this action is the only installation method — you cannot modify the runner startup process.

For **self-hosted runners**, you can either use this action or configure the agent to [wrap the runner's `run.sh` command](agent-self-hosted.md) directly, which avoids adding a step to every job.

## Setup

Add the Lunar CI Action as an early step in your workflow jobs:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Run Lunar CI Agent
        uses: earthly/lunar-ci-action@<latest-tag>
        env:
          LUNAR_HUB_TOKEN: ${{ secrets.LUNAR_HUB_TOKEN }}
          LUNAR_HUB_HOST: your_hub_host

      - uses: actions/checkout@v4
      # ... rest of your workflow
```

The action downloads the Lunar CI Agent, then attaches the agent to the job process. All subsequent steps in the job are automatically instrumented.

## How It Works

The action runs as a step in a job. It attaches to the current shell process via ptrace and traces all commands executed by subsequent steps. The agent exits automatically when the job completes.

The same [configuration reference](agent-config.md) applies. The only difference is that `LUNAR_RUN_CMD` is not needed — the action handles process supervision internally.