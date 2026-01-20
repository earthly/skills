# Docker in Earthly

Earthly provides `WITH DOCKER` for running Docker commands inside the build, commonly used for integration testing.

## WITH DOCKER Basics

`WITH DOCKER` creates a temporary Docker daemon for running containers during the build.

```Earthfile
VERSION 0.8

integration-test:
    FROM earthly/dind:alpine-3.19-docker-25.0.5-r0
    WITH DOCKER
        RUN docker run hello-world
    END
```

### Key Points

- Only ONE `RUN` command is allowed inside `WITH DOCKER`
- Multiple shell commands can be chained with `&&`
- Docker daemon is wiped after `WITH DOCKER` ends
- Automatically implies `--privileged`
- Files created during the RUN persist after WITH DOCKER ends

## Loading Images

### From Targets

```Earthfile
my-app:
    FROM node:18
    COPY . .
    RUN npm install && npm run build
    ENTRYPOINT ["node", "dist/index.js"]
    SAVE IMAGE my-app:latest

integration-test:
    FROM earthly/dind:alpine-3.19-docker-25.0.5-r0
    WITH DOCKER --load=+my-app
        RUN docker run my-app:latest --version
    END
```

### With Build Args

```Earthfile
integration-test:
    WITH DOCKER --load=(+my-app --ENV=test)
        RUN docker run my-app:latest
    END
```

### Custom Image Name

```Earthfile
WITH DOCKER --load=test-image:v1=+my-app
    RUN docker run test-image:v1
END
```

## Pulling Images

Always use `--pull` for external images (better caching):

```Earthfile
integration-test:
    FROM earthly/dind:alpine-3.19-docker-25.0.5-r0
    WITH DOCKER --pull=postgres:15 --pull=redis:7
        RUN docker run -d postgres:15 && \
            docker run -d redis:7 && \
            sleep 5 && \
            ./run-tests.sh
    END
```

## Docker Compose

```Earthfile
integration-test:
    FROM earthly/dind:alpine-3.19-docker-25.0.5-r0
    COPY docker-compose.yml ./
    WITH DOCKER \
            --compose docker-compose.yml \
            --load=api:latest=+api-image \
            --service db \
            --service cache
        RUN docker-compose up -d && \
            sleep 10 && \
            docker-compose run tests
    END
```

### Options

| Option | Description |
|--------|-------------|
| `--compose file.yml` | Load compose file |
| `--service name` | Start specific service |
| `--pull image` | Pull external image |
| `--load [name=]target` | Load image from target |
| `--platform platform` | Platform for loaded images |

## Base Images for WITH DOCKER

Always use an image with Docker pre-installed:

```Earthfile
# Recommended - official Earthly images
FROM earthly/dind:alpine-3.19-docker-25.0.5-r0
FROM earthly/dind:ubuntu-23.04-docker-25.0.2-1

# Alternative - install Docker in any image
FROM alpine:3.18
DO github.com/earthly/lib+INSTALL_DIND
```

## Integration Test Pattern

```Earthfile
VERSION 0.8

build:
    FROM golang:1.21
    COPY . .
    RUN go build -o app ./cmd/main.go
    SAVE ARTIFACT app

docker:
    FROM alpine:3.18
    COPY +build/app /usr/local/bin/
    ENTRYPOINT ["/usr/local/bin/app"]
    SAVE IMAGE my-app:latest

integration-test:
    FROM earthly/dind:alpine-3.19-docker-25.0.5-r0
    COPY docker-compose.test.yml ./
    COPY tests ./tests
    
    WITH DOCKER \
            --compose docker-compose.test.yml \
            --load=my-app:latest=+docker \
            --pull=postgres:15
        RUN docker-compose up -d db && \
            sleep 5 && \
            docker-compose up --exit-code-from tests tests
    END

all:
    BUILD +docker
    BUILD +integration-test
```

## Saving Artifacts from WITH DOCKER

Files persist after WITH DOCKER, so you can save test results:

```Earthfile
integration-test:
    FROM earthly/dind:alpine-3.19-docker-25.0.5-r0
    WITH DOCKER --load=+my-app
        RUN docker run -v $(pwd)/results:/results my-app:latest test && \
            docker logs my-container > ./logs.txt 2>&1
    END
    # These commands run after WITH DOCKER
    SAVE ARTIFACT ./results AS LOCAL ./test-results
    SAVE ARTIFACT ./logs.txt AS LOCAL ./test-logs.txt
```

## LOCALLY with WITH DOCKER

For local development, you can use WITH DOCKER with LOCALLY to use your host's Docker daemon:

```Earthfile
dev-test:
    LOCALLY
    WITH DOCKER --load=+docker
        RUN docker run --rm my-app:latest test
    END
```

**Note:** LOCALLY is not allowed in `--ci` mode.

## Debugging Failed Tests

```bash
# Use -i to get an interactive shell on failure
earthly -i +integration-test
```

Inside the shell:
```bash
# Re-run the Docker command
docker-compose up
# Inspect containers
docker ps -a
docker logs container-name
```

## Common Patterns

### Health Check Before Tests

```Earthfile
WITH DOCKER --compose docker-compose.yml
    RUN docker-compose up -d && \
        while ! docker-compose exec -T db pg_isready; do sleep 1; done && \
        ./run-tests.sh
END
```

### Parallel Services

```Earthfile
WITH DOCKER \
        --pull=postgres:15 \
        --pull=redis:7 \
        --pull=rabbitmq:3
    RUN docker run -d --name pg postgres:15 && \
        docker run -d --name redis redis:7 && \
        docker run -d --name mq rabbitmq:3 && \
        # Wait for all services
        ./wait-for-services.sh && \
        ./run-tests.sh
END
```

### Cleanup (Not Usually Needed)

The Docker daemon is wiped automatically after WITH DOCKER, but if you're using LOCALLY:

```Earthfile
dev-test:
    LOCALLY
    WITH DOCKER --load=+docker
        RUN docker run --rm my-app:latest test
    END
    # Note: --rm flag ensures container is removed
```

## Next Steps

- [caching.md](caching.md) - Caching strategies
- [ci-integration.md](ci-integration.md) - CI best practices
- [docs/guides/docker-in-earthly.md](../docs/guides/docker-in-earthly.md) - Complete guide
- [docs/guides/integration.md](../docs/guides/integration.md) - Integration testing guide
