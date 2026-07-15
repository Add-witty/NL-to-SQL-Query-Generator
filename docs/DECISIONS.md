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

---

### Decision

Adopt a single internal `Schema` model as the common representation for all supported input sources (CSV, XLSX, SQLite, SQL schema).

Reason

All schema extractors should produce the same output format so downstream modules (Prompt Builder, Validator, LLM Service) remain independent of the input source.

Included Fields

- Schema
- Table
- Column
- Data type
- Primary key
- Foreign key
- References
- Source type

Deferred

- Nullable flag
- Constraints
- Indexes
- Sample data
- Column descriptions

These can be added later without breaking existing extractors.

---

### Decision

The CSV schema extractor never infers primary keys or foreign keys, including from naming conventions such as `id` or `*_id`. Every column it produces has `is_primary_key=False`, `is_foreign_key=False`, `references=None`.

Reason

CSV files carry no constraint or relationship metadata. Inferring keys from column names would be hallucinated schema information that the Prompt Builder and LLM could rely on as if it were fact. Key/relationship data is only ever populated by extractors for formats that actually declare it (SQLite, SQL schema).

---

### Decision

`SchemaExtractor` is defined as an abstract base class (`app/services/schema_extraction/base.py`) with a single `extract(file_path) -> Schema` method, implemented independently by each format-specific extractor (CSV now; XLSX, SQLite, SQL in later phases).

Reason

Keeps the Prompt Builder and everything downstream agnostic to the original input format, and gives every future extractor a consistent contract to implement against, per the modular/reusable-services guideline in coding_guidenlines.md.
