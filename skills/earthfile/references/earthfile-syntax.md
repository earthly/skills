# Earthfile Syntax Reference

This is a summary of the most important Earthfile commands. For the complete reference, see [docs/earthfile/earthfile.md](../docs/earthfile/earthfile.md).

## VERSION

**Required first line** of every Earthfile.

```Earthfile
VERSION 0.8
```

Can include feature flags for experimental features:
```Earthfile
VERSION --try 0.8
```

## FROM

Initialize build environment with a base image or another target.

```Earthfile
# From Docker image
FROM alpine:3.18

# From another target (inherits its filesystem)
FROM +build

# From another Earthfile
FROM ./subdir+target

# From remote repository
FROM github.com/earthly/earthly:v0.8.13+earthly

# With platform
FROM --platform=linux/arm64 alpine:3.18

# With build args
FROM +target --ARG=value
```

## RUN

Execute a command in the build environment.

```Earthfile
# Shell form
RUN echo "Hello World"

# Exec form
RUN ["echo", "Hello World"]

# Multi-line
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# With secret (not stored in layer)
RUN --secret MY_TOKEN curl -H "Authorization: $MY_TOKEN" https://api.example.com

# Push command (only runs with --push flag)
RUN --push ./deploy.sh

# No cache (always re-runs)
RUN --no-cache date

# Privileged mode
RUN --privileged docker info

# With cache mount
RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt

# With SSH agent forwarding
RUN --ssh git clone git@github.com:private/repo.git
```

### RUN Options

| Option | Description |
|--------|-------------|
| `--push` | Only execute when `earthly --push` |
| `--no-cache` | Never cache this command |
| `--privileged` | Run with elevated privileges |
| `--secret KEY` | Make secret available as env var |
| `--ssh` | Forward SSH agent |
| `--mount type=cache,target=PATH` | Persistent cache mount |
| `--mount type=secret,id=ID,target=PATH` | Mount secret as file |
| `--entrypoint` | Prepend image entrypoint |
| `--interactive` | Open interactive shell |

## COPY

Copy files from build context or from other targets.

```Earthfile
# From build context
COPY src ./src
COPY *.go ./

# From another target (artifact form)
COPY +build/app ./
COPY +build/output/* ./dist/

# With build args
COPY (+build/app --VERSION=1.0) ./

# Copy directories themselves (not just contents)
COPY --dir dir1 dir2 dir3 ./

# Preserve timestamps
COPY --keep-ts src ./src

# Only if exists
COPY --if-exists optional-file.txt ./

# Set permissions
COPY --chmod=0755 script.sh ./
```

## ARG

Declare a build argument.

```Earthfile
# With default value
ARG VERSION=latest

# Dynamic default (from shell command)
ARG GIT_SHA=$(git rev-parse HEAD)

# Required (must be provided)
ARG --required API_KEY

# Global (available to all targets)
ARG --global DEBUG=false

# Use in commands
RUN echo "Building version $VERSION"
```

### Passing ARGs

```bash
# From command line
earthly +build --VERSION=1.0.0

# From environment
export EARTHLY_BUILD_ARGS="VERSION=1.0.0,DEBUG=true"
earthly +build

# From .arg file
echo "VERSION=1.0.0" > .arg
earthly +build
```

## LET / SET

Declare and modify local variables (cannot be overridden from outside).

```Earthfile
build:
    LET flags = "--release"
    IF [ "$DEBUG" = "true" ]
        SET flags = "--debug"
    END
    RUN cargo build $flags
```

## SAVE ARTIFACT

Export files from the build environment.

```Earthfile
# Save to artifact environment (can be copied by other targets)
SAVE ARTIFACT ./app

# Save to artifact with different path
SAVE ARTIFACT ./build/app /app

# Also output locally
SAVE ARTIFACT ./app AS LOCAL ./output/app

# Only if exists
SAVE ARTIFACT --if-exists ./optional.txt
```

## SAVE IMAGE

Export the current build environment as a Docker image.

