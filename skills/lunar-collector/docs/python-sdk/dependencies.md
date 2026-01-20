# Installing dependencies

If your policy requires dependencies, you have two options depending on your execution environment:

1. **Custom Docker image** - Install dependencies at build time in your Dockerfile
2. **Native execution** - Dependencies are installed automatically at runtime

Your `requirements.txt` should contain the `lunar_policy` package at a minimum:

```txt
lunar_policy==0.1.6
```

## Custom Docker Image

When running in containers, create a custom Docker image with all dependencies pre-installed. This provides faster startup times, reproducible builds, and eliminates network dependencies at runtime.

Create a Dockerfile that inherits from the official `earthly/lunar-scripts` image and installs your dependencies at build time:

```dockerfile
FROM earthly/lunar-scripts:1.0.0

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
```

Then configure your plugin or `lunar-config.yml` to use this image:

```yaml
image: my-org/my-custom-image:v1.0
```

For more details on image configuration, see [Images](../lunar-config/images.md).

## Native Execution

When running with `image: native` (no container), place your `requirements.txt` in the same directory as your `lunar-config.yml` or `lunar-policy.yml` file. Dependencies are installed automatically before the policy is run, and only once in each environment.

## Development convenience with `earthly/lunar-scripts`

The official `earthly/lunar-scripts` image automatically installs dependencies from any `requirements.txt` file found in the plugin directory as part of its entrypoint. This is a convenience feature for quick development iteration, but baking dependencies into your image provides faster startup times in production.

To override this behavior, you can change the `ENTRYPOINT` in your Dockerfile. For example:

```dockerfile
ENTRYPOINT ["/usr/bin/python3"]
```
