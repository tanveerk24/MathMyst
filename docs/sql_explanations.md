# SQL concepts explained through MathMyst

## Read-only query laboratory

The web laboratory executes only developer-approved statements from `query_catalog.py`. The browser submits a query identifier; it cannot supply SQL. `database/queries.sql` contains the examination query collection. CRUD forms provide the separate, validated path for changes.

## DDL, DML, and DQL

DDL defines structures, such as `CREATE TABLE`, `ALTER TABLE`, and `DROP TABLE`. DML changes records with `INSERT`, `UPDATE`, and `DELETE`. `SELECT` retrieves data and is often called DQL in academic classifications; some references group it under DML instead.

```sql
SELECT problem_name, status FROM MATH_PROBLEM;
```

DDL practice belongs in the separate demonstration script. Do not drop an application table to demonstrate the syntax.

## Filtering, projection, and sorting

`SELECT` chooses columns; `WHERE` chooses rows. `DISTINCT` removes duplicate result combinations. `ORDER BY` specifies output order; without it, row order is not guaranteed.

```sql
SELECT DISTINCT math_field
FROM MATH_PROBLEM
WHERE status = 'Unsolved'
ORDER BY math_field;
```

`LIKE '%prime%'` matches a substring, while `'prime%'` matches a prefix. `%` represents zero or more characters and `_` represents one character. `BETWEEN 1800 AND 1900` includes both endpoints. `IN ('Solved', 'Unsolved')` checks membership in a list. Comparison with `NULL` uses `IS NULL`, not `= NULL`.

## Aggregates

| Function | Meaning | MathMyst example |
| --- | --- | --- |
| `COUNT(*)` | Count result rows | Total problems |
| `COUNT(column)` | Count non-null values | Known proposed years |
| `SUM(column)` | Add non-null values | Recorded prize total |
| `AVG(column)` | Mean of non-null values | Average recorded score |
| `MIN(column)` | Smallest non-null value | Earliest proposed year |
| `MAX(column)` | Largest non-null value | Highest recorded prize |

Most aggregate functions return `NULL` for an empty input; `COUNT` returns zero. `COALESCE(SUM(prize_amount), 0)` can give a dashboard an explicit zero when no records exist.

## GROUP BY and HAVING

`GROUP BY` creates groups for aggregate calculations. `WHERE` filters source rows before grouping, while `HAVING` filters groups after aggregation.

```sql
SELECT math_field, COUNT(*) AS problem_count
FROM MATH_PROBLEM
WHERE status = 'Unsolved'
GROUP BY math_field
HAVING COUNT(*) >= 2
ORDER BY problem_count DESC, math_field;
```

Every selected nonaggregated expression should be grouped or otherwise valid under the server's functional-dependency rules. Explicitly listing group columns keeps examination examples clear and compatible with `ONLY_FULL_GROUP_BY`.

## INNER JOIN

An inner join returns matching relationships. Joining through `CONTRIBUTION` converts IDs into readable problem and person names.

```sql
SELECT p.problem_name, m.mathematician_name, c.contribution_year
FROM CONTRIBUTION AS c
INNER JOIN MATH_PROBLEM AS p ON p.problem_id = c.problem_id
INNER JOIN MATHEMATICIAN AS m ON m.mathematician_id = c.mathematician_id
ORDER BY c.contribution_year, c.contribution_id;
```

The aliases shorten qualified column names and avoid ambiguous references.

## LEFT JOIN and missing relationships

A left join keeps every row from its left relation, even when there is no match on the right. Unmatched right-side columns become `NULL`.

```sql
SELECT p.problem_name, COUNT(c.contribution_id) AS recorded_contributions
FROM MATH_PROBLEM AS p
LEFT JOIN CONTRIBUTION AS c ON c.problem_id = p.problem_id
GROUP BY p.problem_id, p.problem_name;
```

Count `c.contribution_id`, not `COUNT(*)`: a left join produces one null-extended row for an unmatched problem, and `COUNT(*)` would incorrectly report one contribution. To find only unlinked problems, filter `WHERE c.contribution_id IS NULL`.

## RIGHT JOIN

A right join preserves every row on the right. Reversing the relations of a left join can express the same result:

```sql
SELECT m.mathematician_name, c.contribution_id
FROM CONTRIBUTION AS c
RIGHT JOIN MATHEMATICIAN AS m
  ON m.mathematician_id = c.mathematician_id;
```

This displays all mathematicians, including those without recorded contributions.

## SELF JOIN

A self join uses the same table under two aliases. It can find pairs of problems in the same field without introducing a hierarchy:

