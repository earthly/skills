---
description: Use the Lunar sync-config GitHub Action to push your config repo to Lunar Hub on every push.
---

# `sync-config` GitHub Action

The [`earthly/lunar-actions/sync-config`](https://github.com/earthly/lunar-actions/tree/main/sync-config) action pushes the latest config (manifest + snippets) from your config repo into Lunar Hub. Run it on every push to your config repo's primary branch so the hub stays in sync.

{% hint style="info" %}
**First time setting up a config repo?** Fork [`earthly/lunar-config-template`](https://github.com/earthly/lunar-config-template) — it ships with this workflow pre-wired so you only need to set the `LUNAR_HUB_TOKEN` secret and push.
{% endhint %}

## How it works

`sync-config` is a thin wrapper around the [`lunar hub pull`](../lunar-cli/lunar-cli.md#lunar-hub-pull) CLI command. The action's inputs map 1:1 to the equivalent CLI flags — see the [CLI reference](../lunar-cli/lunar-cli.md) for the full semantics of each.

## Example

```yaml
name: Sync Lunar Config

on:
  push:
    branches: [main]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: earthly/lunar-actions/sync-config@main
        with:
          manifest-url: github://my-org/my-config-repo@main
          hub-token: ${{ secrets.LUNAR_HUB_TOKEN }}
          hub-host: hub.example.com
          lunar-version: v1.1.1
          rerun-code-collectors: "true"
```

## Inputs

| Input | Required | Default | CLI equivalent |
| --- | --- | --- | --- |
| `manifest-url` | yes | — | `<repo>` positional argument (`github://<org>/<repo>@<branch>`) |
| `hub-token` | yes | — | `LUNAR_HUB_TOKEN` env var |
| `hub-host` | yes | — | `LUNAR_HUB_HOST` env var |
| `lunar-version` | yes | — | Selects the [`lunar-dist`](https://github.com/earthly/lunar-dist/tags) release to download |
| `hub-grpc-port` | no | `443` | `LUNAR_HUB_GRPC_PORT` env var |
| `hub-http-port` | no | `443` | `LUNAR_HUB_HTTP_PORT` env var |
| `rerun-code-collectors` | no | `false` | `--rerun-code-collectors` / `-l` |
| `include-pr-commits` | no | `false` | `--include-pr-commits` |
| `pr-max-age-days` | no | `5` | `--pr-max-age-days` |
| `rerun-catalogers` | no | `false` | `--rerun-catalogers` / `-t` (requires lunar `v1.1.2+` — see [`lunar hub pull`](../lunar-cli/lunar-cli.md#lunar-hub-pull)) |
| `log-level` | no | `debug` | `LUNAR_LOG_LEVEL` env var |

{% hint style="info" %}
By default, pulling the config does **not** rerun catalogers or code collectors. Set `rerun-catalogers: "true"` or `rerun-code-collectors: "true"` to opt in. Per-component catalogers (`component-repo`, `component-cron`) are unaffected by these flags and continue to run on their own hooks.
{% endhint %}

## Versioning

Pin to `@main` for the latest, or to a release tag for stability. The `lunar-version` input selects the CLI version that gets downloaded; check the [`lunar-dist` releases](https://github.com/earthly/lunar-dist/tags) for the latest stable tag.
