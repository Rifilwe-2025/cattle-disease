# MCP Server — Cattle Disease Prediction

An [MCP](https://modelcontextprotocol.io) server that exposes this Django project's
trained ML model and case database as tools an AI client can call directly.

Server name: `cattle-disease`. Transport: **stdio**.

## Files

| File | Purpose |
|---|---|
| `server.py` | Tool definitions and the `FastMCP` app |
| `django_bootstrap.py` | Boots Django outside `manage.py` so tools can use the ORM |
| `__init__.py` | Package marker |

Configuration lives in `.mcp.json` at the project root.

## Tools

### Prediction (no database needed)

| Tool | What it does |
|---|---|
| `predict_disease` | Runs the trained model on a symptom list + herd context. Returns the predicted disease, confidence, top-3 candidates, severity and treatment recommendations. |
| `list_symptoms` | The 93 symptom codes the model accepts. |
| `list_diseases` | The 26 predictable diseases with their severity ratings. |
| `model_info` | Model identity and metrics (accuracy, F1, CV scores, feature counts). |

### Data — all read-only

| Tool | What it does |
|---|---|
| `list_cases` | Cases newest-first, filterable by status, severity and province. |
| `get_case` | One case in full, including the vet's diagnosis and ranked predictions. |
| `list_farmers` | Registered farmers with location, herd details and case counts. |
| `list_vets` | Approved vets, provinces served, availability and workload. |
| `system_stats` | Whole-system summary — case counts by status/severity, top diseases, user totals. |
| `disease_stats_by_province` | Outbreak view: cases broken down by province and disease. |

No tool writes to the database. The MCP server cannot create cases or modify
diagnoses — that stays in the web UI.

## Usage

The server is registered in `.mcp.json`, so Claude Code picks it up
automatically when started from the project root. Check it with `/mcp`.

To run it by hand (it will wait on stdin for MCP protocol messages — that's
correct behaviour, not a hang):

```powershell
venv\Scripts\python.exe -m mcp_server.server
```

### Other MCP clients

For Claude Desktop, add this to its config, using absolute paths:

```json
{
  "mcpServers": {
    "cattle-disease": {
      "command": "C:\\Users\\RifilweMbengo\\Desktop\\Early Disease Prediction For Cattle\\venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\Users\\RifilweMbengo\\Desktop\\Early Disease Prediction For Cattle"
    }
  }
}
```

## Notes

- `predict_disease` works without a database connection; the data tools need
  PostgreSQL running (see `DATABASES` in `cattle_disease_system/settings.py`).
- Unknown symptom codes are not an error — they come back in `unknown_symptoms`
  and are ignored by the model, so a partial match still yields a prediction.
- `SYMPTOM_COLS` in `server.py` mirrors the list in
  `ml_engine/services.py:predict_disease`. If the model is retrained with
  different features, update both.
