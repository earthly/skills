---
description: Overview of Lunar installation, covering Hub, CLI, CI Agent for self-hosted and managed runners, and AI skills for building plugins.
---

# Installing Lunar

Welcome to the Lunar installation guide.

This section contains step-by-step instructions for installing Lunar. Install these pieces, in this order:

1. **Lunar Hub** – the central coordination service.
   - [Overview](hub-overview.md) – the lay of the land: services, dependencies, ports.
   - [Prerequisites](hub-prereqs.md) – what to have in place before `helm install`.
   - [Install walkthrough](hub-install.md) – step-by-step from zero to a working Hub.
   - [Day-2 operations](hub-day2.md) – upgrades, secret rotation, observability, uninstall.
2. **Lunar CLI** – an admin and development CLI.
   - [Install the Lunar CLI](cli.md)
3. **Lunar CI Agent** — instruments your CI runners to report data to the Hub. Choose based on how your CI is set up:
   - [Self-hosted runners](agent-self-hosted.md)
   - [GitHub-hosted managed runners](agent-managed.md) (the [earthly/lunar-ci-action](https://github.com/earthly/lunar-ci-action)).

Optional:

- [`sync-config` GitHub Action](github-actions.md) – pushes your config repo to Lunar Hub on every push.
- [AI Skills](skills.md) – agent skills for building collectors and policies.

Want to try Lunar without installing anything? Get in touch for a guided demo or preview.

<a href="https://earthly.dev/earthly-lunar/demo" class="button primary" data-icon="calendar">Request a demo</a>

Before diving in, browse the [100+ pre-built guardrails](https://earthly.dev/lunar/guardrails/) and [30+ integrations](https://earthly.dev/lunar/integrations/) available out of the box.
