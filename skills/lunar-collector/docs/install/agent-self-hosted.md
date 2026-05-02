---
description: Install the Lunar CI Agent on self-hosted runners to instrument CI/CD pipelines and collect metadata during builds, tests, scans, and deploys.
---

# Installing the Lunar CI Agent

The Lunar CI Agent instruments CI/CD pipelines to collect metadata during builds, tests, scans, and deployments. It wraps your existing runner process, monitors execution, and triggers scripts at the right moments.

This page covers the most common setup: **self-hosted runners** (including GitHub Actions self-hosted runners). If you're using GitHub-hosted managed runners, see [Managed Runners](agent-managed.md).

## Prerequisites

You need an existing self-hosted runner infrastructure (e.g. GitHub Actions self-hosted runner). Lunar adds instrumentation on top of your existing setup — it does not manage the runner lifecycle.

## Adding to an Existing Runner

{% stepper %}
{% step %}
## Download and install the Lunar CLI and CI Agent

<a href="https://github.com/earthly/lunar-dist/releases/latest" class="button primary" data-icon="download">Download the Lunar CLI</a>

Or via the command line:

```bash
curl -LO https://github.com/earthly/lunar-dist/releases/download/v1.1.1/lunar-linux-amd64
chmod +x lunar-linux-amd64 && sudo mv lunar-linux-amd64 /usr/local/bin/lunar
```

<a href="https://github.com/earthly/lunar-ci-agent-dist/releases/latest" class="button primary" data-icon="download">Download the Lunar CI Agent</a>

Or via the command line:

```bash
curl -LO https://github.com/earthly/lunar-ci-agent-dist/releases/download/v1.1.2/lunar-ci-agent-linux-amd64
chmod +x lunar-ci-agent-linux-amd64 && sudo mv lunar-ci-agent-linux-amd64 /usr/local/bin/lunar-ci-agent
```

{% hint style="info" %}
Replace the versions above with the latest from the releases pages.
{% endhint %}
{% endstep %}

{% step %}
## Set the required environment variables

```bash
export LUNAR_CI_TYPE=github
export LUNAR_HUB_TOKEN=your_hub_token
export LUNAR_HUB_HOST=your_hub_host
export LUNAR_HUB_GRPC_PORT=your_grpc_port
export LUNAR_HUB_HTTP_PORT=your_http_port
export LUNAR_RUN_CMD=path_to_github_runner_run.sh

# State directories (need to be set for non-root)
export LUNAR_STATE_DIR=$HOME/.lunar/state
export LUNAR_GIT_CACHE_DIR=$HOME/.lunar/git-cache
export LUNAR_BUNDLE_DIR=$HOME/.lunar/bundles
export LUNAR_SNIPPET_DIR=$HOME/.lunar/snippets
export LUNAR_SCRIPT_LOG_DIR=$HOME/.lunar/scripts
export LUNAR_BIN_DIR=$HOME/.lunar/bin
export LUNAR_LOCK_DIR=$HOME/.lunar/lock
```
{% endstep %}

{% step %}
## Start the agent

```bash
lunar-ci-agent
```

{% hint style="info" %}
For production usage, run `lunar-ci-agent` under a process supervisor such as `systemd` so it restarts automatically on failure. See [Systemd Configuration](systemd.md) for an example unit file.
{% endhint %}
{% endstep %}
{% endstepper %}

## Using a Custom Runner Image

If your runners are containerized, follow the same installation steps inside a `Dockerfile` and override the entrypoint with the agent binary:

{% code title="Dockerfile" %}
```Dockerfile
FROM my-custom-runner-image:ubuntu-slim

ENV LUNAR_HUB_HOST=my.cool.host.com
ENV LUNAR_HUB_GRPC_PORT=443
ENV LUNAR_HUB_HTTP_PORT=443
ENV LUNAR_CI_TYPE=github
ENV LUNAR_RUN_CMD=/home/ubuntu/actions-runner/run.sh

# Replace /home/ubuntu with your runner user's home directory
ENV LUNAR_STATE_DIR=/home/ubuntu/.lunar/state
ENV LUNAR_GIT_CACHE_DIR=/home/ubuntu/.lunar/git-cache
ENV LUNAR_BUNDLE_DIR=/home/ubuntu/.lunar/bundles
ENV LUNAR_SNIPPET_DIR=/home/ubuntu/.lunar/snippets
ENV LUNAR_SCRIPT_LOG_DIR=/home/ubuntu/.lunar/scripts
ENV LUNAR_BIN_DIR=/home/ubuntu/.lunar/bin
ENV LUNAR_LOCK_DIR=/home/ubuntu/.lunar/lock

RUN curl -LO https://github.com/earthly/lunar-dist/releases/download/v1.1.1/lunar-linux-amd64 && \
    chmod +x lunar-linux-amd64 && mv lunar-linux-amd64 /usr/local/bin/lunar

RUN curl -LO https://github.com/earthly/lunar-ci-agent-dist/releases/download/v1.1.2/lunar-ci-agent-linux-amd64 && \
    chmod +x lunar-ci-agent-linux-amd64 && mv lunar-ci-agent-linux-amd64 /usr/local/bin/lunar-ci-agent

ENTRYPOINT ["lunar-ci-agent"]
```
{% endcode %}

{% hint style="info" %}
The GitHub Actions runner may not work correctly when run as root. See GitHub's [self-hosted runner documentation](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners) for details.
{% endhint %}

Bake everything into the image except secrets. Pass the Hub token at runtime:

```bash
docker run -e LUNAR_HUB_TOKEN=$(vault read /lunar/hub/token) runner-image:latest
```

Or in Kubernetes, reference a Secret:

```yaml
env:
  - name: LUNAR_HUB_TOKEN
    valueFrom:
      secretKeyRef:
        name: lunar-hub
        key: token
```

For all environment variable details, see the [Configuration Reference](agent-config.md).

---

## Next Steps

Once installed, you can begin configuring:

- [Collectors](../lunar-config/collectors.md) to gather SDLC data
- [Policies](../lunar-config/policies.md) to enforce standards
- [Domains and Components](../key-concepts/key-concepts.md) to organize your software landscape

For questions or enterprise onboarding:

<a href="https://earthly.dev/earthly-lunar/demo" class="button secondary" data-icon="envelope">Contact the Earthly team</a>
