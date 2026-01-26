# Table of contents

* [Introduction](README.md)
* [Install Lunar](install/install.md)
  * [Lunar Hub](install/hub.md)
    * [Systemd](install/systemd.md)
    * [Helm Charts](install/helm-charts.md)
  * [Lunar CLI](install/cli.md)
  * [Lunar CI Agent](install/agent.md)
  * [AI Skills](install/skills.md)
* [Learn the basics](basics/basics.md)

## 📖 Docs

* [Key concepts](key-concepts/key-concepts.md)
* [Component JSON](key-concepts/component-json.md)
* [Catalog JSON](key-concepts/catalog-json.md)
* [Lunar CLI Reference](lunar-cli/lunar-cli.md)

## 📝 Configuration

* [lunar-config.yml](lunar-config/lunar-config.md)
  * [About images](lunar-config/images.md)
  * [catalogers](lunar-config/catalogers.md)
  * [catalogers/hooks](lunar-config/cataloger-hooks.md)
  * [domains](lunar-config/domains.md)
  * [components](lunar-config/components.md)
  * [collectors](lunar-config/collectors.md)
  * [collectors/hooks](lunar-config/collector-hooks.md)
  * [policies](lunar-config/policies.md)
  * [on (tag matching)](lunar-config/on.md)
* [lunar.yml](lunar-yml/lunar-yml.md)

## 🛠️ Plugin SDKs

* [Plugins configuration](plugins/plugins.md)
  * [lunar-cataloger.yml](plugins/cataloger-plugins.md)
  * [lunar-collector.yml](plugins/collector-plugins.md)
  * [lunar-policy.yml](plugins/policy-plugins.md)
* [Bash SDK](bash-sdk/bash-sdk.md)
  * [Installing dependencies](bash-sdk/dependencies.md)
  * [Cataloger](bash-sdk/cataloger.md)
  * [Collector](bash-sdk/collector.md)
* [Python SDK](python-sdk/python-sdk.md)
  * [Installing dependencies](python-sdk/dependencies.md)
  * [Collector](python-sdk/collector.md)
  * [Policy](python-sdk/policy.md)
    * [Check](python-sdk/check.md)
    * [CheckStatus](python-sdk/check-status.md)
    * [Node](python-sdk/node.md)
    * [NoDataError](python-sdk/no-data-error.md)
    * [SkippedError](python-sdk/skipped-error.md)

## ⚙️ SQL API

* [Overview](sql-api/sql-api.md)
* Views
  * [domains](sql-api/views/domains.md)
  * [components](sql-api/views/components.md)
  * [component\_deltas](sql-api/views/component-deltas.md)
  * [initiatives](sql-api/views/initiatives.md)
  * [policies](sql-api/views/policies.md)
  * [checks](sql-api/views/checks.md)
  * [prs](sql-api/views/prs.md)
  * [catalog](sql-api/views/catalog.md)
