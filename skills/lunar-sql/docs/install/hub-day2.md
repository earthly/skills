# Day 2 Operations

This page covers what you need to run Lunar Hub after the initial install: upgrades, secret rotation, observability, and uninstall. For the per-version upgrade notes (what values changed, what to migrate), see the [chart README's Upgrading section](https://github.com/earthly/charts/blob/main/README.md#upgrading).

## Upgrading

```bash
helm repo update
helm upgrade lunar earthly/lunar \
  --namespace lunar \
  -f values.yaml
```

The Hub runs migrations automatically on every startup. Migrations are forward-only and an interrupted one is safe to retry.

**Before every upgrade:**

1. **Back up Postgres.** Migrations are forward-only. If you need to roll back, roll the database back.
2. **Preview the chart changes.** The [`helm-diff`](https://github.com/databus23/helm-diff) plugin is worth installing — `helm diff upgrade lunar earthly/lunar -f values.yaml` shows exactly what Kubernetes resources will change.
3. **Read the version-specific notes** in the [chart README](https://github.com/earthly/charts/blob/main/README.md#upgrading). Minor version bumps occasionally require values changes.
4. **Pin your new image tags** in `values.yaml`. Don't rely on the chart's default tags.

{% hint style='warning' %}
The Hub runs as a single replica today. Helm's default rolling-update strategy will briefly run two Hubs (old and new) during upgrade; the new Hub will block on migrations if the old one is still holding DB connections. Plan for a ~1 minute Hub API unavailability during upgrade. CI agents and collectors/policy/catalogers should retry transparently across this window.
{% endhint %}

## Rotating secrets

Lunar's secrets split into two categories — **user-managed** (you create and rotate them) and **chart-managed** (auto-generated on first install, preserved across upgrades via `helm.sh/resource-policy: keep`). See [Required secrets](https://github.com/earthly/charts/blob/main/README.md#required-secrets) in the chart README for the full list and naming rules.

### Hub auth token (`<release>-auth-token`)

Used by the CLI and CI agents to authenticate to the Hub. The Hub accepts a single token today — rotation requires a coordinated cutover. To force a regeneration, delete the secret and re-run `helm upgrade` (the chart will generate a fresh token):

```bash
kubectl -n lunar delete secret lunar-auth-token
helm upgrade lunar earthly/lunar -n lunar -f values.yaml
kubectl -n lunar rollout restart deployment/lunar-hub
kubectl -n lunar rollout restart deployment/lunar-operator
```

Both the Hub and the Operator read this token from the same secret (the Operator uses it as `OPERATOR_HUB_TOKEN` to call the Hub), so restart both. Retrieve the new token with `kubectl -n lunar get secret lunar-auth-token -o jsonpath='{.data.token}' | base64 -d`, then update every CI agent's `LUNAR_HUB_TOKEN` and every developer's CLI config. Active builds authenticated with the old token will fail mid-run and need to be retried. Dual-token support is on the roadmap.

To pin to an externally-managed token instead, set `hub.auth.secretName` in values to a secret you control — the chart will consume it instead of generating its own.

### GitHub App private key (`lunar-github-app`)

GitHub supports multiple active private keys per App — rotate with zero downtime:

1. **Generate a new key** in GitHub → **Apps → your App → Private keys → Generate a private key**. Download the new PEM.
2. **Update the Kubernetes secret** in place, matching the install-time encoding (the Hub expects a base64-encoded PEM inside the secret value):

   ```bash
   kubectl -n lunar create secret generic lunar-github-app \
     --from-literal=private-key="$(base64 < path/to/new-key.pem | tr -d '\n')" \
     --dry-run=client -o yaml | kubectl apply -f -
   ```
3. **Restart the Hub** — `kubectl -n lunar rollout restart deployment/lunar-hub`.
4. **Verify** webhooks still deliver successfully (GitHub → any repo → **Settings → Webhooks → Recent Deliveries**).
5. **Delete the old key** in GitHub.

### GitHub webhook secret (`<release>-github-webhook`)

Changing the webhook secret requires re-registering every repo's webhook. Easier path: delete and regenerate, then re-pull your primary config to trigger re-registration.

```bash
kubectl -n lunar delete secret lunar-github-webhook
helm upgrade lunar earthly/lunar -n lunar -f values.yaml
kubectl -n lunar rollout restart deployment/lunar-hub

# Re-pull triggers webhook re-registration on every repo in your config.
lunar hub pull github://your-org/your-config-repo@main
```

During the window between Hub restart and `lunar hub pull`, per-repo webhooks from GitHub are still signed with the old secret, and the new Hub rejects them with a `500`. **GitHub does not auto-retry failed webhook deliveries** — any events in that window are lost unless you manually redeliver them from **Settings → Webhooks → Recent Deliveries** on the affected repos. Minimize the gap by running `lunar hub pull` immediately after the Hub restart comes up healthy.

### Database password (`lunar-db`)

Standard Kubernetes secret rotation. If your Postgres supports multiple active passwords (e.g. RDS password grace), rotate without downtime:

1. Set the new password in Postgres (keeping the old one active).
2. Update the `lunar-db` secret.
3. Restart the Hub.
4. Revoke the old password.

If your Postgres doesn't support multiple active passwords, expect ~1 minute of Hub unavailability during the rotation.

### Other secrets

A few secrets don't get their own recipe above:

| Secret | Managed by | Consumed by |
|---|---|---|
| `<release>-grafana-admin` | Chart | `lunar-grafana` deployment |
| Elastic telemetry API key (default `lunar-elastic-api-key`) | You | Hub + Operator |
| Per-scope runtime secrets (`hub.secrets.{collector,cataloger,policy}.secretName`) | You | Hub |

The rotation shape follows the same split as the sections above:

- **Chart-managed** (Grafana admin): `kubectl delete secret <name>` → `helm upgrade` to regenerate → restart the consumer deployment.
- **User-managed** (Elastic, runtime secrets): update the secret in place (`kubectl apply` or `kubectl create --dry-run=client -o yaml | kubectl apply -f -`) → restart the consumer(s).

To find what consumes an arbitrary secret:

```bash
kubectl -n lunar get deployments -o yaml | grep -B2 '<secret-name>'
```

## Observability

### Logs

The Hub and Operator log in structured JSON by default (`logging.format: json`). Log level defaults to `info`; raise to `debug` temporarily by editing `values.yaml` and running `helm upgrade`.

The Hub and Operator don't ship logs anywhere themselves — they stream to stdout. To get them into your log aggregator, point a cluster-level log shipper (Fluent Bit, Vector, Datadog Agent, etc.) at the `lunar` namespace.

### Telemetry to Earthly

The Hub and Operator can send structured logs back to Earthly for usage analytics, performance monitoring, and support diagnostics — it helps us improve Lunar and diagnose your issues faster. Earthly provides the telemetry credentials as part of onboarding; drop them into your values:

```yaml
telemetry:
  enabled: true
  elastic:
    url: "https://..."  # from Earthly
```

Create the corresponding API key secret:

```bash
kubectl -n lunar create secret generic lunar-elastic-api-key \
  --from-literal=api-key='<earthly-provided-key>'
```

The default `telemetry.elastic.apiKeySecret.secretName` (`lunar-elastic-api-key`) and `secretKey` (`api-key`) match the command above. Override them if your secret uses different names.

To disable telemetry, set `telemetry.enabled: false`. Hub and Operator logs still stream to stdout either way, so `kubectl logs` and any cluster-level log shipper continue to work.

### Metrics

The Hub exports request-duration histograms (HTTP and gRPC) via OTLP to a collector you run. Point it at your OTEL collector via `hub.extraEnv`:

```yaml
hub:
  extraEnv:
    - name: HUB_OTEL_COLLECTOR_ENDPOINT
      value: otel-collector.observability:4317
    - name: HUB_OTEL_SECURE
      value: "false"
```

Both env vars are required. If `HUB_OTEL_COLLECTOR_ENDPOINT` is unset the Hub writes metrics to a local temp file (effectively disabled). Secure (TLS) OTLP isn't implemented yet — `HUB_OTEL_SECURE` must be `"false"` or the Hub will fail to start. The service name is hardcoded `hub`.

{% hint style='info' %}
The Hub does not export distributed traces today — only metrics. Trace support is on the roadmap.
{% endhint %}

### Diagnostics bundle

The Hub can produce a diagnostics bundle (Postgres queue state, recent error logs, slow-query stats) for support requests. The bundle gathers extra Postgres telemetry when the `pg_stat_statements` extension is enabled — without it the bundle still works, just with less query-performance data.

To enable it:

- **Amazon RDS / Aurora:** add `pg_stat_statements` to `shared_preload_libraries` in the DB parameter group, then reboot the instance.
- **Self-managed:** add `pg_stat_statements` to `shared_preload_libraries` in `postgresql.conf` and restart, then `CREATE EXTENSION pg_stat_statements;` as a superuser.

The Hub does not require this extension — it's only used by the diagnostics path.

## Scaling

Lunar Hub runs as a single replica today. Vertical scaling (CPU, memory, Postgres connection pool via `HUB_DB_MAX_OPEN_CONNS` / `HUB_DB_MAX_POOL_CONNS`) is the way to handle more load. Horizontal scaling of the Hub is not yet supported.

Run throughput scales independently — raise `operator.maxConcurrent` and size run pod resources accordingly. See [`operator.snippetContainerSpec*`](https://github.com/earthly/charts/blob/main/README.md#values-reference) in the chart README.

## Backup and disaster recovery

Lunar's authoritative state lives in the systems you already back up:

- **Postgres** — use your existing Postgres backup process. Everything the Hub cares about (components, policies, run history, queue state) is here.
- **S3 buckets** — enable object versioning on both buckets and, if compliance requires, cross-region replication. Lost resource archives cause re-building the cache of catalogers, collectors, and policies; lost log archives mean lost history. Neither impedes Hub operation.
- **Hub PVC** — the Hub's PVC at `/var/lib/lunar` holds the local git repo cache and materialized run bundles. It is regenerable; the Hub repopulates it on startup from Postgres and S3. You do not need to back it up.
- **Kubernetes secrets** — keep the GitHub App PEM, DB credentials, auth token, and webhook secret in your organization's secret-management system of record. Losing them means re-provisioning.

## Uninstalling

```bash
helm uninstall lunar --namespace lunar
```

Helm removes all resources the chart created: the Hub and operator deployments, services, ingress, RBAC, and service accounts.

**Not removed automatically:**

- The `lunar` namespace itself (and, if used, the Operator's execution namespace).
- Kubernetes secrets you created manually (e.g. `lunar-db`, `lunar-github-app`).
- Chart-managed secrets (`<release>-auth-token`, `<release>-github-webhook`, `<release>-grafana-admin`). These carry `helm.sh/resource-policy: keep` so a re-install reuses the same values — by design. Delete them explicitly if you want fresh credentials on the next install.
- The Hub's PVC (`<release>-hub` by default). Delete with `kubectl -n lunar delete pvc -l app.kubernetes.io/instance=lunar` if you want the state gone.
- Your Postgres database, S3 buckets, or their contents.
- The GitHub App. Webhooks previously registered by this Hub are tagged with the Hub's instance ID (`earthly-lunar-<tenantId>` as a URL fragment); they remain on your repos until you remove them manually or install a fresh Hub with the same `tenantId`, which will clean up its own stale webhooks on next config pull.

To fully tear down:

```bash
helm uninstall lunar --namespace lunar
kubectl -n lunar delete pvc -l app.kubernetes.io/instance=lunar
kubectl -n lunar delete secret lunar-db lunar-github-app \
  lunar-auth-token lunar-github-webhook lunar-grafana-admin \
  --ignore-not-found
kubectl delete namespace lunar

# Externally:
#   - Drop the Postgres database
#   - Delete or empty the S3 buckets
#   - Uninstall the GitHub App from your organization
```

## Getting help

- [Chart values reference](https://github.com/earthly/charts/blob/main/README.md#values-reference)
- [Chart source](https://github.com/earthly/charts)
- [Lunar source](https://github.com/earthly/lunar)
- For enterprise onboarding or production sizing guidance, [contact the Earthly team](https://earthly.dev/earthly-lunar/demo).
