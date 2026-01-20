# Targets and Artifacts

Understanding how targets, artifacts, and images work together is key to writing effective Earthfiles.

## Targets

A target is a named collection of build commands that produces a build environment. Targets can output:
- **Artifacts** - files that can be copied by other targets or output locally
- **Images** - Docker images that can be loaded locally or pushed to registries

### Target Naming

```Earthfile
# Lowercase with hyphens
build-frontend:
    ...

# Can include numbers
build-v2:
    ...
```

### Target References

| Reference | Description |
|-----------|-------------|
| `+build` | Target in same Earthfile |
| `./subdir+build` | Target in subdirectory |
| `../other+build` | Target in parent directory |
| `github.com/org/repo+build` | Remote target |
| `github.com/org/repo:v1.0+build` | Remote target at tag |

### Base Target

Every Earthfile has an implicit `+base` target. All other targets inherit from it.

```Earthfile
VERSION 0.8
FROM golang:1.21      # These commands form +base
WORKDIR /app

build:                # Implicitly: FROM +base
    COPY . .
    RUN go build
```

## Artifacts

Artifacts are files or directories saved from a target's build environment.

### Creating Artifacts

```Earthfile
build:
    RUN gcc -o app main.c
    SAVE ARTIFACT ./app           # Save to artifact environment
    SAVE ARTIFACT ./app /bin/app  # Save with different path
```

### Using Artifacts

```Earthfile
docker:
    COPY +build/app ./           # Copy from +build target
    COPY +build/bin/app ./app    # Artifact paths work like file paths
```

### Local Output

```Earthfile
build:
    RUN go build -o app
    SAVE ARTIFACT app AS LOCAL ./output/app  # Also write to host
```

**Important:** Local artifacts are only output when:
1. The target is built directly: `earthly +build`
2. Or connected via `BUILD` chain to the main target

### Artifact References

```
+target/path/to/file      # Artifact from same Earthfile
./dir+target/file         # From different Earthfile
(+target/file --arg=val)  # With build args
```

## Images

### Saving Images

```Earthfile
docker:
    FROM alpine:3.18
    COPY +build/app /usr/local/bin/
    ENTRYPOINT ["/usr/local/bin/app"]
    SAVE IMAGE my-app:latest                     # Local name
    SAVE IMAGE my-app:latest my-app:v1.0         # Multiple names
    SAVE IMAGE --push registry.io/my-app:latest  # Push to registry
```

### Image Output

Images are output when:
1. The target is built directly: `earthly +docker`
2. Or connected via `BUILD` chain

```Earthfile
all:
    BUILD +docker     # This causes +docker's image to be output
    BUILD +test       # +test is run but doesn't affect +docker's output
```

### Pushing Images

```bash
# Images with --push are only pushed when --push flag is used
earthly --push +docker
```

## The BUILD Command

`BUILD` invokes another target and connects it to the output chain.

```Earthfile
all:
    BUILD +test
    BUILD +docker
    BUILD +deploy
```

### BUILD vs COPY/FROM

| Command | Runs Target | Output Connected | Inherits Environment |
|---------|-------------|------------------|---------------------|
| `BUILD +target` | Yes | Yes | No |
| `COPY +target/file` | Yes | No | No |
| `FROM +target` | Yes | No | Yes |

### Example: Output Chain

```Earthfile
all:
    BUILD +test
    BUILD +docker

test:
    COPY +build/app ./
    RUN ./test.sh

build:
    RUN go build -o app
    SAVE ARTIFACT app
    SAVE ARTIFACT app AS LOCAL ./output/app  # Won't output! Not in BUILD chain

docker:
    COPY +build/app ./
    SAVE IMAGE my-app:latest  # Will output - connected via BUILD +docker
```

To fix the local artifact output:

```Earthfile
all:
    BUILD +build   # Now +build is in the chain
    BUILD +test
    BUILD +docker

build:
    RUN go build -o app
    SAVE ARTIFACT app
    SAVE ARTIFACT app AS LOCAL ./output/app  # Now outputs!
```

## Parallel Execution

Targets run in parallel when they don't depend on each other:

```Earthfile
all:
    BUILD +frontend    # These 3 run in parallel
    BUILD +backend
    BUILD +docs

integration:
    BUILD +all                  # Must wait for +all
    COPY +frontend/dist ./dist  # Declares dependency on +frontend
    ...
```

Multiple COPYs from different targets also parallelize the builds:

```Earthfile
combined:
    COPY +frontend/dist ./frontend    # +frontend and +backend
    COPY +backend/api ./backend       # build in parallel
```

## Passing Build Args

### To Targets

```Earthfile
build:
    ARG VERSION=dev
    RUN echo "Building $VERSION"

all:
    BUILD +build --VERSION=1.0.0
```

### To Artifacts

```Earthfile
docker:
    COPY (+build/app --VERSION=1.0.0) ./
```

### Pass-through

Within the same Earthfile, args are automatically passed:

```Earthfile
all:
    ARG VERSION
    BUILD +build  # $VERSION is automatically passed

build:
    ARG VERSION
    RUN echo $VERSION
```

For external targets, use `--pass-args`:

```Earthfile
all:
    ARG VERSION
    BUILD --pass-args ./other+build
```

## Multi-Platform Builds

### Building for Multiple Platforms

```Earthfile
all-platforms:
    BUILD --platform=linux/amd64 --platform=linux/arm64 +build
```

### Platform-Specific Logic

```Earthfile
build:
    ARG TARGETPLATFORM
    ARG TARGETARCH
    IF [ "$TARGETARCH" = "arm64" ]
        RUN echo "Building for ARM"
    ELSE
        RUN echo "Building for x86"
    END
```

### Built-in Platform Args

| Arg | Example |
|-----|---------|
| `TARGETPLATFORM` | `linux/arm64` |
| `TARGETOS` | `linux` |
| `TARGETARCH` | `arm64` |
| `TARGETVARIANT` | `v8` |

## Next Steps

- [functions-and-imports.md](functions-and-imports.md) - Reusable code
- [docker-in-earthly.md](docker-in-earthly.md) - WITH DOCKER for integration tests
- [docs/guides/importing.md](../docs/guides/importing.md) - Complete importing guide
