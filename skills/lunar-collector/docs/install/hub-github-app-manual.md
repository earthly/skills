# Manual GitHub App Setup

This page is the fallback for [prereqs Step 5](hub-prereqs.md#step-5--create-a-github-app). Most users should use [the hosted setup tool](https://earthly.dev/lunar/github-app-setup/) — it creates the App with the right permissions and events in a couple of clicks.

Use the manual flow if:

- Your GitHub instance is air-gapped or otherwise can't reach `earthly.dev` from a browser session.
- You're standing the App up against **GitHub Enterprise Server** and prefer your GHES web UI for the audit trail.
- Your security review needs explicit visibility into every permission and event before the App is created.

## Create the App

Create the App at GitHub's [App creation page](https://github.com/settings/apps/new) (or for an org: **Org Settings → Developer settings → GitHub Apps → New GitHub App**). GitHub's [registering-a-github-app docs](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app) walk through every form field if you want a reference.

For GHES, create the App on your GHES instance instead.

**Permissions:**

| Permission | Access | Why |
|---|---|---|
| `actions` | read | Read workflow runs for CI data collection |
| `checks` | write | Post policy results as PR checks |
| `contents` | read | Fetch config and source for policy evaluation |
| `metadata` | read | Required by GitHub on every App |
| `pull_requests` | write | Post PR comments and statuses |
| `repository_hooks` | write | Auto-register per-repo webhooks |
| `organization_hooks` | write | Auto-register organization-level webhooks |

**Subscribe to events:** `push`, `pull_request`, `workflow_run`.

**Other fields:**

- **Homepage URL** — any URL works (e.g. your internal Lunar URL, or `https://earthly.dev/lunar`).
- **Webhook** — uncheck "Active." The Hub registers its own per-repo webhooks at runtime; the App-level webhook is unused. URL can be a placeholder (e.g. `https://example.com/placeholder`) — GitHub requires a value but nothing will ever hit it.
- **Webhook secret** — leave blank. Since you unchecked "Active" above, GitHub won't deliver App-level events. The Hub's per-repo webhook signing secret is a separate thing — see [prereqs Step 6](hub-prereqs.md#step-6--plan-your-kubernetes-secrets).
- **Where can this app be installed?** — "Only on this account."

## After creating the App

1. **Generate a private key** (App settings → "Private keys" → "Generate a private key"). Save the `.pem` file — GitHub does not show it again.
2. **Install the App** on your organization (App settings → "Install App"). Choose **All repositories** unless you have a specific reason not to — Lunar's actual monitoring scope is configured in `lunar-config.yml`, so a narrower scope here just means coming back to this page every time you add a new repo to Lunar.

## Capture these before continuing

| What | Source |
|---|---|
| **App ID** (numeric, e.g. `3635822`) | App settings page |
| **Installation ID** (numeric) | URL after install: `https://github.com/organizations/<org>/settings/installations/<INSTALL_ID>` — the trailing number |
| **PEM private key** | Downloaded from "Generate a private key" — **shown only once, save it now** |

For GitHub Enterprise Server, you also need to set `hub.github.baseUrl` in your values to point at your GHES instance.

Return to [prereqs Step 6](hub-prereqs.md#step-6--plan-your-kubernetes-secrets) once you've captured all three.
