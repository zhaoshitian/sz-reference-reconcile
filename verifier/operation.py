from dataclasses import asdict

from .checks import destination_problem, encoded, identifier, result, safe_path


def input_problem(v):
    problem = destination_problem(v.destination)
    if problem:
        return problem
    for source in (v.bank, v.ledger):
        if len(source) > 200 or len({r.entry_id for r in source}) != len(source):
            return "entry count exceeds 200 or entry identifiers are duplicated within a source"
        if any(
            not identifier(r.entry_id) or not identifier(r.reference) or not -1000000000 <= r.cents <= 1000000000
            for r in source
        ):
            return "invalid entry identifier, reference, or amount"
    return None


def verify_input(value):
    problem = input_problem(value)
    return result(not problem, problem or "input is valid")


def expected(v):
    refs = sorted({r.reference for r in v.bank + v.ledger})
    rows = []
    for ref in refs:
        b = [r.cents for r in v.bank if r.reference == ref]
        l = [r.cents for r in v.ledger if r.reference == ref]
        rows.append(
            {
                "reference": ref,
                "bank_present": bool(b),
                "ledger_present": bool(l),
                "bank_cents": sum(b),
                "ledger_cents": sum(l),
                "difference_cents": sum(b) - sum(l),
            }
        )
    return rows, sum(abs(r["difference_cents"]) for r in rows)


def verify_output(input_value, output_value, workspace):
    problem = input_problem(input_value)
    if problem:
        return result(False, problem)
    rows, total = expected(input_value)
    actual = [asdict(r) for r in output_value.records]
    if actual != rows or output_value.total != total:
        return result(False, "returned rows or total do not match the task rules")
    if output_value.path != input_value.destination:
        return result(False, "returned path does not match destination")
    path = safe_path(workspace, input_value.destination)
    if path is None or not path.is_file():
        return result(False, "artifact is missing, is a symlink, or escapes the workspace")
    try:
        content = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError):
        return result(False, "artifact cannot be read as UTF-8")
    if content != encoded(rows, total):
        return result(False, "artifact is not the exact canonical JSON result")
    return result(True, "verified rows, total, destination, and artifact bytes", rows=len(rows), total=total)


def verify_task(arguments, output, reference, workspace):
    return verify_output(arguments, output, workspace)
