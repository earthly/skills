
## Images

Lunar supports running collectors, policies, and catalogers inside Docker containers. This provides isolation, reproducibility, and simplifies dependency management. Default images can be configured at multiple levels, with more specific settings overriding more general ones.

## Image Resolution Order

The image used to run a script is determined in the following order (first match wins):

1. **Script-level `image`** - Set directly on the collector, policy, or cataloger
2. **Plugin-level default** - Set in `lunar-collector.yml`, `lunar-policy.yml`, or `lunar-cataloger.yml`
3. **Global default** - Set in `lunar-config.yml`
4. **Implicit default** - `native` (no container)

## Global Default Images

Configure default images in `lunar-config.yml`:

```yaml
version: 0

default_image: my-custom-image:alpine-1.2.3
default_image_ci_collectors: native
default_image_non_ci_collectors: my-image:v1.0
default_image_policies: another-image:latest
default_image_catalogers: yet-another-image:v2.0

# ... rest of configuration
```

### `default_image`

* `lunar-config.yml -> default_image`
* Type: `string`
* Optional
* Default: `native`

The global default image to use for all collectors, policies, and catalogers. This is overridden by the more specific `default_image_*` settings.

### `default_image_ci_collectors`

* `lunar-config.yml -> default_image_ci_collectors`
* Type: `string`
* Optional
* Default: value of `default_image`

The default image for CI collectors (collectors with hooks of type `ci-before-command`, `ci-after-command`, `ci-before-job`, `ci-after-job`). It is common to set this to `native` since CI collectors often need direct access to the CI environment.

### `default_image_non_ci_collectors`

* `lunar-config.yml -> default_image_non_ci_collectors`
* Type: `string`
* Optional
* Default: value of `default_image`

The default image for non-CI collectors (collectors with hooks of type `code`, `cron`).

### `default_image_policies`

* `lunar-config.yml -> default_image_policies`
* Type: `string`
* Optional
* Default: value of `default_image`

The default image for all policies.

### `default_image_catalogers`

* `lunar-config.yml -> default_image_catalogers`
* Type: `string`
* Optional
* Default: value of `default_image`

The default image for all catalogers.

## Plugin-Level Default Images

Plugins can define their own default images that override the global settings. This is useful when a plugin requires specific dependencies that are pre-installed in a custom image.

In `lunar-collector.yml`, `lunar-policy.yml`, or `lunar-cataloger.yml`:

```yaml
version: 0
name: my-plugin
description: A plugin with custom image defaults

default_image: my-org/my-plugin-image:v1.0
default_image_ci_collectors: native
default_image_non_ci_collectors: my-org/my-plugin-image:v1.0
default_image_policies: my-org/my-plugin-image:v1.0
default_image_catalogers: my-org/my-plugin-image:v1.0

# ... rest of plugin configuration
```

The same settings are available as at the global level. Plugin-level defaults override global defaults but are overridden by script-level `image` settings.

## Script-Level Image

Each individual collector, policy, or cataloger can specify its own `image` to override all defaults:

```yaml
collectors:
  - runBash: lunar collect .file-count "$(find . | wc -l)"
    image: earthly/lunar-scripts:1.0.0
    hook:
      type: code
    on: [my-tag]
```

## The `native` Value

The special value `native` explicitly opts out of containerized execution. When `image: native` is set, the script runs directly on the host system using the native runtime (Python, Bash, etc.).

This is useful when:

* A default image has been configured, but a specific script needs to run natively
* CI collectors need direct access to the CI environment
* The script needs access to host-specific resources

## Common Configuration Pattern

A common configuration is to use containers for most scripts but run CI collectors natively:

```yaml
default_image: earthly/lunar-scripts:1.0.0
default_image_ci_collectors: native
```

This configuration:

* Runs all policies in containers
* Runs all catalogers in containers
* Runs non-CI collectors (code, cron, repo hooks) in containers
* Runs CI collectors natively for direct access to CI environment variables and tools

## Official Image: `earthly/lunar-scripts`

Lunar provides an official Docker image `earthly/lunar-scripts` that includes:

* Alpine Linux (or `-debian` variant for tools requiring glibc)
* Python 3 with venv
* Bash
* The `lunar-policy` Python package
* The `lunar` CLI
* Common tools: `jq`, `yq`, `curl`, `parallel`, `wget`

### Dependency Handling

The official `earthly/lunar-scripts` image automatically executes any `requirements.txt` and/or `install.sh` files it finds in the plugin directory as part of its entrypoint. This is a convenience feature to help you get up and running quickly during development.

**For production use, we recommend baking all dependencies directly into your image.** This approach provides:

* Faster startup times (no runtime installation)
* Reproducible builds
* Better caching and smaller attack surface
* Elimination of network dependencies at runtime

### Recommended Approach: Custom Image Inheriting from Official

The recommended approach is to create a custom Dockerfile that inherits from the official `earthly/lunar-scripts` image and installs your dependencies at build time:

```dockerfile
FROM earthly/lunar-scripts:1.0.0

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y jq curl && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy and run install script (if needed)
COPY install.sh /tmp/install.sh
RUN /tmp/install.sh && rm /tmp/install.sh
```

This pattern gives you all the benefits of the official image (Python, Bash, `lunar` CLI, `lunar-policy` package) while ensuring your dependencies are baked in for production use.

### Execution Model

When a script runs inside a container, the execution follows this pattern:

```
<image entrypoint> <main-script>
```

The following directories are mounted into the container:

| Host Path | Container Path | Description |
|-----------|----------------|-------------|
| Plugin directory | `/app/exec` | Where the script and plugin files are located |
| Working directory | `/app/work` | The component's code (for collectors and some catalogers) |

The container's working directory is set to `/app/work`, so your scripts can access the component's files using relative paths. The main script path (e.g., `/app/exec/main.py`) is passed as an argument to the image's entrypoint.

## Private Registry Authentication

To pull images from private Docker registries, configure the following environment variables:

* `LUNAR_DOCKER_REGISTRY_USER` - Username for Docker registry authentication
* `LUNAR_DOCKER_REGISTRY_PASS` - Password or token for Docker registry authentication
