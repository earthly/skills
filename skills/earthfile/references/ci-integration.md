# CI Integration

Earthly is designed to work seamlessly with any CI system. The same Earthfile runs locally and in CI.

**Note:** Earthly Cloud features (Satellites, cloud secrets, remote runners) are no longer available. This guide focuses on self-hosted usage.

## Basic CI Usage

### The --ci Flag

Use `--ci` in CI pipelines. It's shorthand for:
- `--no-output` - Don't output artifacts/images to host
- `--strict` - Disallow LOCALLY and other non-repeatable commands
- `--use-inline-cache --save-inline-cache` - Enable inline caching

```bash
earthly --ci +all
```

### Push Mode

To push images, add `--push`:

```bash
earthly --ci --push +all
```

## GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Earthly
        run: |
          sudo /bin/sh -c 'wget https://github.com/earthly/earthly/releases/latest/download/earthly-linux-amd64 -O /usr/local/bin/earthly && chmod +x /usr/local/bin/earthly'
          earthly bootstrap
      
      - name: Build and Test
        run: earthly --ci +all
      
      - name: Push (main only)
        if: github.ref == 'refs/heads/main'
        run: earthly --ci --push +all
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```

### With Docker Login

```yaml
      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and Push
        run: earthly --ci --push +all
```

## GitLab CI

```yaml
# .gitlab-ci.yml
image: docker:24

services:
  - docker:24-dind

variables:
  DOCKER_HOST: tcp://docker:2375

before_script:
  - wget https://github.com/earthly/earthly/releases/latest/download/earthly-linux-amd64 -O /usr/local/bin/earthly
  - chmod +x /usr/local/bin/earthly
  - earthly bootstrap

build:
  script:
    - earthly --ci +all

push:
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - earthly --ci --push +all
  only:
    - main
```

## Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'earthly/earthly:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'earthly --ci +all'
            }
        }
        
        stage('Push') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'docker login -u $DOCKER_USER -p $DOCKER_PASS'
                    sh 'earthly --ci --push +all'
                }
            }
        }
    }
}
```

## CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  build:
    machine:
      image: ubuntu-2204:current
    steps:
      - checkout
      - run:
          name: Install Earthly
          command: |
            sudo wget https://github.com/earthly/earthly/releases/latest/download/earthly-linux-amd64 -O /usr/local/bin/earthly
            sudo chmod +x /usr/local/bin/earthly
            earthly bootstrap
      - run:
          name: Build
          command: earthly --ci +all
      - run:
          name: Push
          command: |
            if [ "$CIRCLE_BRANCH" = "main" ]; then
              earthly --ci --push +all
            fi

workflows:
  build-workflow:
    jobs:
      - build
```

## Secrets in CI

### Environment Variables

```bash
# Pass secrets from environment
earthly --secret MY_TOKEN="$MY_TOKEN" +deploy
```

### From Files

```bash
# Pass secret from file
earthly --secret-file SSH_KEY=/path/to/key +deploy
```

### In Earthfile

```Earthfile
deploy:
    RUN --secret MY_TOKEN echo "Deploying with token"
    RUN --mount=type=secret,id=SSH_KEY,target=/root/.ssh/id_rsa ssh-keyscan github.com >> /root/.ssh/known_hosts
```

## Caching in CI

### Inline Cache

Share cache via container registry:

```bash
# CI build with cache
earthly --ci \
  --use-inline-cache \
  --save-inline-cache \
  --push +all
```

The inline cache is stored in the pushed images.

### Remote BuildKit (Self-Hosted)

Run a persistent BuildKit instance:

```bash
# On a dedicated server
docker run -d \
  --name earthly-buildkitd \
  -p 8372:8372 \
  --privileged \
  earthly/buildkitd:latest

# In CI
earthly --buildkit-host tcp://buildkit-server:8372 --ci +all
```

### Pull-Through Cache

Configure a registry mirror for faster pulls:

```yaml
# ~/.earthly/config.yml
global:
  buildkit_additional_config: |
    [registry."docker.io"]
      mirrors = ["your-registry-mirror:5000"]
```

## Best Practices

### 1. Push on Main Only

```yaml
# GitHub Actions example
- name: Build
  run: earthly --ci +all

- name: Push
  if: github.ref == 'refs/heads/main'
  run: earthly --ci --push +all
```

### 2. Use --ci Flag

Always use `--ci` to ensure strict, reproducible builds:

```bash
# Good
earthly --ci +all

# Bad - may use LOCALLY targets
earthly +all
```

### 3. Single Earthly Invocation

```bash
# Good - single invocation
earthly --ci +all

# Bad - multiple invocations waste cache
earthly --ci +build
earthly --ci +test
earthly --ci +push
```

### 4. Define an "all" Target

```Earthfile
all:
    BUILD +lint
    BUILD +test
    BUILD +build
    BUILD +docker
```

### 5. Separate Build and Push Concerns

```Earthfile
all:
    BUILD +test
    BUILD +docker

docker:
    FROM +build
    SAVE IMAGE my-app:latest
    SAVE IMAGE --push registry.io/my-app:latest
```

The `--push` images only push when `earthly --push` is used.

## Debugging CI Failures

### Reproduce Locally

```bash
# Run the exact same command as CI
earthly --ci +all
```

### Interactive Debug

On failure in CI, you can reproduce locally:

```bash
earthly -i +failing-target
```

### Verbose Output

```bash
earthly --ci --verbose +all
```

## Common Issues

### Docker Socket Access

```yaml
# Mount Docker socket
services:
  - docker:dind
# Or use machine executor with Docker pre-installed
```

### Disk Space

```bash
# Clean up before build
earthly prune --all
docker system prune -af
```

### Timeouts

```bash
# Increase BuildKit timeout
earthly --buildkit-additional-config 'worker.oci.env["BUILDKIT_STEP_LOG_MAX_SPEED"]="10485760"' +all
```

## Next Steps

- [caching.md](caching.md) - Cache optimization
- [best-practices.md](best-practices.md) - More best practices
- [docs/ci-integration/overview.md](../docs/ci-integration/overview.md) - Complete CI guide
- [docs/ci-integration/guides/](../docs/ci-integration/guides/) - Vendor-specific guides