```Earthfile
# Save with name
SAVE IMAGE my-app:latest

# Multiple names
SAVE IMAGE my-app:latest my-app:v1.0.0

# Push to registry (requires --push flag)
SAVE IMAGE --push docker.io/myuser/my-app:latest

# Without manifest list (for platforms that don't support it)
SAVE IMAGE --no-manifest-list my-app:latest
```

## BUILD

Invoke another target.

```Earthfile
# Build another target
BUILD +test

# With arguments
BUILD +build --VERSION=1.0.0

# Multiple platforms
BUILD --platform=linux/amd64 --platform=linux/arm64 +build

# Pass all args to target
BUILD --pass-args +build

# Auto-skip if unchanged
BUILD --auto-skip +build
```

## WORKDIR

Set the working directory.

```Earthfile
WORKDIR /app
WORKDIR ./subdir  # Relative to current
```

## ENV

Set environment variable (persists in final image).

```Earthfile
ENV NODE_ENV=production
ENV PATH="/app/bin:$PATH"
```

## ENTRYPOINT / CMD

Set the image entrypoint and default command.

```Earthfile
ENTRYPOINT ["./app"]
CMD ["--help"]

# Or shell form
ENTRYPOINT ./app
CMD --help
```

## EXPOSE / LABEL / USER / VOLUME

Standard Dockerfile commands work the same way.

```Earthfile
EXPOSE 8080
LABEL version="1.0"
USER nobody
VOLUME /data
```

## GIT CLONE

Clone a git repository (cache-aware).

```Earthfile
GIT CLONE https://github.com/example/repo.git ./repo
GIT CLONE --branch=v1.0.0 git@github.com:example/repo.git ./repo
```

## IF / ELSE

Conditional execution.

```Earthfile
ARG DEBUG=false
IF [ "$DEBUG" = "true" ]
    RUN echo "Debug mode"
ELSE IF [ -f ./config.yml ]
    RUN echo "Config exists"
ELSE
    RUN echo "Production mode"
END
```

## FOR

Iterate over a list.

```Earthfile
FOR dir IN $(ls -d */)
    BUILD "./$dir+build"
END

FOR lang IN go python rust
    RUN echo "Building $lang"
END
```

## WAIT

Wait for all enclosed operations to complete before continuing.

```Earthfile
WAIT
    BUILD +push-image-1
    BUILD +push-image-2
END
RUN ./notify-deployment.sh
```

## IMPORT

Import an Earthfile for easier referencing.

```Earthfile
IMPORT github.com/earthly/lib AS lib
IMPORT ./subdir AS sub

build:
    DO lib+INSTALL_DIND
    BUILD sub+compile
```

## FUNCTION / DO

Define and call reusable functions.

```Earthfile
# Define (ALL_CAPS name)
GO_COMPILE:
    FUNCTION
    ARG package
    ARG output
    RUN go build -o "$output" "$package"
    SAVE ARTIFACT "$output"

# Call
build:
    FROM golang:1.21
    COPY . .
    DO +GO_COMPILE --package=./cmd/app --output=app
```

## LOCALLY

Execute on the host machine (not in container). Use sparingly.

```Earthfile
dev-setup:
    LOCALLY
    RUN npm install
```

## CACHE

Create a persistent cache directory.

```Earthfile
build:
    CACHE /root/.cache/go-build
    RUN go build ./...
```

## FROM DOCKERFILE

Build from an existing Dockerfile.

```Earthfile
docker:
    FROM DOCKERFILE .
    SAVE IMAGE my-app:latest

# With specific file
docker:
    FROM DOCKERFILE -f ./docker/Dockerfile.prod .
```

## HOST

Add an entry to /etc/hosts.

```Earthfile
HOST myservice 127.0.0.1
```

## Next Steps

- [targets-and-artifacts.md](targets-and-artifacts.md) - How targets and artifacts work together
- [functions-and-imports.md](functions-and-imports.md) - Reusable code patterns
- [docs/earthfile/earthfile.md](../docs/earthfile/earthfile.md) - Complete reference
- [docs/earthfile/builtin-args.md](../docs/earthfile/builtin-args.md) - Built-in arguments
