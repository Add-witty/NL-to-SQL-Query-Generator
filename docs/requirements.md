Functional requirements: 
Functional Requirements

The application shall allow users to upload:

- CSV
- XLSX
- SQLite database
- SQL schema file

The system shall automatically extract:

- table names
- column names
- data types
- primary keys
- foreign keys (when available)

The extracted schema shall be supplied to the LLM.

The generated SQL must only reference existing tables and columns.

If a requested column does not exist, the system shall return a meaningful error.

The user enters English. 
The system generates SQL query. 
The sql query should be valid. 
The sql should never invent columns or table names. 
The sql should only generate queries out of the information provided as the input. 


Non Functional requirements: 
Response < 5sec 
Clean UI 
Syntax highlighting 
Copy button 
Responsive 
