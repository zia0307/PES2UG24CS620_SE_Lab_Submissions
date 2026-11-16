"""Library fine and book renewal tracker for a campus library.

Records which student has borrowed which book, works out overdue fines,
handles renewals and saves the loan records to ``loans.json``.
"""
import ast
import json
import operator
from datetime import datetime

# Global state
loans = {}
FINE_PER_DAY = 2

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}


def add_book_loan(student_id, book_id, dates=None):
    """Record that ``student_id`` borrowed ``book_id``.

    Returns True if the loan was recorded, False if the input was rejected.
    """
    if not student_id:
        print("Rejected loan: missing student id")
        return False
    if not isinstance(book_id, str) or not book_id:
        print(f"Rejected loan for {student_id}: book id must be a "
              f"non-empty string, got {book_id!r}")
        return False
    if dates is None:
        dates = []
    dates.append(str(datetime.now()))
    loans[student_id] = loans.get(student_id, []) + [book_id]
    print(f"{student_id} borrowed {book_id} "
          f"(loan dates on record: {len(dates)})")
    return True


def return_book(student_id, book_id):
    """Remove ``book_id`` from the student's loans, if it is on record.

    Returns True if the book was returned, False if there was no such loan.
    """
    try:
        loans[student_id].remove(book_id)
    except (KeyError, ValueError):
        print(f"Cannot return {book_id}: {student_id} has no such loan")
        return False
    if not loans[student_id]:
        del loans[student_id]
    return True


def calculate_fine(days_overdue):
    """Return the fine for a book that is ``days_overdue`` days late.

    A book that is not overdue (zero or negative days) costs nothing.
    """
    return max(days_overdue, 0) * FINE_PER_DAY


def renew_book(student_id, book_id, extra_days):
    """Renew ``book_id`` for ``student_id`` by ``extra_days`` days.

    Renewing never changes the fine rate, which is shared by every loan.
    Returns True if the renewal went through, False otherwise.
    """
    if book_id not in loans.get(student_id, []):
        print(f"Cannot renew {book_id}: {student_id} has not borrowed it")
        return False
    if extra_days <= 0:
        print(f"Cannot renew {book_id}: extra days must be positive")
        return False
    print(f"Renewed {book_id} for {student_id} by {extra_days} days")
    return True


def load_records(file="loans.json"):
    """Replace the in-memory loans with the records stored in ``file``."""
    try:
        with open(file, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        print(f"No saved records found at {file}; starting empty")
        data = {}
    loans.clear()
    loans.update(data)


def save_records(file="loans.json"):
    """Write the current loans to ``file`` as JSON."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(loans, handle)


def _eval_node(node, days):
    """Evaluate a parsed fine-rule expression using only safe operations."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, days)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id == "days":
        return days
    if isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.UAdd, ast.USub)):
        value = _eval_node(node.operand, days)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        left = _eval_node(node.left, days)
        right = _eval_node(node.right, days)
        return _ALLOWED_OPS[type(node.op)](left, right)
    raise ValueError("Unsupported expression in fine rule")


def fine_from_rule(rule, days):
    """Evaluate a fine rule such as ``"days * 2 + 10"`` for ``days`` days.

    Only numbers, the name ``days`` and + - * / // % are allowed (no eval).
    """
    try:
        tree = ast.parse(rule, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid fine rule: {rule!r}") from exc
    return _eval_node(tree, days)


def print_report():
    """Print every student and the books they currently have on loan."""
    print("Loan Report")
    for student_id, books in loans.items():
        print(student_id, "->", books)


def read_days_overdue():
    """Ask how many days overdue S102 is; fall back to 0 on bad input."""
    raw = input("Days overdue for S102 (press Enter for 0): ").strip() or "0"
    try:
        return int(raw)
    except ValueError:
        print(f"'{raw}' is not a whole number; using 0")
        return 0


def main():
    """Run the demo: a few loans, a renewal, fines, then save and reload."""
    add_book_loan("S101", "B-ALGO")
    add_book_loan("S102", "B-NETW")
    add_book_loan("", "B-DBMS")
    add_book_loan("S103", 4521)  # book id should be a string
    return_book("S999", "B-NONE")
    renew_book("S101", "B-ALGO", 21)
    print("Fine for 5 days:", calculate_fine(5))
    print("Fine for -3 days:", calculate_fine(-3))
    print("Fine via rule:", fine_from_rule("days * 2 + 10", 4))
    print("S102 owes:", calculate_fine(read_days_overdue()))
    save_records()
    load_records()
    print_report()


if __name__ == "__main__":
    main()
