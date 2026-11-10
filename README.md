# Arxyne

Run engineering simulations from a conversation, on your own machine.

Arxyne dispatches a solver, records the run, and reads the result back. Eleven
solvers ship: OpenFOAM, XLB and SU2 for aerodynamics, DoMINO as an ML surrogate,
Chrono for vehicle dynamics, CalculiX for structures, Palace for
electromagnetics, OpenCourant for crash, OpenLB and openCFS for acoustics, and
Elmer for thermal multiphysics. Each run carries a record — the case, the
container and its version — so a number can be recomputed later.

## Install

In Claude Code:

```
/plugin install arxyne --marketplace arxynehq/arxyne-plugin
```

Then install the CLI, which the plugin calls. It is a separate install:

```bash
pip install arxyne
arxyne --version
```

Arxyne runs solver containers with Docker, so Docker must be installed and
running. The first run of a solver pulls its image, which is large; a 2D case is
the cheap way to start.

## Use it

Ask for a simulation in plain language — a product, a solver and any settings
you want to change:

- "Run Ahmed body on OpenFOAM and tell me the drag coefficient."
- "Which solvers can I use?"
- "Read back the results of my last run."

Claude calls your local `arxyne` MCP server. It can list solvers and
products, dispatch a run, and read results and provenance. Runs execute locally
in Docker and are stored under `~/.arxyne/`. Nothing is sent to Arxyne: there is
no Arxyne account, no API key, and no service to reach.

Full documentation: <https://docs.arxyne.com>

## Checks

A daily workflow (`check.yml`) validates the manifest and runs a live
handshake against the latest `arxyne` on PyPI, so a CLI change that breaks
the plugin's tools is caught here before it reaches a customer.

## Data

The plugin sends nothing off your machine. Tool calls go to a local process
(`arxyne mcp stdio`); the CLI writes run records to `~/.arxyne/` and dispatches
Docker containers locally. Solver images are pulled from `ghcr.io` on first use,
which reveals to GitHub only that an image was fetched.

## Licence

Business Source License 1.1. See `LICENSE`. The CLI is free for any use,
including production, provided you do not use it to offer a competing
simulation-orchestration product or service.
