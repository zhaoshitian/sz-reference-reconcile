from slimconfig import build_output

from contract import TaskOutput
from verifier.checks import encoded, safe_path
from verifier.operation import verify_input


def solve(v):
    grouped = {}
    for side, source in enumerate((v.bank, v.ledger)):
        for entry in source:
            if entry.reference not in grouped:
                grouped[entry.reference] = [False, False, 0, 0]
            grouped[entry.reference][side] = True
            grouped[entry.reference][side + 2] += entry.cents
    rows = []
    for ref, (bp, lp, b, l) in sorted(grouped.items()):
        rows.append(
            {
                "reference": ref,
                "bank_present": bp,
                "ledger_present": lp,
                "bank_cents": b,
                "ledger_cents": l,
                "difference_cents": b - l,
            }
        )
    return rows, sum(abs(r["difference_cents"]) for r in rows)


def operate(value, workspace):
    verdict = verify_input(value)
    if not verdict["valid"]:
        raise ValueError(verdict["message"])
    path = safe_path(workspace, value.destination)
    if path is None:
        raise ValueError("destination crosses a symlink or leaves the workspace")
    rows, total = solve(value)
    output = build_output({"path": value.destination, "records": rows, "total": total}, TaskOutput)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded(rows, total))
    return output
