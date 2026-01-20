# Installing Lunar Hub

Lunar Hub is the central service that, along with its database, stores metadata,
evaluates policies, and provides visibility into overall code and CI engineering
health. It is deployed as a containerized application and requires a set of
environment variables for configuration.

## Installation

1. Pull the latest release image from [Docker Hub](https://hub.docker.com/r/earthly/lunar-hub):

   ```bash
   docker pull earthly/lunar-hub:latest
   ```

2. Set the following environment variables in your environment or `lunar.env` file:

   ```bash
   # Base configuration (required)
   export HUB_LOGS_AWS_BUCKET=your_logs_bucket
   export HUB_DB_NAME=postgres
   export HUB_DB_USER=postgres
   export HUB_DB_PASS=postgres
   export HUB_DB_HOST=localhost
   export HUB_GITHUB_WEBHOOK_SECRET=your_github_webhook_secret
   export HUB_GITHUB_TOKEN=your_github_token
   export HUB_GRAFANA_URL_BASE=your_grafana_url_base
   export HUB_AUTH_TOKEN=your_auth_token

   # Elastic logs integration
   export HUB_ELASTIC_URL=your_elastic_url
   export HUB_ELASTIC_API_KEY=your_elastic_api_key
   export HUB_TENANT_ID=your_tenant_id

   # Optional (defaults shown). Tune to your preferences.
   export HUB_STATE_DIR=/var/lib/lunar
   export HUB_HTTP_PORT=8001
   export HUB_GRPC_PORT=8000
   export HUB_HEALTH_PORT=8002
   export HUB_LOG_LEVEL=info
   export HUB_LOG_FORMAT=json
   ```

3. Run the container:

   ```bash
   docker run -d \
     --name=lunar-hub \
     --env-file=./lunar.env \
     -p 8000:8000 \
     -p 8001:8001 \
     -p 8002:8002 \
     earthly/lunar-hub:latest
   ```

4. Run `curl -v http://localhost:8002/health` (or your configured domain) to confirm it's running. You'll see a 200 response.

{% hint style='info' %}
For the full list of configuration options and production deployment guidance, refer to the [Lunar Hub Deployment Guide](https://github.com/earthly/lunar).
{% endhint %}

{% hint style='info' %}
For production deployments, you can also run Lunar Hub in a container orchestrator such as Kubernetes. This provides robust process management, scaling, and automated restarts. See the [Kubernetes documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) for guidance on creating a Deployment and managing your service in production.
{% endhint %}

## Using a Primary Configuration

Lunar Hub can be directed to pull and process a primary `lunar-config.yml` configuration from a source repository. This command must be run before any collectors or policies will be triggered. This can be done via the CLI using the following command:

```bash
lunar hub pull github://repo-name/project-name@branch-or-sha
```

**Examples:**

Pulling from a specific branch:

```bash
lunar hub pull github://acme-corp/infra-config@main
```

Pulling from a specific commit SHA:

```bash
lunar hub pull github://acme-corp/infra-config@de4adbeef
```

This command fetches the `lunar-config.yml` configuration file from the specified repository and branch or commit, then applies it to the running Hub instance. All domains, components, catalogers, collectors, & policy definitions, including all remote plugins, will be extracted and saved.

---

## Next Steps

Once installed, you can begin configuring:

- [Collectors](../lunar-config/collectors.md) to gather SDLC data
- [Policies](../lunar-config/policies.md) to enforce standards
- [Domains and Components](../key-concepts/key-concepts.md) to organize your software landscape

For questions or enterprise onboarding, [contact the Earthly team](https://earthly.dev/earthly-lunar/demo).
