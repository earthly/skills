# Functions and Imports

Functions and imports enable code reuse across Earthfiles and projects.

## Functions

Functions (formerly called UDCs - User Defined Commands) are reusable sets of instructions that inherit the caller's build context and environment.

### Defining Functions

Functions are named in ALL_UPPERCASE_SNAKE_CASE and start with `FUNCTION`:

```Earthfile
VERSION 0.8

GO_BUILD:
    FUNCTION
    ARG package
    ARG output=app
    RUN go build -o "$output" "$package"
    SAVE ARTIFACT "$output"
```

### Calling Functions

Use `DO` to call a function:

```Earthfile
build:
    FROM golang:1.21
    COPY . .
    DO +GO_BUILD --package=./cmd/api --output=api-server
```

### Function Scope

Functions:
- **Inherit** the build context (files, working directory) from the caller
- **Inherit** the build environment (installed packages, env vars) from the caller
- **Create their own** ARG scope - args must be passed explicitly
- **Can modify** the caller's filesystem (changes are visible after `DO`)

```Earthfile
setup:
    FROM alpine
    WORKDIR /app
    RUN echo "initial" > /app/file.txt
    DO +MODIFY_FILE      # Function runs in /app, can see file.txt
    RUN cat /app/file.txt  # Shows "modified" - change persists

MODIFY_FILE:
    FUNCTION
    RUN echo "modified" > /app/file.txt
```

### Functions vs Targets

| Aspect | Target | Function |
|--------|--------|----------|
| Naming | `lowercase-kebab` | `UPPERCASE_SNAKE` |
| Build context | Own Earthfile's directory | Inherited from caller |
| Build environment | Starts fresh or from `FROM` | Inherited from caller |
| ARG scope | Own scope | Own scope |
| Can output artifacts | Yes (directly) | No (caller outputs) |
| Called with | `BUILD`, `FROM`, `COPY` | `DO` |
| Can call via CLI | Yes | No |

### Function Best Practices

```Earthfile
# Good: Generic, reusable function
NPM_INSTALL:
    FUNCTION
    ARG ci=false
    IF [ "$ci" = "true" ]
        RUN npm ci
    ELSE
        RUN npm install
    END

# Good: Function that sets up common tooling
INSTALL_GO_TOOLS:
    FUNCTION
    RUN go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
    RUN go install golang.org/x/tools/cmd/goimports@latest
```

## Imports

IMPORT creates an alias for an Earthfile, making references shorter and cleaner.

### Basic Import

```Earthfile
VERSION 0.8
IMPORT ./frontend AS fe
IMPORT github.com/earthly/lib AS lib

build:
    BUILD fe+compile           # Same as ./frontend+compile
    DO lib+INSTALL_DIND       # Same as github.com/earthly/lib+INSTALL_DIND
```

### Import Types

```Earthfile
# Local subdirectory
IMPORT ./services/api AS api

# Local parent/sibling
IMPORT ../shared AS shared

# Remote repository
IMPORT github.com/earthly/lib

# Remote at specific version
IMPORT github.com/earthly/lib:3.0.1 AS lib

# Auto-aliased (uses last path component)
IMPORT github.com/earthly/lib  # Alias is "lib"
```

### Global vs Local Imports

Imports in the base recipe are global (available to all targets):

```Earthfile
VERSION 0.8
IMPORT github.com/earthly/lib AS lib  # Global - available everywhere

build:
    DO lib+INSTALL_DIND

test:
    DO lib+INSTALL_DIND   # Also works here
```

## Reference Syntax

### Target References

```
+build                              # Same Earthfile
./subdir+build                      # Subdirectory
../other+build                      # Parent directory
github.com/org/repo+build          # Remote
github.com/org/repo:v1.0+build     # Remote with tag
imported-alias+build                # Via IMPORT
```

### Artifact References

```
+build/path/to/file                 # Artifact from +build
./subdir+build/file                 # From subdirectory
(+build/file --arg=val)             # With build args
```

### Function References

```
+MY_FUNCTION                        # Same Earthfile
./subdir+MY_FUNCTION                # Subdirectory
imported-alias+MY_FUNCTION          # Via IMPORT
```

## Earthly Lib

The official `github.com/earthly/lib` provides useful functions:

```Earthfile
VERSION 0.8
IMPORT github.com/earthly/lib:3.0.1

integration-test:
    FROM alpine:3.18
    DO lib+INSTALL_DIND  # Install Docker-in-Docker
    WITH DOCKER
        RUN docker run hello-world
    END
```

Common functions:
- `lib+INSTALL_DIND` - Install Docker daemon
- `lib/rust+INIT` - Setup Rust with caching
- `lib/rust+CARGO` - Run cargo with caching

## Cross-Repository Patterns

### Consuming from Another Repo

```Earthfile
# In consumer repo
VERSION 0.8
IMPORT github.com/myorg/shared-lib:v1.0 AS shared

build:
    FROM shared+base-image
    COPY shared+generated-code/protos ./protos
```

### Exposing for Other Repos

```Earthfile
# In shared-lib repo
VERSION 0.8

base-image:
    FROM golang:1.21
    RUN go install tools...
    SAVE IMAGE myorg/base:latest

generated-code:
    FROM +base-image
    COPY *.proto ./
    RUN protoc --go_out=. *.proto
    SAVE ARTIFACT ./protos
```

## Versioning Remote References

Always pin versions in production:

```Earthfile
# Good - pinned version
IMPORT github.com/earthly/lib:3.0.1 AS lib
BUILD github.com/org/repo:v1.2.3+target

# Risky - may change
IMPORT github.com/earthly/lib AS lib
BUILD github.com/org/repo+target
```

## allow-privileged

For remote targets that need privileged operations:

```Earthfile
IMPORT --allow-privileged github.com/org/repo AS repo

build:
    FROM --allow-privileged repo+privileged-target
```

## Next Steps

- [docker-in-earthly.md](docker-in-earthly.md) - Docker-in-Docker for testing
- [best-practices.md](best-practices.md) - Best practices for organization
- [docs/guides/functions.md](../docs/guides/functions.md) - Complete functions guide
- [docs/guides/importing.md](../docs/guides/importing.md) - Complete importing guide