```sql
SELECT a.problem_name AS first_problem, b.problem_name AS second_problem
FROM MATH_PROBLEM AS a
INNER JOIN MATH_PROBLEM AS b
  ON a.math_field = b.math_field AND a.problem_id < b.problem_id;
```

The `<` condition excludes a problem paired with itself and prevents duplicate reversed pairs.

## Scalar subquery

A scalar subquery returns one value that the outer query can compare against:

```sql
SELECT problem_name, prize_amount
FROM MATH_PROBLEM
WHERE prize_amount > (SELECT AVG(prize_amount) FROM MATH_PROBLEM);
```

## IN subquery

An `IN` subquery tests whether a value occurs in a set of returned values:

```sql
SELECT mathematician_name
FROM MATHEMATICIAN
WHERE mathematician_id IN (
    SELECT mathematician_id
    FROM CONTRIBUTION
    WHERE contribution_year >= 1950
);
```

## EXISTS, NOT EXISTS, and correlation

`EXISTS` is true when its subquery returns at least one row. A correlated subquery references the current outer row.

```sql
SELECT p.problem_name
FROM MATH_PROBLEM AS p
WHERE EXISTS (
    SELECT 1 FROM CONTRIBUTION AS c
    WHERE c.problem_id = p.problem_id
);
```

`NOT EXISTS` finds the complementary case: a problem with no matching recorded contribution. It avoids the surprising unknown result that `NOT IN` can produce if a subquery contains `NULL`.

## Views

A view is a stored query definition. It presents a reusable relation, such as readable contribution names, without duplicating the underlying base-table records. The supplied view script is installed with an administrator connection; the normal app does not require permission to create views.

```sql
CREATE VIEW example_problem_names AS
SELECT problem_id, problem_name, status FROM MATH_PROBLEM;
```

This snippet explains syntax; use the actual named views in `database/views.sql` for the prepared demonstration. Views are not a fourth main entity.

## Indexes

Indexes help locate rows and support key enforcement. Useful candidates include foreign-key columns and frequent filter columns. More indexes increase storage and write costs. Inspect plans with `EXPLAIN` instead of assuming an index always improves a query.

```sql
EXPLAIN SELECT * FROM CONTRIBUTION WHERE problem_id = 1;
```

## Transactions, COMMIT, and ROLLBACK

```sql
START TRANSACTION;
UPDATE MATH_PROBLEM SET prize_amount = prize_amount + 1
WHERE problem_id = 1;
SELECT problem_id, prize_amount FROM MATH_PROBLEM WHERE problem_id = 1;
ROLLBACK;
```

This restores the old amount if the table uses InnoDB and no intervening implicit-commit statement occurs. `COMMIT` would instead make the successful change permanent. Auto-increment numbers may still have gaps after rolled-back inserts; sequences are identifiers, not gapless counters.

ACID means atomicity (all or nothing), consistency (preserve valid state), isolation (control concurrent interference), and durability (committed changes survive failures under the server's persistence configuration).

## Stored procedures and triggers

A stored procedure is a named server-side routine called explicitly with `CALL`. A trigger runs automatically for a specified table event, such as before an insert. The prepared scripts keep these examples small and do not create extra main entities.

`DELIMITER` is a command understood by the MySQL/MariaDB client so that routine bodies can contain semicolons. It is not SQL sent directly to the server through PyMySQL.

## Implicit commits and safe practice

MySQL DDL commonly commits the active transaction. `CREATE DATABASE`, ordinary `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, and statements defining views, procedures, or triggers cannot be treated as rollback-safe DML. Temporary-table DDL has special behavior: it can avoid an implicit commit while still being non-rollbackable. Keep such demonstrations separate and clean up explicitly. See [the official MySQL list](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html).

Use a disposable demonstration table or separate practice schema for destructive exercises. The application entities must not be dropped as an exam demonstration.

## Parameterized SQL

In PyMySQL, pass values separately:

```python
cursor.execute(
    "SELECT * FROM MATH_PROBLEM WHERE status = %s",
    (selected_status,),
)
```

The `%s` is a driver placeholder, not Python string formatting. Do not interpolate user text with f-strings, `%`, or concatenation. Parameters represent values; table names, column names, and sort directions must come from a fixed server-side allowlist.

## Interpreting results honestly

An empty join result can reflect sparse seed data. A problem without recorded contributions is unlinked within this catalogue; it is not historically unstudied. Contribution counts measure rows, and editorial significance averages summarize demonstration scores rather than objective mathematical importance.
