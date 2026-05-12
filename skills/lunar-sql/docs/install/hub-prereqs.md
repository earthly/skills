# Lunar Hub Prerequisites

Before you run `helm install lunar`, the external dependencies below must be in place. The [install walkthrough](hub-install.md) assumes you have them.

If you want a total picture of what you're about to deploy, read the [overview](hub-overview.md) first.

{% hint style='info' %}
Lunar Hub is supported on Kubernetes only. Bare-metal and Docker installations are not supported.
{% endhint %}

## Before you begin

Make sure you have the following available before continuing.

| Step | What you need | Detail |
|---|---|---|
| — | Workstation tools | `kubectl`, `helm` 3.x |
| [2](#step-2--check-your-kubernetes-cluster) | Kubernetes cluster | 1.29+, with an ingress controller and a default StorageClass |
| [2](#step-2--check-your-kubernetes-cluster) | DNS hostnames + TLS certs | Two hostnames (Hub + Grafana), both reachable from GitHub (or your GHES instance) for the Hub, and from your users for Grafana |
| [3](#step-3--provision-postgresql) | PostgreSQL instance | 16+, where you can create a dedicated owner role |
| [4](#step-4--provision-s3-compatible-object-storage) | S3-compatible buckets | Two private buckets (logs + resources) with IAM to read and write them |
| [5](#step-5--create-a-github-app) | GitHub org admin access | Or a personal account, where you can create a GitHub App for your org |

{% hint style='info' %}
If you're standing up EKS from scratch, [`earthly/lunar-terraform-quickstart`](https://github.com/earthly/lunar-terraform-quickstart) is a working reference module you can fork if desired.
{% endhint %}

## Step 1 — Plan your Kubernetes namespaces

We recommend splitting the install across two namespaces:

- **Control-plane namespace** (e.g. `lunar`). This is the release namespace. It hosts the Lunar Hub, Operator, and Grafana. These are the parts that need to stay up, and will be updated by Helm.
- **Run Pods namespace** (e.g. `lunar-scripts`). This hosts the short-lived pods the operator spawns to execute cataloger, collector, and policy batches. We recommend this separate namespace because:

  * this workload is ephemeral, and can be rather "bursty" in number and resource requirements. You can tune resources and limits independently here.
  * this code is user-supplied (e.g. your plugins, scripts, third-party catalogers), not Lunar's. This is a different trust boundary, where you can tighten RBAC, egress, and resource limits independently.

Both namespaces must exist **before** `helm install`. The chart will not create the run-pods namespace for you. Point the operator at it with `operator.snippetNamespace`.

Single-namespace installs also work — leave `operator.snippetNamespace` unset and everything runs in the release namespace. This is fine for trying things out, or small setups; but is _not recommended_ for production configurations.

```bash
kubectl create namespace lunar
kubectl create namespace lunar-scripts
```

## Step 2 — Check your Kubernetes cluster

| Requirement | Detail |
|---|---|
| **Kubernetes** | 1.29 or newer. |
| **Helm** | 3.x. |
| **StorageClass** | A StorageClass must be available — your cluster default is probably fine. The chart provisions a 10 GiB `ReadWriteOnce` PVC for Hub state. You can tune details if needed via `hub.persistence.*` ([chart README](https://github.com/earthly/charts/blob/main/README.md)). |
| **Ingress controller** | Must support gRPC backend routing. See [Ingress](https://github.com/earthly/charts/blob/main/README.md#ingress) in the chart README for an NGINX-tested example. |
| **DNS** | Two hostnames pointing at your ingress controller's external IP — one for the Hub (e.g. `lunar.example.com`) and one for Grafana (e.g. `grafana.lunar.example.com`). GitHub, CI integrations, and Lunar CLI users must reach the Hub hostname; the Grafana hostname is for your team's browser access. |
| **TLS certificate** | The Hub and Grafana pods both listen plaintext. Terminate TLS at your ingress or an upstream load balancer for each hostname.|

## Step 3 — Provision PostgreSQL

Lunar needs a single PostgreSQL database. The Hub runs migrations on every startup and manages several of its own schemas (including the default `public`). We recommend that you give it a dedicated DB where its role is the owner.

| Requirement | Detail |
|---|---|
| **Version** | PostgreSQL 16 or newer. |
| **Connectivity** | Reachable from both the Hub and Operator pod's network. The chart does **not** include Postgres. |
| **Role** | Dedicated DB role for the Hub. Minimum: **database owner** (to create schemas, and grants on created objects) **plus cluster-level `CREATEROLE`** (to create a read-only `sqlapi_user` role during migration). `SUPERUSER` also works. |
| **Extensions** | Optional: `pg_stat_statements` enabled in `shared_preload_libraries`. The Hub's diagnostics bundle uses it when present. Setting `shared_preload_libraries` requires a Postgres restart (or parameter-group reboot on RDS / Cloud SQL), so it's easier to enable at provisioning time than later. |
| **Connection pool** | The Hub runs as a single replica today and opens up to 40 connections by default. Size your Postgres (or PgBouncer) accordingly. See [Scaling](hub-day2.md#scaling) in Day 2 Operations for tuning context. |
| **SSL** | The Hub negotiates TLS by default via `hub.db.connectionOptions: "sslmode=require"`. Most managed Postgres (RDS, Aurora, Cloud SQL) ships with TLS forced and will connect out of the box. Plain Postgres deployments without TLS must set `hub.db.connectionOptions: "sslmode=disable"` explicitly. **Format is libpq KV pairs, space-separated** — to pass extra options write `"sslmode=require connect_timeout=10"` (NOT `&`-separated URL query). The default is not merged in when overridden, so include `sslmode=` yourself. |
| **Backups** | Use your existing Postgres backup process; backups are your responsibility. All authoritative Hub and Operator state lives entirely in Postgres. |

{% hint style='info' %}
**Shared Postgres cluster?** Because `CREATEROLE` is a cluster-level attribute, Postgres has no mechanism to scope it to a single database. If granting it cluster-wide is too broad, pre-create the `sqlapi_user` role yourself (any password) and leave `HUB_SQLAPI_PASSWORD` unset. The migration's `IF NOT EXISTS` check skips role creation, leaving only schema-level grants — which the Hub's role can do as database owner.
{% endhint %}

## Step 4 — Provision S3-compatible object storage

Lunar needs two private S3 buckets, both writable by the Hub:

- A **Logs bucket**, which contains per-run log files. These can be short-lived; a 30-day lifecycle rule is reasonable here.
- A **Resources bucket**, which contains run-bundle archives fetched by init containers. Keep these as long as you might re-run historical catalogers, collectors, or policies.

Both buckets must block public access. Content may include credentials, user script source code, or PII surfaced from CI runs. The Hub serves all reads via time-limited pre-signed URLs.

{% hint style='warning' %}
**Object lifecycles are your responsibility.** Lunar never deletes from either bucket. Set S3 lifecycle rules yourself to cap storage growth. Check with your compliance requirements before settling on retention windows, since logs and run bundles may contain information that falls under your organization's data-retention policies.
{% endhint %}

The Hub _only_ calls `PutObject`, `GetObject`, and `HeadObject` on both buckets, and issues pre-signed `GET`/`PUT` URLs for both. Minimum IAM policy on AWS:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": [
        "arn:aws:s3:::your-logs-bucket/*",
        "arn:aws:s3:::your-resources-bucket/*"
      ]
    }
  ]
}
```

### Region and credentials

The Hub picks up AWS credentials via the standard [SDK credential chain](https://docs.aws.amazon.com/sdkref/latest/guide/standardized-credentials.html) — the chart stays out of the credentials business. Region must be set explicitly:

```yaml
hub:
  extraEnv:
    - name: AWS_REGION
      value: us-east-1
```

Common patterns (see the [chart README](https://github.com/earthly/charts/blob/main/README.md#object-storage--aws-credentials) for full YAML):

- **EKS**. Annotate the chart's service account with an [IAM role for service accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html).
- **Static credentials**. Inject `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` from a secret via `hub.extraEnv`. Not recommended for production.
- **IMDS, pod identity, external secrets operators**. All the usual AWS-SDK-friendly mechanisms work.

### Non-AWS backends

MinIO, Cloudflare R2, and GCS in S3-compatibility mode all work — set `AWS_ENDPOINT_URL_S3` via `hub.extraEnv`:

```yaml
hub:
  extraEnv:
    - name: AWS_REGION
      value: auto
    - name: AWS_ENDPOINT_URL_S3
      value: https://your-minio.example.com
```

Lunar uses virtual-host-style S3 addressing only. Most MinIO, R2, and GCS deployments handle this out of the box. Path-style-only backends aren't currently supported.

## Step 5 — Create a GitHub App

The Hub authenticates to GitHub as a GitHub App. Use our hosted setup tool to create one in a couple of clicks.

{% hint style='info' %}
**Need to create the App manually?** If your GitHub instance is air-gapped, you're using GitHub Enterprise Server, or your security review needs every permission and event laid out before the App is created, see [manual GitHub App setup](hub-github-app-manual.md) instead.
{% endhint %}

### Using the setup tool

1. Visit **[earthly.dev/lunar/github-app-setup](https://earthly.dev/lunar/github-app-setup/)**.
2. Follow the prompts. The tool uses GitHub's [manifest flow](https://docs.github.com/en/apps/creating-github-apps/setting-up-a-github-app-from-a-manifest/about-creating-github-apps-from-a-manifest) to register the App with the right permissions and events.
3. **Download the PEM private key when prompted.** GitHub shows it exactly once — if you click past this page, you'll have to generate a new key from the App settings later.
4. Click *Install App on GitHub* and select the org. Choose **All repositories** unless you have a specific reason not to — Lunar's actual monitoring scope is configured in `lunar-config.yml`, so a narrower scope here just means coming back to **Org Settings → GitHub Apps → Lunar → Repository access** every time you add a new repo to Lunar.

The hosted tool proxies the manifest exchange to GitHub and returns the credentials to your browser; we never persist them.

### Capture these before continuing

When you finish Step 5, you'll have three things — confirm you've saved all three before moving on:

| What | Source |
|---|---|
| **App ID** (numeric, e.g. `3635822`) | Setup tool result page |
| **Installation ID** (numeric) | URL after install: `https://github.com/organizations/<org>/settings/installations/<INSTALL_ID>` — the trailing number |
| **PEM private key** | Downloaded from the setup tool — **shown only once, save it now** |

For GitHub Enterprise Server, you also need to set `hub.github.baseUrl` in your values to point at your GHES instance.

## Step 6 — Plan your Kubernetes secrets

Five Kubernetes secrets come into play at install time. You create two; the chart generates the other three (with `helm.sh/resource-policy: keep`, so they survive upgrades and uninstalls).

| Secret | Who creates it | Contents |
|---|---|---|
| `lunar-db` | You | DB `username` and `password` |
| `lunar-github-app` | You | `private-key` — the PEM from Step 5 |
| `<release>-auth-token` | Chart (auto-generated) | Shared bearer token for the CLI and CI agents |
| `<release>-github-webhook` | Chart (auto-generated) | Per-repo webhook signing secret — the Hub registers this with GitHub automatically when it creates per-repo webhooks |
| `<release>-grafana-admin` | Chart (auto-generated) | Grafana admin username and password |

**GitOps alternative.** If your setup needs deterministic secret management, you can pre-create any chart-managed secret and point the chart at it (e.g. `hub.github.webhookSecret.secretName`). See the [chart README](https://github.com/earthly/charts/blob/main/README.md) for the full list of `*.secretName` values you can override.

The [install walkthrough](hub-install.md#step-3--create-kubernetes-secrets) has the exact `kubectl create secret` commands for the two user-created secrets.

## Step 7 — Size for capacity

The chart sets **no** default resource requests or limits. The numbers below are reasonable starting points, but you should monitor and adjust them based on your specific needs.

| Component | CPU request | Memory request |
|---|---|---|
| Hub | 500m | 1 Gi |
| Operator | 100m | 128 Mi |

**Run pods** are short-lived batch pods spawned by the operator. Each pod contains N **user containers** (one per script in the batch) plus an init container and a sidecar. Per-user-container resources come from `operator.snippetContainerSpec*` — the operator's built-in defaults request 250m / 256 Mi for collectors and catalogers, 50m / 128 Mi for policies.

**Batch size** is per script type via `operator.batchMaxCount*` (defaults: 10 for collectors and catalogers, 20 for policies — policies pack denser because each container is lighter). Concurrent batch pods are capped by `operator.maxConcurrent` (default `10`), shared across script types.

The run-pods namespace needs headroom for:

```
maxConcurrent × batchMaxCount(type) × per-user-container requests
```

At defaults that's ~25 GiB of concurrent-run memory per script type (10 pods × 10 collectors × 256 Mi, or 10 × 20 × 128 Mi for policies).

If you want sizing guidance once you're past initial install, please reach out.


## Next steps

When your prerequisites are in place:

- [Install walkthrough](hub-install.md) — step-by-step from zero to a working Hub.
- [Chart README](https://github.com/earthly/charts/blob/main/README.md) — complete `values.yaml` reference.
