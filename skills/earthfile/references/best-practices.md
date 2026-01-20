# Earthfile Best Practices

Guidelines for writing efficient, maintainable Earthfiles.

## File Organization

### 1. High-Level Targets at Top

Define frequently-used targets at the top of your Earthfile:

```Earthfile
VERSION 0.8
FROM alpine:3.18

# High-level targets first
all:
    BUILD +lint
    BUILD +test
    BUILD +docker

ci:
    BUILD +all
    # CI-specific steps

# Lower-level targets below
lint:
    ...

test:
    ...
```

### 2. Place Earthfiles Near Code

```
project/
├── Earthfile              # Main targets
├── services/
│   ├── api/
│   │   ├── Earthfile      # API-specific targets
│   │   └── main.go
│   └── worker/
│       ├── Earthfile      # Worker-specific targets
│       └── main.go
└── shared/
    ├── Earthfile          # Shared functions
    └── utils.go
```

### 3. Don't Put All Earthfiles in One Directory

```Earthfile
# Bad - separated from code
build/
├── api.Earthfile
├── worker.Earthfile
└── shared.Earthfile

# Good - co-located with code
services/api/Earthfile
services/worker/Earthfile
shared/Earthfile
```

## COPY Best Practices

### 1. Copy Minimum Files

```Earthfile
# Bad - copies everything
COPY . .

# Good - only what's needed
COPY go.mod go.sum ./
RUN go mod download
COPY *.go ./
COPY internal ./internal
```

### 2. Order for Cache Efficiency

```Earthfile
# Copy least-changing files first
COPY package.json package-lock.json ./
RUN npm ci
# Then more frequently changing files
COPY src ./src
RUN npm run build
```

### 3. Use --dir for Multiple Directories

```Earthfile
# Bad - multiple layers
COPY dir1 dir1
COPY dir2 dir2
COPY dir3 dir3

# Good - single layer
COPY --dir dir1 dir2 dir3 ./
```

### 4. Avoid Copying .git

```Earthfile
# .earthlyignore
.git
```

## ARG Best Practices

### 1. ARG for Build Configuration, ENV for Image

```Earthfile
# ARG - build-time configuration, not in final image
ARG VERSION=dev
RUN echo "Building $VERSION"

# ENV - persists in final image
ENV NODE_ENV=production
```

### 2. Declare ARGs Late (Cache Optimization)

```Earthfile
# Bad - ARG early invalidates cache
ARG GIT_SHA
RUN expensive-setup.sh
RUN echo $GIT_SHA > /version.txt

# Good - ARG after expensive operations
RUN expensive-setup.sh
ARG GIT_SHA
RUN echo $GIT_SHA > /version.txt
```

### 3. Avoid --global for Frequently Changing Args

```Earthfile
# Bad - any change invalidates all targets
ARG --global GIT_SHA=$(git rev-parse HEAD)

# Good - pass explicitly where needed
build:
    ARG GIT_SHA
    RUN echo $GIT_SHA
```

## Secrets

### 1. Use --secret, Not ARG

```Earthfile
# Bad - secret in build history
ARG API_TOKEN
RUN curl -H "Authorization: $API_TOKEN" ...

# Good - secret not stored
RUN --secret API_TOKEN curl -H "Authorization: $API_TOKEN" ...
```

### 2. Mount Secrets as Files

```Earthfile
# Good - secret file not in layer
RUN --mount=type=secret,id=netrc,target=/root/.netrc \
    curl https://private.example.com/file
```

### 3. Never Copy Secrets to Filesystem

```Earthfile
# Bad - secret persists in layer
RUN --secret API_KEY echo "$API_KEY" > /config/key
RUN use-key.sh

# Good - use in single command, or mount
RUN --secret API_KEY sh -c 'use-key.sh "$API_KEY"'
# Or
RUN --mount=type=secret,id=API_KEY,target=/config/key use-key.sh
```

## Control Flow

### 1. Prefer RUN if Over IF When Possible

```Earthfile
# IF - for Earthly commands
IF [ "$DEBUG" = "true" ]
    SAVE ARTIFACT debug.log
END

# RUN if - for shell commands (simpler, single layer)
RUN if [ "$DEBUG" = "true" ]; then \
        echo "Debug mode"; \
    fi
```

### 2. Same for FOR vs RUN for

