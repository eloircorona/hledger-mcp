import os
import subprocess
from typing import Optional

from fastmcp import FastMCP

JOURNAL = os.environ.get(
    "HLEDGER_JOURNAL",
    "/home/eloircorona/Eloir/FINANCE/ledger.journal",
)

mcp = FastMCP("hledger")


def _run(args: list[str]) -> str:
    result = subprocess.run(
        ["hledger", f"--file={JOURNAL}"] + args,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "hledger error")
    return result.stdout.strip()


@mcp.tool()
def get_balance(account: Optional[str] = None, period: Optional[str] = None) -> str:
    """Show account balances. Optionally filter by account name pattern and/or period (e.g. 'this month', '2026-08', 'Q1')."""
    args = ["bal"]
    if period:
        args += ["--period", period]
    if account:
        args.append(account)
    return _run(args)


@mcp.tool()
def get_register(
    account: Optional[str] = None,
    period: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """Show transaction register (history). Optionally filter by account, period, and max number of entries."""
    args = ["reg"]
    if period:
        args += ["--period", period]
    if limit:
        args += ["--count", str(limit)]
    if account:
        args.append(account)
    return _run(args)


@mcp.tool()
def get_budget(period: Optional[str] = None) -> str:
    """Show budget report. Requires budget directives in the journal. Optionally filter by period."""
    args = ["budget"]
    if period:
        args += ["--period", period]
    return _run(args)


@mcp.tool()
def add_transaction(
    date: str,
    description: str,
    postings: list[dict],
) -> str:
    """Add a new transaction to the journal.

    Args:
        date: ISO date string, e.g. '2026-08-08'
        description: Payee/description, e.g. 'Supermercado Walmart'
        postings: List of postings. Each is {"account": "gastos:alimentacion", "amount": "850 MXN"}.
                  The last posting may omit 'amount' — hledger will auto-balance it.

    Example:
        add_transaction(
            date="2026-08-08",
            description="Supermercado",
            postings=[
                {"account": "gastos:alimentacion", "amount": "850 MXN"},
                {"account": "activos:banco:bbva"},
            ]
        )
    """
    if not postings:
        raise ValueError("postings must have at least two entries")

    lines = [f"{date} {description}"]
    for p in postings:
        acct = p.get("account", "").strip()
        amt = p.get("amount", "").strip()
        if amt:
            lines.append(f"    {acct:<40}  {amt}")
        else:
            lines.append(f"    {acct}")
    entry = "\n".join(lines) + "\n"

    with open(JOURNAL, "a") as f:
        f.write(f"\n{entry}")

    return f"Transaction added:\n{entry}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
