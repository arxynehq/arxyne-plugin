#!/usr/bin/env python3
"""Prove the plugin still points at a working MCP server, and that the server
still offers what the skill tells an agent to call.

The failure this exists to catch: the CLI renames or drops a tool, and the
plugin keeps installing happily while its skill gives instructions that no
longer resolve. Nothing in the plugin repo would notice.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

# The tools skills/arxyne/SKILL.md tells the agent to call, in the order it uses them.
REQUIRED_TOOLS = ["list_solvers", "list_products", "simulate", "get_product_results"]

# A tool name the CLI has already used for these two, so a rename is named rather than
# reported as "missing": the skill was written against these on 2026-11-10.
KNOWN_RENAMES = {
    "get_product_results": ["get_results"],
    "simulate": ["run_simulation"],
}


def rpc(stdin_write, payload):
    stdin_write.write(json.dumps(payload) + "\n")
    stdin_write.flush()


def main() -> int:
    compat = json.loads(open("compat.json", encoding="utf-8").read())
    minimum = compat["arxyne_min"]

    version = subprocess.run(
        ["arxyne", "--version"], capture_output=True, text=True, check=True
    ).stdout.strip()
    installed = version.split()[-1].lstrip("v")

    def parts(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.split(".")[:3])

    print(f"arxyne {installed} (plugin requires >= {minimum})")
    if parts(installed) < parts(minimum):
        print(f"FAIL: installed {installed} is older than the declared minimum {minimum}")
        return 1

    home = tempfile.mkdtemp(prefix="arxyne-plugin-ci-")
    env = dict(os.environ, ARXYNE_HOME=home)
    proc = subprocess.Popen(
        ["arxyne", "mcp", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert proc.stdin and proc.stdout
    try:
        rpc(
            proc.stdin,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "plugin-ci", "version": "0"},
                },
            },
        )
        rpc(proc.stdin, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        rpc(proc.stdin, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})

        tools = None
        for line in proc.stdout:
            line = line.strip()
            if not line.startswith("{"):
                continue
            msg = json.loads(line)
            if msg.get("id") == 2:
                tools = msg["result"]["tools"]
                break
    finally:
        proc.kill()

    if not tools:
        print("FAIL: the server never answered tools/list")
        return 1

    names = {t["name"] for t in tools}
    print(f"{len(names)} tools offered")

    missing = [t for t in REQUIRED_TOOLS if t not in names]
    if missing:
        for tool in missing:
            renamed = [c for c in KNOWN_RENAMES.get(tool, []) if c in names and c != tool]
            hint = f" - a tool named {renamed[0]} exists instead" if renamed else ""
            print(f"FAIL: {tool} is gone{hint}; the skill still calls it")
        return 1

    unannotated = [
        t["name"]
        for t in tools
        if not any(k in (t.get("annotations") or {}) for k in ("readOnlyHint", "destructiveHint"))
    ]
    if unannotated:
        print(f"FAIL: no readOnlyHint/destructiveHint on: {', '.join(unannotated)}")
        return 1

    print("PASS: handshake, required tools and annotations all hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