```Earthfile
# FOR - when you need Earthly commands
FOR dir IN $(ls -d */)
    BUILD "./$dir+test"
END

# RUN for - for shell operations
RUN for f in *.txt; do process "$f"; done
```

## Images

### 1. Separate Build and Production Images

```Earthfile
build:
    FROM golang:1.21
    COPY . .
    RUN go build -o app
    SAVE ARTIFACT app

docker:
    FROM alpine:3.18           # Fresh, minimal base
    COPY +build/app /usr/local/bin/
    ENTRYPOINT ["/usr/local/bin/app"]
    SAVE IMAGE my-app:latest
```

### 2. Use Multi-Stage Pattern

```Earthfile
deps:
    FROM node:18
    COPY package.json package-lock.json ./
    RUN npm ci

build:
    FROM +deps
    COPY . .
    RUN npm run build
    SAVE ARTIFACT dist

docker:
    FROM nginx:alpine
    COPY +build/dist /usr/share/nginx/html
    SAVE IMAGE my-frontend:latest
```

## Artifacts

### 1. Don't Pass via Local Filesystem

```Earthfile
# Bad - race condition, no dependency tracking
all:
    BUILD +build
    BUILD +use-artifact

build:
    SAVE ARTIFACT output AS LOCAL ./output

use-artifact:
    COPY ./output ./  # May not exist yet!
```

```Earthfile
# Good - explicit dependency
all:
    BUILD +use-artifact

build:
    RUN generate output
    SAVE ARTIFACT output

use-artifact:
    COPY +build/output ./
```

### 2. Use BUILD to Connect Output Chain

```Earthfile
all:
    BUILD +build     # Connects +build to output chain
    BUILD +test

build:
    SAVE ARTIFACT output AS LOCAL ./dist/output  # Now outputs!
```

## WITH DOCKER

### 1. Use earthly/dind Base Images

```Earthfile
# Good - Docker pre-installed
FROM earthly/dind:alpine-3.19-docker-25.0.5-r0

# Works but slower - installs Docker
FROM alpine:3.18
DO github.com/earthly/lib+INSTALL_DIND
```

### 2. Use --pull for External Images

```Earthfile
# Bad - no caching
WITH DOCKER
    RUN docker run postgres:15
END

# Good - cached
WITH DOCKER --pull=postgres:15
    RUN docker run postgres:15
END
```

### 3. Use --load for Earthly-Built Images

```Earthfile
WITH DOCKER --load=+my-image
    RUN docker run my-image:latest
END
```

## Git

### 1. Prefer Cross-Repo References Over GIT CLONE

```Earthfile
# Good - clear API, cache-aware
COPY github.com/org/repo+target/artifact ./

# OK - when you need the whole repo
GIT CLONE github.com/org/repo repo
```

### 2. GIT CLONE Over RUN git clone

```Earthfile
# Good - cache-aware, uses Earthly auth config
GIT CLONE git@github.com:org/repo.git repo

# Bad - not cache-aware
RUN git clone git@github.com:org/repo.git repo
```

## General

### 1. Single Earthly Invocation

```bash
# Good
earthly +all

# Bad
earthly +build && earthly +test && earthly +push
```

### 2. Use --push for Deploy Commands

```Earthfile
deploy:
    RUN --push ./deploy.sh  # Only runs with earthly --push
```

### 3. Avoid Non-Deterministic Behavior

```Earthfile
# Bad - different result each time
ARG BUILD_TIME=$(date)

# Better - deterministic
ARG VERSION=1.0.0
```

### 4. Document Your Earthfile

```Earthfile
VERSION 0.8

# Build and test the application
# Usage:
#   earthly +all           - Build and test
#   earthly --push +deploy - Deploy to production

all:
    BUILD +test
    BUILD +docker
```

## Anti-Patterns

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| `COPY . .` | Copy specific files |
| ARG for secrets | `RUN --secret` |
| Multiple earthly invocations | Single `+all` target |
| LOCALLY in CI-required paths | Keep LOCALLY for dev only |
| Wrapping earthly in scripts | Use Earthfile features |
| --no-cache for deploy | `RUN --push` |

## Next Steps

- [docs/guides/best-practices.md](../docs/guides/best-practices.md) - Complete best practices guide
- [caching.md](caching.md) - Cache optimization
- [ci-integration.md](ci-integration.md) - CI patterns
