# Reference Reconcile

Reconcile two signed integer-cent transaction lists by reference while retaining zero-net and one-sided references.

## Tools

- `reconcile_entries` accepts `TaskInput` and returns `TaskOutput`.
- `reconcile-entries` is a `runner: tool` task using `reconcile_entries`. It requires no model or external service. A RUSH Lab agent can select the task from its structured interface.

### Exact success conditions

Group by exact case-sensitive reference. Keep the union of references, including zero-net groups. Presence reflects entries, not net amount. difference_cents=bank_cents-ledger_cents. Sort by reference. total is the sum of absolute differences.

The tool creates a new file at `destination`. The exact file format is UTF-8 JSON of `{"records": [...], "total": integer}`, sorted object keys, compact separators `(',', ':')`, ASCII escapes, and one final newline. Returned records, total, and destination must match the file and the independently computed answer. A matching claim without a matching file fails. Existing files are never overwritten. Paths must be canonical relative `.json` paths, at most 200 characters, with identifier-style directories and filename stems; symlinks are rejected. Identifiers match `[A-Za-z0-9][A-Za-z0-9_-]{0,31}`. Input sizes and numeric bounds are declared in `contract.py` and enforced in `verifier/operation.py`.

The tool accumulates two sums and presence flags in one pass. The verifier filters each source independently for every reference and recomputes all sums.

### Example input

```json
{
  "destination": "results/out.json",
  "bank": [
    {
      "entry_id": "b1",
      "reference": "A",
      "cents": 100
    },
    {
      "entry_id": "b2",
      "reference": "A",
      "cents": -20
    },
    {
      "entry_id": "b3",
      "reference": "B",
      "cents": 0
    }
  ],
  "ledger": [
    {
      "entry_id": "l1",
      "reference": "A",
      "cents": 75
    },
    {
      "entry_id": "l2",
      "reference": "C",
      "cents": -30
    }
  ]
}
```

## Layout

- `contract.py`: typed schemas and tool/task tables.
- `nanoagent.yaml`: tool runner, no network hosts, workspace-only writes.
- `src/plugin/`: MCP runtime and deterministic implementation.
- `verifier/`: independent deterministic checks; no LLM, clock, network, randomness, or writes.
- `tests/test_verifier.py`: known answers, adversarial outputs, boundaries, malformed inputs, artifact changes, and safe paths.
- `ui/` and `product/`: result schema rendering and marketplace presentation.
- `uv.lock`: pinned dependency versions and Git revision of slimconfig.

## Develop and run

Requires Python 3.12 or later, Git, uv, and NanoAgent implementing `nanoagent.plugin/v0001` (tested with the RUSH Lab bundled CLI). First-time dependency installation requires the package index and GitHub; execution requires no network or environment secrets.

```sh
uv sync --frozen --extra dev
uv run --frozen pytest -q
uv run --frozen ruff check .
uv lock --check
rushlab nanoagent plugin inspect .
```

To run: save the example as `/absolute/path/input.json`, then create a YAML file outside the repository:

```yaml
_ > nanoagent.cli.plugin.PluginRunConfig:
plugin: /absolute/path/sz-reference-reconcile
task: reconcile-entries
arguments: /absolute/path/input.json
inputs: []
timeout: 60.0
```

Run `rushlab nanoagent plugin run config=/absolute/path/run.yaml home=/absolute/path/new-run-folder`.
The new run folder contains `workspace/results/out.json`, `result.json`, and `verdict.json`. A successful verifier returns `valid: true` and `score: 1.0`. Use a fresh run folder and destination for each run. Evidence and validation logs belong in the milestone report, outside this repository.

Limitations: Exact reference matching and integer cents only; no fuzzy matching, currencies, fees, accounting policy, or external bank access.
