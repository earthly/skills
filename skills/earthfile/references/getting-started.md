# Getting Started with Earthly

Earthly is a build automation tool that uses Docker containers to enforce build repeatability. It combines the best ideas from Dockerfiles and Makefiles into a single specification.

## Installation

```bash
# macOS
brew install earthly && earthly bootstrap

# Linux
sudo /bin/sh -c 'wget https://github.com/earthly/earthly/releases/latest/download/earthly-linux-amd64 -O /usr/local/bin/earthly && chmod +x /usr/local/bin/earthly && /usr/local/bin/earthly bootstrap'

# Windows (WSL2)
sudo /bin/sh -c 'wget https://github.com/earthly/earthly/releases/latest/download/earthly-linux-amd64 -O /usr/local/bin/earthly && chmod +x /usr/local/bin/earthly && /usr/local/bin/earthly bootstrap'
```

For more installation options, see [docs/install/install.md](../docs/install/install.md).

## Core Concepts

### Earthfile

An Earthfile is a file named `Earthfile` (no extension) that defines your build. It contains:
- A **base recipe** (implicit `+base` target) that all targets inherit from
- **Targets** (like Makefile targets) that can produce artifacts or images
- **Functions** (reusable command sequences)

### Target

A target is a named collection of build steps. Targets are defined with a name followed by a colon:

```Earthfile
my-target:
    RUN echo "Hello from my-target"
```

Targets are invoked with the `+` prefix: `earthly +my-target`

### Artifact

An artifact is a file or directory produced by a target that can be:
- Copied to other targets with `COPY +target/path`
- Output locally with `SAVE ARTIFACT ... AS LOCAL ...`

### Image

A target can produce a Docker image using `SAVE IMAGE`. Images can be:
- Loaded into the local Docker daemon
- Pushed to a registry with `--push`

## Basic Earthfile Example

```Earthfile
VERSION 0.8
FROM python:3.11
WORKDIR /app

deps:
    COPY requirements.txt ./
    RUN pip install -r requirements.txt
    SAVE ARTIFACT /usr/local/lib/python3.11/site-packages /site-packages

build:
    FROM +deps
    COPY src ./src
    SAVE ARTIFACT ./src /src

test:
    FROM +deps
    COPY +build/src ./src
    RUN pytest ./src

docker:
    FROM python:3.11-slim
    COPY +deps/site-packages /usr/local/lib/python3.11/site-packages
    COPY +build/src /app/src
    ENTRYPOINT ["python", "/app/src/main.py"]
    SAVE IMAGE my-python-app:latest
```

## Running Earthly

```bash
# Build a single target
earthly +test

# Build multiple targets
earthly +test +docker

# Build with push (for images with --push flag)
earthly --push +docker

# Pass arguments
earthly +build --VERSION=1.0.0

# Pass secrets
earthly --secret MY_TOKEN=abc123 +deploy

# Interactive debugging on failure
earthly -i +failing-target

# CI mode (strict, no local output)
earthly --ci +test
```

## Key Differences from Dockerfile

| Dockerfile | Earthfile |
|------------|-----------|
| Single build output | Multiple targets, multiple outputs |
| `FROM ... AS stage` | Named targets (`my-target:`) |
| `COPY --from=stage` | `COPY +target/path` |
| Build args scoped globally | `ARG` scoped to target |
| No native parallelism | Automatic parallel execution |
| No native caching control | Cache mounts, layer caching |

## Key Differences from Makefile

| Makefile | Earthfile |
|----------|-----------|
| Runs on host | Runs in container |
| Host-dependent | Repeatable anywhere |
| Tab-sensitive | Not tab-sensitive |
| File-based dependencies | Target-based dependencies |
| Shell commands | Dockerfile-like commands |

## VERSION Command

Every Earthfile must start with a `VERSION` command:

```Earthfile
VERSION 0.8
```

This specifies which version of the Earthfile syntax to use. Different versions enable different features. Current stable version is 0.8.

For version-specific features, see [docs/earthfile/features.md](../docs/earthfile/features.md).

## Next Steps

- [earthfile-syntax.md](earthfile-syntax.md) - Complete command reference
- [targets-and-artifacts.md](targets-and-artifacts.md) - Deep dive into targets and outputs
- [best-practices.md](best-practices.md) - Writing good Earthfiles
- [docs/basics/basics.md](../docs/basics/basics.md) - Full tutorial
