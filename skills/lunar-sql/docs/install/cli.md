---
description: Install the Lunar CLI for managing configurations, inspecting components, running collectors, and testing policies locally.
---

# Installing Lunar CLI

The Lunar CLI is primarily an administration tool for platform engineers, with developer-focused capabilities secondarily. It uses the same `lunar` binary as the CI agent but provides different subcommands for interactive CLI usage versus CI instrumentation. It can be used to manage configurations, inspect components, run collectors, and test policies.

## Prerequisites

**Docker** is required for local development commands since collectors and policies run inside containers.

{% hint style="info" %}
**macOS Users:** If using Docker Desktop, you must enable the default Docker socket. Go to **Docker Desktop → Settings → Advanced** and enable **"Allow the default Docker socket to be used"**, then click **Apply & Restart**.
{% endhint %}

## Installation

{% stepper %}
{% step %}
## Download the binary

<a href="https://github.com/earthly/lunar-dist/releases" class="button primary" data-icon="download">Download the Lunar CLI</a>
{% endstep %}

{% step %}
## Move the binary into place

Move the binary to the `~/.lunar/bin` directory:

```bash
chmod +x lunar-linux-amd64 && mv ./lunar-linux-amd64 "$HOME/.lunar/bin/lunar"
```

If you prefer to install `lunar` to a different directory, you must set the `LUNAR_BIN_DIR` environment variable to the desired path (see below).
{% endstep %}

{% step %}
## Set environment variables

```bash
# Required
export LUNAR_HUB_TOKEN=your_hub_token
export LUNAR_HUB_HOST=your_hub_host
export LUNAR_HUB_GRPC_PORT=your_grpc_port
export LUNAR_HUB_HTTP_PORT=your_http_port
export PATH="$HOME/.lunar/bin:$PATH"

# Optional, if you want to override the default bin dir
export LUNAR_BIN_DIR="$HOME/.lunar/bin"
```
{% endstep %}

{% step %}
## Verify installation

```bash
lunar --help
```
{% endstep %}
{% endstepper %}

For usage examples and full CLI documentation, see the [Lunar CLI Docs](../lunar-cli/lunar-cli.md).

---

## Next Steps

Once installed, you can begin configuring:

- [Collectors](../lunar-config/collectors.md) to gather SDLC data
- [Policies](../lunar-config/policies.md) to enforce standards
- [Domains and Components](../key-concepts/key-concepts.md) to organize your software landscape

For questions or enterprise onboarding:

<a href="https://earthly.dev/earthly-lunar/demo" class="button secondary" data-icon="envelope">Contact the Earthly team</a>
