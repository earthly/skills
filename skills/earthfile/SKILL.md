---
name: earthfile
description: Write Earthfiles for repeatable, containerized builds. Use when creating build automation with Earthly - a tool combining Dockerfile and Makefile concepts. Covers targets, artifacts, caching, functions, imports, Docker-in-Docker, CI integration, and best practices.
---

# Earthfile Skill

Write Earthfiles for Earthly - a build automation tool that runs all builds in containers for repeatability. Earthly combines the best ideas from Dockerfiles and Makefiles into a single specification.

**Important:** Earthly is no longer actively maintained and all cloud features (Satellites, cloud secrets, remote runners) are no longer available. This skill focuses on the local/self-hosted Earthly usage.

## Quick Start

1. Read [getting-started.md](references/getting-started.md) for core concepts
2. Read [earthfile-syntax.md](references/earthfile-syntax.md) for command reference
3. Read [best-practices.md](references/best-practices.md) for writing good Earthfiles

## What is Earthly?

Earthly is a CI/CD framework that:
- Runs all builds in containers for **repeatable builds**
- Uses a simple, instantly recognizable **Dockerfile-like syntax**
- Works with **every language, framework, and build tool**
- Executes build targets in **parallel** with **automatic caching**

## Basic Earthfile Structure

```Earthfile
VERSION 0.8
FROM alpine:3.18
WORKDIR /app

# Base recipe (implicit +base target)
# All targets inherit from this

build:
    COPY src ./src
    RUN gcc -o app ./src/main.c
    SAVE ARTIFACT ./app

docker:
    COPY +build/app ./
    ENTRYPOINT ["./app"]
    SAVE IMAGE my-app:latest
```

## Key Commands

| Command | Description |
|---------|-------------|
| `VERSION` | Required first line, specifies Earthly version |
| `FROM` | Set base image or inherit from another target |
| `RUN` | Execute shell command |
| `COPY` | Copy files from context or artifacts from targets |
| `SAVE ARTIFACT` | Export files from build environment |
| `SAVE IMAGE` | Export Docker image |
| `BUILD` | Invoke another target |
| `ARG` | Declare build argument |
| `IF/FOR/WAIT` | Control flow |

## Running Earthly

```bash
# Build a target
earthly +build

# Build with arguments
earthly +build --MY_ARG=value

# Build and push images
earthly --push +docker

# Build with secrets
earthly --secret MY_SECRET=value +target
```

## Reference Documentation

For detailed information, read these files in the `references/` directory:

| File | Content |
|------|---------|
| [getting-started.md](references/getting-started.md) | Core concepts, installation, basic workflow |
| [earthfile-syntax.md](references/earthfile-syntax.md) | Complete command reference (FROM, RUN, COPY, etc.) |
| [targets-and-artifacts.md](references/targets-and-artifacts.md) | Targets, artifacts, images, and outputs |
| [functions-and-imports.md](references/functions-and-imports.md) | Reusable functions, importing across Earthfiles |
| [docker-in-earthly.md](references/docker-in-earthly.md) | WITH DOCKER, integration testing |
| [caching.md](references/caching.md) | Cache optimization, cache mounts |
| [ci-integration.md](references/ci-integration.md) | Using Earthly in CI systems |
| [best-practices.md](references/best-practices.md) | Patterns, anti-patterns, optimization tips |

## Full Documentation

For comprehensive documentation, see the [docs/SUMMARY.md](docs/SUMMARY.md) table of contents, which links to:

- Complete Earthfile reference
- Built-in args
- Configuration reference
- Language-specific guides
- CI vendor guides (GitHub Actions, GitLab, Jenkins, etc.)

## Common Patterns

### Multi-stage Build

```Earthfile
VERSION 0.8

deps:
    FROM golang:1.21
    COPY go.mod go.sum ./
    RUN go mod download

build:
    FROM +deps
    COPY . .
    RUN go build -o app ./cmd/main.go
    SAVE ARTIFACT app

docker:
    FROM alpine:3.18
    COPY +build/app /usr/local/bin/
    ENTRYPOINT ["/usr/local/bin/app"]
    SAVE IMAGE my-app:latest
```

### Integration Testing with Docker

```Earthfile
VERSION 0.8

integration-test:
    FROM earthly/dind:alpine-3.19-docker-25.0.5-r0
    COPY docker-compose.yml ./
    WITH DOCKER --compose docker-compose.yml --load=+docker
        RUN docker-compose run tests
    END
```

### Reusable Function

```Earthfile
VERSION 0.8

GO_BUILD:
    FUNCTION
    ARG package
    ARG output
    RUN go build -o "$output" "$package"
    SAVE ARTIFACT "$output"

build-api:
    FROM golang:1.21
    COPY . .
    DO +GO_BUILD --package=./cmd/api --output=api

build-worker:
    FROM golang:1.21
    COPY . .
    DO +GO_BUILD --package=./cmd/worker --output=worker
```

### Cross-Repository Import

```Earthfile
VERSION 0.8
IMPORT github.com/earthly/lib/rust:3.0.1

build:
    FROM rust:1.75
    DO rust+INIT --keep_fingerprints=true
    COPY --dir src Cargo.toml Cargo.lock ./
    DO rust+CARGO --args="build --release"
    SAVE ARTIFACT target/release/myapp
```
