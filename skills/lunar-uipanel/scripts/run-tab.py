#!/usr/bin/env python3
"""Run the tabs of a uiPanels panel file the way the Lunar dashboard runs them.

Lunar does not execute tab SQL when it validates configuration, so a typo or a
missing column only shows up on the dashboard after publishing. This script
reproduces the documented view-time behavior against a live database:

  * each `:name` parameter is substituted as a quoted SQL string literal
    (`::type` casts are left alone; a parameter the caller did not supply is
    reported and left in place, which is what the dashboard does too);
  * a trailing semicolon is stripped and the SQL runs as a read-only subquery;
  * every `columns[].sqlId` (table) or `sqlId` (markdown) must be present in
    the first row;
  * table tabs are capped at 200 rows and the cap is reported when hit.

Requires python3, PyYAML and psql. The connection string defaults to the
stdout of `lunar sql connection-string` (SQL API role, `public.*` views).

Usage:
  run-tab.py uipanels/release-evidence.yml --component github.com/org/repo --sha abc1234
  run-tab.py uipanels/release-notes.yml --component ... --sha ... --param from_sha=
  run-tab.py panel.yml --component ... --sha ... --tab Evidence --conn "$DSN"
"""

import argparse
import json
import re
import subprocess
import sys

import yaml

MAX_ROWS = 200
PREVIEW_ROWS = 10
# A colon that is not part of a `::` cast and not glued to a word, followed by
# an identifier: the same grammar `lunar hub pull` validates against.
PARAM_TOKEN = re.compile(r"(?<![A-Za-z0-9_:]):([A-Za-z_][A-Za-z0-9_]*)")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("panel", help="panel YAML file")
    p.add_argument("--component", help="value for :component")
    p.add_argument("--sha", help="value for :sha")
    p.add_argument("--param", action="append", default=[], metavar="NAME=VALUE",
                   help="any other parameter, e.g. from_sha= (repeatable)")
    p.add_argument("--tab", help="run only the tab with this name")
    conn = p.add_mutually_exclusive_group()
    conn.add_argument("--conn", help="PostgreSQL connection string")
    conn.add_argument("--grafana", action="store_true",
                      help="use `lunar sql connection-string --grafana` (admins)")
    return p.parse_args()


def collect_params(args):
    params = {}
    if args.component is not None:
        params["component"] = args.component
    if args.sha is not None:
        params["sha"] = args.sha
    for item in args.param:
        name, sep, value = item.partition("=")
        if not sep or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            sys.exit(f"--param expects NAME=VALUE, got {item!r}")
        params[name] = value
    return params


def resolve_dsn(args):
    if args.conn:
        return args.conn
    cmd = ["lunar", "sql", "connection-string"] + (["--grafana"] if args.grafana else [])
    try:
        out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    except FileNotFoundError:
        sys.exit("lunar CLI not found; pass --conn")
    except subprocess.CalledProcessError as e:
        sys.exit(f"{' '.join(cmd)} failed:\n{e.stderr.strip()}")
    dsn = out.strip()
    if not dsn:
        sys.exit(f"{' '.join(cmd)} printed nothing; pass --conn")
    return dsn


def load_tabs(path, only):
    try:
        with open(path, encoding="utf-8") as f:
            panel = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        sys.exit(f"{path}: {e}")
    tabs = (panel or {}).get("tabs") or []
    if not tabs:
        sys.exit(f"{path}: no tabs declared")
    if only is not None:
        tabs = [t for t in tabs if t.get("name") == only]
        if not tabs:
            sys.exit(f"{path}: no tab named {only!r}")
    return tabs


def quote_literal(value):
    """PostgreSQL quote_literal(): 'it''s', or E'...' when a backslash is present."""
    escaped = value.replace("'", "''")
    if "\\" in escaped:
        return "E'" + escaped.replace("\\", "\\\\") + "'"
    return "'" + escaped + "'"


def substitute(sql, params, used):
    """Replace every supplied `:name` in one pass; leave unknown tokens as they are."""
    unknown = []

    def repl(m):
        name = m.group(1)
        if name in params:
            used.add(name)
            return quote_literal(params[name])
        unknown.append(name)
        return m.group(0)

    return PARAM_TOKEN.sub(repl, sql), sorted(set(unknown))


def run_sql(dsn, sql):
    wrapped = (
        "SELECT coalesce(json_agg(to_json(t)), '[]'::json) "
        f"FROM (SELECT * FROM ({sql}\n) uipanel_q LIMIT {MAX_ROWS + 1}) t"
    )
    proc = subprocess.run(
        ["psql", dsn, "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-f", "-"],
        input=wrapped, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"psql exited {proc.returncode}")
    return json.loads(proc.stdout)


def declared_columns(tab):
    if tab.get("type") == "markdown":
        return [tab.get("sqlId")]
    return [c.get("sqlId") for c in tab.get("columns") or []]


def run_tab(tab, params, dsn, used):
    name = tab.get("name", "<unnamed>")
    sql = (tab.get("sql") or "").strip().rstrip(";").strip()
    sql, unknown = substitute(sql, params, used)
    if unknown:
        print(f"[{name}] parameter(s) not supplied, left as-is: " + ", ".join(":" + u for u in unknown))
    try:
        rows = run_sql(dsn, sql)
    except (RuntimeError, ValueError) as e:
        print(f"[{name}] ERROR: {e}")
        return False

    if rows:
        missing = [c for c in declared_columns(tab) if c not in rows[0]]
        if missing:
            print(f"[{name}] ERROR: column(s) not in the query result: {', '.join(missing)}")
            return False

    if tab.get("type") == "markdown":
        if not rows:
            print(f"[{name}] markdown: 0 rows, the tab renders empty")
        else:
            print(f"[{name}] markdown:")
            print(rows[0].get(tab.get("sqlId")) or "")
        return True

    truncated = len(rows) > MAX_ROWS
    rows = rows[:MAX_ROWS]
    note = f" (truncated: the dashboard shows the first {MAX_ROWS})" if truncated else ""
    print(f"[{name}] table: {len(rows)} row(s){note}")
    if not rows:
        print(f"[{name}] warning: 0 rows; expected? check the (:component, :sha) filter")
    for row in rows[:PREVIEW_ROWS]:
        print("  " + json.dumps(row, ensure_ascii=False))
    if len(rows) > PREVIEW_ROWS:
        print(f"  ... {len(rows) - PREVIEW_ROWS} more")
    return True


def main():
    args = parse_args()
    params = collect_params(args)
    tabs = load_tabs(args.panel, args.tab)
    dsn = resolve_dsn(args)

    used = set()
    ok = True
    for tab in tabs:
        ok &= run_tab(tab, params, dsn, used)

    unused = sorted(set(params) - used)
    if unused and args.tab is None:
        print("warning: no tab references " + ", ".join(":" + u for u in unused)
              + "; the dashboard would show the same rows for every value")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
