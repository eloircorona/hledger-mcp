# hledger-mcp

MCP server for [hledger](https://hledger.org) — exposes double-entry accounting tools to AI agents via the [Model Context Protocol](https://modelcontextprotocol.io).

Built with [fastmcp](https://gofastmcp.com).

## Tools

| Tool | Description |
|---|---|
| `get_balance` | Account balances, optionally filtered by account and period |
| `get_register` | Transaction history, optionally filtered by account, period, and limit |
| `get_budget` | Budget report (requires `budget` directives in the journal) |
| `add_transaction` | Append a new transaction to the journal |

## Requirements

- Python 3.11+
- [hledger](https://hledger.org/install.html) installed and on `PATH`
- [uv](https://docs.astral.sh/uv/) (for `uvx` invocation)

## Usage

### Run directly with uvx

```bash
uvx --from /path/to/hledger-mcp hledger-mcp
```

### Add to Claude Code / orbit mcp.json

```json
{
  "mcpServers": {
    "hledger": {
      "command": "uvx",
      "args": ["--from", "/path/to/hledger-mcp", "hledger-mcp"]
    }
  }
}
```

### Journal path

By default, the server reads and writes to `~/hledger.journal`. Override with the `HLEDGER_JOURNAL` environment variable:

```bash
HLEDGER_JOURNAL=/path/to/my.journal uvx --from /path/to/hledger-mcp hledger-mcp
```

Or in `mcp.json`:

```json
{
  "mcpServers": {
    "hledger": {
      "command": "uvx",
      "args": ["--from", "/path/to/hledger-mcp", "hledger-mcp"],
      "env": {
        "HLEDGER_JOURNAL": "/home/user/finance/ledger.journal"
      }
    }
  }
}
```

## Tool reference

### `get_balance`

Returns the balance report (`hledger bal`).

```
get_balance(account="gastos", period="this month")
get_balance(account="activos:banco")
get_balance()
```

| Param | Type | Description |
|---|---|---|
| `account` | `str` (optional) | Account name pattern to filter |
| `period` | `str` (optional) | Period expression: `"this month"`, `"2026-08"`, `"Q1"`, `"last year"`, etc. |

### `get_register`

Returns the register report (`hledger reg`).

```
get_register(account="gastos:alimentacion", period="this month")
get_register(limit=20)
```

| Param | Type | Description |
|---|---|---|
| `account` | `str` (optional) | Account name pattern to filter |
| `period` | `str` (optional) | Period expression |
| `limit` | `int` (optional) | Max number of entries to return |

### `get_budget`

Returns the budget report (`hledger budget`). Requires `~ monthly` or similar budget directives in your journal.

```
get_budget(period="this month")
```

| Param | Type | Description |
|---|---|---|
| `period` | `str` (optional) | Period expression |

### `add_transaction`

Appends a transaction to the journal file.

```python
add_transaction(
    date="2026-08-08",
    description="Supermercado Walmart",
    postings=[
        {"account": "gastos:alimentacion", "amount": "850 MXN"},
        {"account": "activos:banco:bbva"},   # no amount — hledger auto-balances
    ]
)
```

| Param | Type | Description |
|---|---|---|
| `date` | `str` | ISO date: `"2026-08-08"` |
| `description` | `str` | Payee or description |
| `postings` | `list[dict]` | List of `{"account": str, "amount": str}`. Last entry may omit `amount`. |

The resulting journal entry:

```
2026-08-08 Supermercado Walmart
    gastos:alimentacion                       850 MXN
    activos:banco:bbva
```

## Account conventions (hledger standard)

```
activos:      assets  (bank, cash, investments)
pasivos:      liabilities  (credit cards, loans)
ingresos:     income  (salary, freelance)
gastos:       expenses  (food, transport, rent)
patrimonio:   equity  (opening balances)
```

## Development

```bash
git clone git@github.com:eloircorona/hledger-mcp.git
cd hledger-mcp
uv sync
uv run hledger-mcp
```

## License

MIT
