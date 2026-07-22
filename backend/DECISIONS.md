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

Introduce a dedicated `FileValidator` service, separate from the schema extractors, and a shared exception hierarchy (`FileValidationError` and subclasses, `SchemaExtractionError`) raised by services rather than HTTPException.

Reason

Keeps upload routers limited to request/response handling and HTTP status mapping, as required by the coding guidelines. Validation logic (filename present, extension allowed, content not empty) is reusable across future extractors (XLSX, SQLite, SQL) without duplicating checks in each router. Routers catch the domain exceptions and translate them to HTTP status codes (400 for validation failures, 422 for parse/extraction failures), keeping business logic and HTTP concerns fully decoupled.