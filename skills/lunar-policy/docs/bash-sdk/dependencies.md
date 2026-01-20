# Installing dependencies

If your collector or cataloger requires dependencies, you have two options depending on your execution environment:

1. **Custom Docker image** - Bake dependencies into your image for containerized execution
2. **Install script** - Use `install.sh` for native execution

## Custom Docker Image

When running in containers, create a custom Docker image with all dependencies pre-installed. This provides faster startup times, reproducible builds, and eliminates network dependencies at runtime.

Create a Dockerfile that inherits from the official `earthly/lunar-scripts` image:

```dockerfile
FROM earthly/lunar-scripts:1.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y jq curl && rm -rf /var/lib/apt/lists/*

# Install additional tools
RUN curl -L "https://github.com/keilerkonzept/dockerfile-json/releases/download/v1.2.2/dockerfile-json_Linux_x86_64.tar.gz" | tar xz \
    && mv dockerfile-json /usr/local/bin/
```

Then configure your plugin or `lunar-config.yml` to use this image:

```yaml
image: my-org/my-custom-image:v1.0
```

For more details on image configuration, see [Images](../lunar-config/images.md).

## Install Script for Native Execution

When running with `image: native` (no container), you can install dependencies using an `install.sh` script in the same directory as your `lunar-config.yml`, `lunar-collector.yml` or `lunar-cataloger.yml` file.

This install script is executed only once in each environment, before the collector or cataloger is run.

### Example

```bash
#!/bin/bash
curl -L "https://github.com/keilerkonzept/dockerfile-json/releases/download/v1.2.2/dockerfile-json_Linux_x86_64.tar.gz" | tar xz
mv dockerfile-json "$LUNAR_BIN_DIR/"
```

### Installation path

If you need to install a binary that will be used in the collector or cataloger, you can use the `LUNAR_BIN_DIR` environment variable. This will ensure the binary is available in the `PATH`.

### Multi-platform support

For platform-specific logic, you can use `install-<os>-<arch>.sh` or `install-<os>.sh` files. Making your script multi-platform is useful for local development when your local platform may differ from the one Lunar's runners or your CI is running on.

Platform-specific scripts are checked for existence in the following order:

1. `install-<os>-<arch>.sh`
2. `install-<os>.sh`
3. `install.sh`

Only the first script found is executed.

Examples of valid platform-specific script names:

- `install-linux-amd64.sh`
- `install-linux-arm64.sh`
- `install-linux.sh`
- `install-darwin-arm64.sh`
- `install-darwin.sh`

## Development convenience with `earthly/lunar-scripts`

The official `earthly/lunar-scripts` image automatically executes any `install.sh` script found in the plugin directory as part of its entrypoint. This is a convenience feature for quick development iteration, but baking dependencies into your image provides faster startup times in production.

To override this behavior, you can change the `ENTRYPOINT` in your Dockerfile. For example:

```dockerfile
ENTRYPOINT ["/bin/bash"]
```
