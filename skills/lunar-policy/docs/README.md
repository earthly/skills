# Earthly Lunar

Earthly Lunar is a platform for monitoring and enforcing engineering practices across your organization's software development lifecycle.

Lunar works by instrumenting your existing CI/CD pipelines (no YAML changes needed) and source code repositories to collect structured metadata about how code is built, tested, scanned, and deployed. This metadata is then continuously evaluated against policies that you define—policies that are flexible, testable, and expressive enough to reflect your real-world engineering standards.

Want to block deployments that would violate compliance rules, like using unapproved licenses or bypassing required security scans? Or fail a PR if it introduces stale dependencies or vulnerable CI plugins? Or ensure that security-sensitive services are collecting SBOMs, running code scans, and deploying frequently enough to avoid operational drift? Lunar makes all of that possible—without requiring a wholesale rewrite of every team's CI pipeline, and without sacrificing developer velocity.

Lunar is designed to work with the messy reality of modern engineering. It's not a one-size-fits-all template. Its instrumentation is flexible and centralized—meaning platform teams stay in control, app teams stay autonomous, and standards actually get enforced.

## Overview

Earthly Lunar helps organizations maintain high engineering standards by:

- Monitoring components (services, libraries, repositories) across your organization
- Collecting metadata about your software development lifecycle
- Enforcing policies and best practices
- Providing visibility into engineering health through checks

## Key Features

* **Component Monitoring**: Track the health and status of individual software components
* **SDLC Instrumentation**: Collect data from various stages of your software development lifecycle
* **Policy Enforcement**: Define and enforce engineering standards across your organization
* **Flexible Integration**: Works with existing CI/CD pipelines and tools
* **Extensible Platform**: Create custom collectors and policies using Bash or Python SDKs
* **SQL API**: Query and analyze your engineering data

## AI Skills

To get started quickly with developing guardrails, see the [AI skills](install/skills.md) compatible with Claude Code, Codex, and Cursor.

## Getting Started

1. [Learn the basics](basics/basics.md)
2. [Install Lunar](install/install.md)
3. [Understand key concepts](key-concepts/key-concepts.md)
