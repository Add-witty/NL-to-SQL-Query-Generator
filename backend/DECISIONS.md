### Decision

Use a single internal Schema model regardless of input source.

Reason

Allows every parser (CSV, XLSX, SQLite, SQL) to produce the same output consumed by the Prompt Builder.

---

### Decision

Use sqlglot for SQL parsing and validation.

Reason

More reliable than regex parsing and supports multiple SQL dialects.

---

### Decision

The MVP will be stateless.

Reason

Uploaded files are processed, converted into a Schema object, and discarded immediately after SQL generation.

---

### Decision

The initial version supports single-turn query generation only.

Reason

Conversation memory will be added in a later phase.

#### Decision

Adopt a single internal `Schema` model as the common representation for all supported input sources (CSV, XLSX, SQLite, SQL schema).

#### Reason

All schema extractors should produce the same output format so downstream modules (Prompt Builder, Validator, LLM Service) remain independent of the input source.

#### Included Fields

- Schema

- Table

- Column

- Data type

- Primary key

- Foreign key

- References

- Source type

#### Deferred

- Nullable flag

- Constraints

- Indexes

- Sample data

- Column descriptions

These can be added later without breaking existing extractors.

---

### Decision

The `POST /upload` endpoint reads the entire uploaded file into memory and parses it synchronously with `pandas.read_csv`, capped at a 10MB file size limit. File type is validated by extension (`.csv`), not by the client-supplied `Content-Type` header.

### Reason

This keeps the endpoint stateless and simple for the MVP (consistent with the "stateless MVP" decision above): no temp files, no streaming parser. `Content-Type` from browsers/clients is unreliable for CSV, so the extension check is the primary gate; actual parseability is still verified by pandas and surfaced as a 400 on failure. The 10MB cap bounds memory usage until a streaming or chunked-upload approach is needed for larger files.

### Decision

CSV-derived schemas never set `is_primary_key=True` or populate `foreign_keys`, even heuristically (e.g. a column named `id`).

### Reason

CSV files carry no real constraint metadata. Guessing keys from naming conventions risks the LLM later generating SQL (e.g. JOINs) based on a relationship that doesn't actually exist. This is consistent with the project's "never invent columns or table names" rule extended to constraints.