# Database design

## Design goals

MathMyst uses exactly three main InnoDB entities: `MATH_PROBLEM`, `MATHEMATICIAN`, and `CONTRIBUTION`. The design separates problem facts, person facts, and facts about a person's contribution to a problem. It favors simple, explicit SQL and enforceable relationships over additional application features.

Use MySQL 8.0.16+ or MariaDB 10.4+. A database administrator creates the schema; the web application connects with a separate CRUD-only account.

## Data dictionary

### MATH_PROBLEM

| Attribute | Type | Rules and meaning |
| --- | --- | --- |
| `problem_id` | `INT` | Primary key, auto-increment |
| `problem_name` | `VARCHAR(100)` | Required, unique catalogue name |
| `math_field` | `VARCHAR(50)` | Required primary field label |
| `proposed_year` | `INT` | Optional; positive when known |
| `status` | `VARCHAR(20)` | Required; `Solved` or `Unsolved` |
| `prize_amount` | `DECIMAL(12,2)` | Default zero; nonnegative monetary amount |
| `has_prize` | `BOOLEAN` | Default false; whether a prize association is recorded |

`DECIMAL` stores decimal amounts exactly within the declared precision, unlike a floating-point approximation. The column does not store a currency code; the sample catalogue interprets its prize amounts as USD for demonstration purposes. A nonzero value is a recorded prize association, not a statement that the award remains claimable.

### MATHEMATICIAN

| Attribute | Type | Rules and meaning |
| --- | --- | --- |
| `mathematician_id` | `INT` | Primary key, auto-increment |
| `mathematician_name` | `VARCHAR(80)` | Required name; names are not assumed globally unique |
| `country` | `VARCHAR(40)` | Optional simplified country label |
| `birth_date` | `DATE` | Optional calendar date |
| `specialization` | `VARCHAR(50)` | Optional primary specialization |

Two people may share a name, so the numeric key identifies the person. Country labels simplify historical nationality and geography; they are not intended to express every citizenship or border change.

### CONTRIBUTION

| Attribute | Type | Rules and meaning |
| --- | --- | --- |
| `contribution_id` | `INT` | Primary key, auto-increment |
| `problem_id` | `INT` | Required foreign key to a problem |
| `mathematician_id` | `INT` | Required foreign key to a mathematician |
| `contribution_year` | `INT` | Required positive year |
| `contribution_type` | `VARCHAR(40)` | Optional short label describing the contribution |
| `significance_score` | `DECIMAL(4,2)` | Optional editorial demonstration score from 0 to 10 |

A contribution row is a recorded event, not just a unique problem/person pair. The same person may make multiple contributions to the same problem in different years or of different types. A unique constraint on only the two foreign keys would prevent such legitimate records, so the surrogate `contribution_id` identifies each event.

## Keys and integrity

- **Entity integrity:** every primary key uniquely identifies a non-null row.
- **Candidate/alternate key:** `MATH_PROBLEM.problem_name` is unique in this catalogue.
- **Referential integrity:** both contribution foreign keys must refer to existing parents.
- **Domain integrity:** checks constrain status, positive years, nonnegative prizes, and score range.
- **Required values:** `NOT NULL` prevents the absence of mandatory attributes. Application validation also rejects blank or whitespace-only required text.
- **Defaults:** omitted prize fields receive their declared defaults. A default does not replace an explicitly supplied invalid value.

SQL `NULL` means missing or unknown, not zero or an empty string. A nullable score may satisfy a range check because SQL check expressions permit unknown outcomes; the application treats an empty optional score as `NULL`.

## Relationships and referential actions

`MATH_PROBLEM (1) -> (0..many) CONTRIBUTION` and `MATHEMATICIAN (1) -> (0..many) CONTRIBUTION` resolve the parent entities' many-to-many relationship. The required foreign keys mean the contribution side always has exactly one parent of each kind.

`ON DELETE RESTRICT` protects contribution history from accidental parent deletion. To remove a parent intentionally, first remove or reassign its contributions. `ON UPDATE CASCADE` maintains references if an administrator changes a parent key. Routine application edits never change primary-key values.

## Normalization

**First normal form:** each column holds one value, and each row has a key. Lists of mathematician IDs are not stored inside problem rows.

**Second normal form:** each table uses a single-column primary key, so there is no dependency on only part of a composite primary key. Problem and person details are stored in their own relations rather than copied into each contribution.

**Third normal form:** under the stated assumptions, descriptive attributes describe the entity or event identified by their key. Country is a stored person label rather than an address hierarchy; field is a primary label rather than a list of field metadata.

The required `has_prize` field deserves an explicit qualification. If the business rule defines it as exactly `prize_amount > 0`, it is a derived value and therefore redundant; claiming an entirely redundancy-free 3NF design would be misleading. MathMyst retains both required fields. The form requires the flag for a positive monetary amount, but allows a checked flag with zero amount, representing a prize association without a recorded positive amount. The schema checks the boolean domain and nonnegative amount separately; it does not enforce their relationship for direct SQL writes. A redesigned system could derive the flag at query time or use a generated column if strict equivalence were desired. Those alternatives are outside this fixed examination schema.

## Indexes

Primary and unique keys have supporting indexes. InnoDB requires suitable indexes for foreign keys and creates supporting ones if necessary. Additional indexes in `schema.sql` support common field, status, contribution-year, and association filters.

An index can reduce the records the engine examines for an appropriate filter or join; it does not guarantee an improvement for every query. Indexes use storage and add write overhead. A leading-wildcard search such as `LIKE '%prime%'` usually cannot use a normal B-tree index for a direct prefix lookup. Use `EXPLAIN SELECT ...` to inspect a plan rather than assuming every indexed column speeds up every search.

## Transactions and connection lifecycle

InnoDB supports transactions. A successful write commits; a failed write rolls back. A connection belongs to the request and is closed during teardown. Database errors are logged for diagnosis while the browser receives a safe explanation.

For multi-step manual exercises, use `START TRANSACTION`, inspect the temporary changes, then `ROLLBACK` or intentionally `COMMIT`. Do not mix DDL into a transaction that you expect to roll back: many MySQL DDL statements cause implicit commits. See [the MySQL reference](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html).

## Historical and analytical limits

Contribution types summarize sourced historical work; scores are subjective demonstration values. A collaborative result may appear once for each credited researcher, so `COUNT(*)` counts recorded contribution rows, not unique publications. A problem without contributions means this catalogue has no recorded association, not that nobody has studied it.

Prize associations and problem status are a sample snapshot. They should be checked against current authoritative sources before being used as contemporary research guidance. See [data_sources.md](data_sources.md) for the seed's evidence and conventions.
