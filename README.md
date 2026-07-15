Project:
Natural Language to SQL Generator

Goal:
Convert natural language requests into SQL queries using a Large Language Model.

The application supports two modes:

Mode 1:
The user manually provides the table name and column names.

Mode 2:
The user uploads one of the following:

- CSV
- XLSX
- SQLite database
- PostgreSQL schema
- SQL dump (.sql)

The application automatically extracts the database schema and uses it as context for SQL generation.

The AI should understand:

- available tables
- relationships
- primary keys
- foreign keys
- column names
- data types

The generated SQL must only use objects that exist in the uploaded schema.

The application should support:

SELECT
WHERE
GROUP BY
HAVING
ORDER BY
LIMIT
JOIN
Subqueries