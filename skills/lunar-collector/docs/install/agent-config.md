## CI Agent Configuration Reference

### Required

| Variable | Description |
|---|---|
| `LUNAR_HUB_TOKEN` | Auth token for your Hub installation. |
| `LUNAR_HUB_HOST` | Hostname of your Hub installation. Must be reachable from the runner. |
| `LUNAR_HUB_GRPC_PORT` | Hub's gRPC port. Used for configuration sync, collection results, and GitHub token resolution. |
| `LUNAR_HUB_HTTP_PORT` | Hub's HTTP port. Used for log uploads and script downloads. |
| `LUNAR_CI_TYPE` | CI platform type. Currently only `github` is supported. |
| `LUNAR_RUN_CMD` | Command to start the runner process. For GitHub Actions self-hosted runners, this is the path to `run.sh` (e.g. `/home/ubuntu/actions-runner/run.sh`). Not needed when using the [managed runners](agent-managed.md) GitHub Action. |

### Optional

| Variable | Default | Description |
|---|---|---|
| `LUNAR_HUB_INSECURE` | `false` | Set to `true` when connecting to a Hub instance without TLS. |
| `LUNAR_UPDATE_PERIOD` | `15s` | How often the agent polls Hub for configuration updates. |
| `LUNAR_LOG_LEVEL` | `info` | Log verbosity. Set to `debug` for troubleshooting. |
| `LUNAR_GIT_BASE_URL` | _(none)_ | GitHub API base URL. Required for GitHub Enterprise Server installations. |

### Advanced

#### Docker

These options are for environments where collectors or policies run in Docker containers (e.g. private registries, custom networks, or sidecar Docker daemons).

| Variable | Default | Description |
|---|---|---|
| `LUNAR_DOCKER_REGISTRY_USER` | _(none)_ | Username for a private Docker registry containing collector/policy images. |
| `LUNAR_DOCKER_REGISTRY_PASS` | _(none)_ | Password for a private Docker registry containing collector/policy images. |
| `LUNAR_DOCKER_NETWORK` | _(none)_ | Docker network for script container execution. |

#### State Directories

The agent uses several directories for state, caching, and execution. The defaults require root access. To run as a non-root user, override these to user-writable paths (e.g. under `$HOME/.lunar/`).

| Variable | Default | Description |
|---|---|---|
| `LUNAR_STATE_DIR` | `/var/lib/lunar` | Script execution state and embedded runtimes. |
| `LUNAR_GIT_CACHE_DIR` | `/var/cache/lunar/git-repos` | Cached git repository clones. |
| `LUNAR_BUNDLE_DIR` | `/var/tmp/lunar/bundles` | Component JSON bundles for policy evaluation. |
| `LUNAR_SNIPPET_DIR` | `/var/lib/lunar/snippets` | Downloaded script code from Hub. |
| `LUNAR_SCRIPT_LOG_DIR` | `/var/tmp/lunar/scripts` | Script execution logs (uploaded to Hub). |
| `LUNAR_BIN_DIR` | `/usr/lib/lunar` | Embedded runtime binaries. |
| `LUNAR_LOCK_DIR` | `/run/lock/lunar` | Installation lock files to prevent parallel installs. |
