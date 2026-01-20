# Caching in Earthly

Earthly provides powerful caching mechanisms to speed up builds. Understanding how caching works helps you write faster, more efficient Earthfiles.

## Layer Caching

Like Docker, Earthly caches each command as a layer. Layers are reused when:
- The command hasn't changed
- All previous layers are unchanged
- Input files haven't changed

```Earthfile
build:
    FROM golang:1.21
    COPY go.mod go.sum ./    # Cache key: go.mod, go.sum content
    RUN go mod download      # Cached if go.mod/go.sum unchanged
    COPY . .                 # Cache key: all copied files
    RUN go build ./...       # Cached if source unchanged
```

### Optimizing Layer Cache

Order commands from least to most frequently changing:

```Earthfile
# Bad - any source change invalidates dependency download
build:
    FROM node:18
    COPY . .
    RUN npm install

# Good - dependencies cached separately from source
build:
    FROM node:18
    COPY package.json package-lock.json ./
    RUN npm ci
    COPY src ./src
    RUN npm run build
```

## Cache Mounts

Cache mounts persist data between builds, even when the layer is invalidated.

### RUN --mount

```Earthfile
build:
    FROM golang:1.21
    ENV GOCACHE=/go-cache
    RUN --mount=type=cache,target=/go-cache go build ./...
```

### CACHE Command

```Earthfile
build:
    FROM golang:1.21
    CACHE /root/.cache/go-build
    CACHE /go/pkg/mod
    COPY . .
    RUN go build ./...
```

### Cache Mount Options

```Earthfile
# Shared cache (concurrent builds can access)
RUN --mount=type=cache,target=/cache,sharing=shared go build

# Locked cache (exclusive access, default)
RUN --mount=type=cache,target=/cache,sharing=locked go build

# Named cache (shared across targets/Earthfiles)
RUN --mount=type=cache,target=/cache,id=my-global-cache go build
```

| Option | Values | Description |
|--------|--------|-------------|
| `sharing` | `locked`, `shared`, `private` | Concurrency mode |
| `id` | string | Global cache identifier |

## Common Cache Locations

### Go
```Earthfile
CACHE /root/.cache/go-build
CACHE /go/pkg/mod
ENV GOCACHE=/root/.cache/go-build
```

### Node.js
```Earthfile
CACHE /root/.npm
# Or for npm ci with cache
RUN --mount=type=cache,target=/root/.npm npm ci
```

### Python
```Earthfile
CACHE /root/.cache/pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
```

### Rust
```Earthfile
CACHE /usr/local/cargo/registry
CACHE target
```

### Maven
```Earthfile
CACHE /root/.m2/repository
```

### Gradle
```Earthfile
CACHE /root/.gradle/caches
```

## Copy Optimization

### Minimal COPY

Only copy what's needed to avoid unnecessary cache invalidation:

```Earthfile
# Bad - copies everything including unneeded files
COPY . .

# Good - only copy what's needed for each step
COPY go.mod go.sum ./
RUN go mod download
COPY *.go ./
COPY internal ./internal
```

### .earthlyignore

Exclude files from the build context:

```
# .earthlyignore
.git
node_modules
*.log
.env
```

## No-Cache Operations

### RUN --no-cache

Forces a command to always run:

```Earthfile
RUN --no-cache date > /build-date.txt
```

**Warning:** All subsequent commands will also skip cache.

### Selective Cache Invalidation

Use ARGs to control cache:

```Earthfile
build:
    ARG CACHE_BUST=""  # Empty by default
    RUN echo "$CACHE_BUST" && expensive-operation
```

```bash
# Normal build - uses cache
earthly +build

# Force rebuild
earthly +build --CACHE_BUST=$(date +%s)
```

## Cache Management

### Viewing Cache

```bash
# See cache disk usage
earthly prune --dry-run
```

### Clearing Cache

```bash
# Remove unused cache
earthly prune

# Remove all cache
earthly prune -a
```

## Inline Cache

Share cache via container registry (note: Earthly Cloud is no longer available):

```bash
# Save cache to registry
earthly --save-inline-cache --push +build

# Use cache from registry
earthly --use-inline-cache +build
```

## Auto-Skip

Skip targets entirely if their inputs haven't changed:

```Earthfile
all:
    BUILD --auto-skip +expensive-build
```

**Requires:** Earthly to track the target's inputs across builds.

## Cache Tips

### 1. Structure for Cache Hits

```Earthfile
# Dependencies first, source last
COPY package.json package-lock.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src ./src
RUN npm run build
```

### 2. Use Cache Mounts for Package Managers

```Earthfile
RUN --mount=type=cache,target=/root/.npm npm ci
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
```

### 3. Avoid --no-cache Unless Necessary

```Earthfile
# Only use for truly non-cacheable operations
RUN --no-cache --push ./deploy.sh
```

### 4. ARG Placement Matters

```Earthfile
# Bad - ARG early invalidates cache for all following commands
ARG VERSION
RUN expensive-setup.sh
RUN echo $VERSION > /version.txt

# Good - ARG late preserves cache for earlier commands
RUN expensive-setup.sh
ARG VERSION
RUN echo $VERSION > /version.txt
```

### 5. Separate Cacheable Work

```Earthfile
deps:
    COPY go.mod go.sum ./
    RUN go mod download
    SAVE ARTIFACT /go/pkg/mod /mod

build:
    COPY +deps/mod /go/pkg/mod
    COPY . .
    RUN go build
```

## Next Steps

- [ci-integration.md](ci-integration.md) - Caching in CI environments
- [best-practices.md](best-practices.md) - Performance optimization
- [docs/caching/caching.md](../docs/caching/caching.md) - Complete caching guide
