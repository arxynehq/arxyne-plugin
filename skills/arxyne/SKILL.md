---
name: arxyne
description: Run an engineering simulation and read its result with the Arxyne CLI. Use when the user asks to run a CFD, structural, crash, thermal, acoustic or electromagnetic case, asks which solvers or products are available, or wants the numbers and provenance of a previous run.
---

# Arxyne

Arxyne runs a simulation on this machine and keeps a record of it. The tools
come from the local `arxyne` MCP server.

## Find out what can run

1. Call `list_solvers` to see the solvers this machine can dispatch, with the
   domains they cover and the products each one declares.
2. Call `list_products` to see the products, and which solvers can run each.

Choose a product and a solver that declares it. If the user named neither, ask
which they want rather than guessing: a run pulls a large image and takes real
time.

## Run a case

1. Call `simulate` with the product name, the solver, and any settings the user
   asked to change. Omit everything else and the product's own defaults apply.
2. Report what the run produced: the KPIs it returned, and the gate verdict if
   the product declares a target. A gate that misses is a result, not a failure
   of the run — say which number missed and by how much.

## Read a past run

Call `get_results` for the product to get the recorded KPIs and provenance for
each run. Quote the values as recorded. Do not recompute, round differently, or
describe a value the record does not carry.

## Say what happened

If a dispatch fails, report the error the tool returned and stop. Do not retry
with a different solver or product unless the user asks: the error is usually
about the machine (Docker not running, image not pulled) or about a setting the
product does not declare.
