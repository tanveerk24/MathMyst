# MathMyst DBMS viva preparation

Use these answers as speaking prompts. Be ready to point to a table, query, or route that demonstrates each claim.

1. **What is MathMyst?**
   MathMyst is a local Flask and MySQL/MariaDB application that organizes mathematical problems, mathematicians, and their research contributions.

2. **Why was this project chosen?**
   Mathematical research gives a clear many-to-many relationship and meaningful examples for joins, grouping, and subqueries without complicated business workflows.

3. **What problem does it solve?**
   It connects separate records about problems and researchers so users can search, maintain, and analyze their relationships.

4. **What is a DBMS?**
   A database management system is software for storing, retrieving, updating, and controlling access to organized data.

5. **What is an RDBMS?**
   A relational DBMS organizes data into relations, usually represented as tables, and uses keys and constraints to connect them.

6. **What are the three main entities?**
   `MATH_PROBLEM`, `MATHEMATICIAN`, and `CONTRIBUTION`.

7. **What is a primary key?**
   A column or set of columns that uniquely identifies each row and cannot be null. `problem_id` is one example.

8. **What is a foreign key?**
   A constraint requiring a child value to reference an existing parent key. `CONTRIBUTION.problem_id` references `MATH_PROBLEM.problem_id`.

9. **Why is CONTRIBUTION necessary?**
   It resolves the many-to-many problem/person relationship and stores attributes of each association, such as year and score.

10. **What is a one-to-many relationship here?**
    One mathematical problem can have many contributions, while each contribution references exactly one problem.

11. **What is a many-to-many relationship here?**
    A mathematician can contribute to many problems, and a problem can receive contributions from many mathematicians.

12. **Can a problem have no contributions?**
    Yes. Contributions require parents, but parents do not require children. This is useful for outer-join demonstrations.

13. **What is normalization?**
    It is organizing relations to reduce unnecessary repetition and insertion, update, and deletion anomalies.

14. **Is the schema in first normal form?**
    Yes under its stated model: each attribute holds one value, and every row has a primary key. Researcher lists are not stored inside one problem column.

15. **Is it in second normal form?**
    The tables use single-column primary keys, so no attribute depends on only part of a composite primary key.

16. **Is it in third normal form?**
    Problem, person, and contribution facts are separated, but `has_prize` is redundant if it is defined solely by `prize_amount > 0`. We retain that required field and acknowledge the limitation rather than claiming no redundancy.

17. **What is an insertion anomaly?**
    A design prevents adding one fact without an unrelated fact. Separating mathematicians allows adding a researcher before any contribution is recorded.

18. **What is an update anomaly?**
    Repeated copies of one fact can disagree after an edit. A mathematician's name is stored once instead of repeated in every contribution.

19. **What is a deletion anomaly?**
    Deleting one fact accidentally removes another. Removing a contribution does not delete the separately stored mathematician.

20. **What does UNIQUE do?**
    It prevents duplicate key values. The catalogue requires unique problem names, while person names need not be globally unique.

21. **How is NOT NULL different from a nonblank value?**
    `NOT NULL` rejects SQL null, but can still allow an empty string. Application validation also rejects blank required names.

22. **What is a CHECK constraint?**
    It rejects rows whose condition is false, such as a negative prize or a score above 10. A supported engine version is necessary for enforcement.

23. **What does DEFAULT mean?**
    The database supplies a declared value when an insert omits the column. The prize amount defaults to zero.

24. **Why use DECIMAL for money?**
    It stores fixed-precision decimal values exactly within its range, avoiding typical binary floating-point rounding surprises.

25. **What does ON DELETE RESTRICT do?**
    It blocks deleting a parent while child contributions reference it. Delete or reassign those contributions first.

26. **What does ON UPDATE CASCADE do?**
    If an administrator changes a referenced parent key, matching child foreign keys are updated automatically.

27. **What is a JOIN?**
    It combines related rows from relations using a condition, such as matching a contribution's `problem_id` to its problem.

28. **How does INNER JOIN differ from LEFT JOIN?**
    An inner join keeps matching rows. A left join also preserves unmatched left-side rows with null right-side columns.

29. **What is RIGHT JOIN?**
    It preserves all right-side rows. Reversing table order lets a left join express the same preservation.

30. **What is a SELF JOIN?**
    A table is joined to itself using aliases, such as finding two distinct problems in the same field.

31. **What does GROUP BY do?**
    It forms groups for aggregates. `SELECT status, COUNT(*) FROM MATH_PROBLEM GROUP BY status;` counts each status.

32. **How is HAVING different from WHERE?**
    `WHERE` filters rows before grouping; `HAVING` filters resulting groups, such as groups with more than one contribution.

33. **What is the difference between COUNT(*) and COUNT(column)?**
    `COUNT(*)` counts rows; `COUNT(column)` counts non-null values. Count the child ID after a left join to get zero for an unmatched parent.

34. **Which aggregate functions are demonstrated?**
    `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX` summarize counts, totals, averages, and extremes.

35. **What is a subquery?**
    A query nested inside another SQL statement. An average-prize subquery can find problems whose prize is above the overall average.

36. **What is a scalar subquery?**
    It returns one value, such as `(SELECT MAX(prize_amount) FROM MATH_PROBLEM)`.

37. **What is a correlated subquery?**
    It references a row from the outer query. `EXISTS` can look for contributions matching each outer problem ID.

38. **What does EXISTS do?**
    It is true when the subquery returns at least one row. `NOT EXISTS` identifies the absence of matching rows.

39. **Why can NOT IN be surprising with NULL?**
    A null in its comparison set can make the result unknown. `NOT EXISTS` is often clearer for finding missing relationships.

40. **What is a view?**
    A named, saved query that presents data from existing relations. It does not create another main application entity.

41. **What is an index?**
    An auxiliary structure that can speed suitable lookups and supports key enforcement. It also consumes storage and adds write overhead.

42. **Does an index always improve performance?**
    No. Small tables, low-selectivity filters, or leading-wildcard searches may not benefit. Use `EXPLAIN` to examine the plan.

43. **What is a stored procedure?**
    A named database routine invoked with `CALL`. It can accept parameters and encapsulate a query or operation.

44. **What is a trigger?**
    Code that runs automatically for a specified table event, such as `BEFORE INSERT`. Procedures are called explicitly; triggers respond to events.

45. **What is a transaction?**
    A set of operations treated as one logical unit. `COMMIT` makes its changes permanent; `ROLLBACK` cancels uncommitted transactional changes.

46. **What does ACID mean?**
    Atomicity, consistency, isolation, and durability: all-or-nothing changes, valid state, controlled concurrency, and persistence of committed work.

47. **Why use InnoDB?**
    It supports transactions, foreign keys, and row-level locking, which are important for this relational application.

48. **Can all SQL statements be rolled back?**
    No. MySQL DDL commonly causes implicit commits. `CREATE TABLE`, `ALTER TABLE`, and `DROP TABLE` must not be treated like rollback-safe DML.

49. **Why can auto-increment IDs contain gaps?**
    Deleted or rolled-back inserts can consume numbers. The key guarantees identity, not a gapless sequence.

50. **What is PyMySQL?**
    A Python database driver used to connect to MySQL/MariaDB, execute SQL, fetch records, and control transactions without an ORM.

51. **What is SQL injection?**
    An attack where input changes SQL syntax because the program inserts it into a statement unsafely.

52. **Why use parameterized queries?**
    The driver binds values separately from SQL structure. PyMySQL uses `%s` placeholders, with a tuple of values passed to `execute`.

53. **Can a placeholder represent a column name?**
    No. Placeholders represent values. Sort columns and directions are selected from a server-side allowlist.

54. **What is Flask's role?**
    Flask handles HTTP requests, routes them to Python functions, processes forms, and returns rendered responses.

55. **What is Jinja2?**
    A template engine that combines HTML with dynamic data, loops, conditionals, and shared layouts. HTML templates escape values by default.

56. **What is python-dotenv used for?**
    It loads local environment settings from `.env`, keeping configuration separate from source code. `.env` must remain untracked.

57. **Why use POST for modifications?**
    GET should retrieve resources without changing state. POST is the appropriate method for these create, update, and delete actions.

58. **What is CSRF?**
    Cross-site request forgery tricks a browser into submitting an unintended state-changing request. Session-bound CSRF tokens help reject such requests.

59. **Why validate in both Python and SQL?**
    Python gives clear feedback, while database constraints preserve integrity even if data is written through another client.

60. **Why not use the MySQL root account in the app?**
    Root has unnecessary administrative power. A dedicated user with only CRUD permissions limits what the application connection can do.

61. **Why is arbitrary SQL disabled in the web laboratory?**
    The lab teaches approved queries safely. Accepting a query identifier prevents users from submitting destructive or unauthorized SQL.

62. **How are dashboard numbers produced?**
    SQL queries compute totals and grouped counts from current database records; the displayed statistics are not hardcoded.

63. **How are database errors handled?**
    Failed writes roll back. The app shows a safe message, while detailed errors are kept in server logs rather than exposed in the browser.

64. **Why use a separate database for integration tests?**
    Tests may create, change, or remove records. An isolated test database protects the main demonstration data.

65. **Do passing unit tests prove the live database works?**
    No. Unit tests can validate application logic without MySQL; integration tests verify behavior against a real, separately configured engine.

66. **Are significance scores historical facts?**
    No. They are clearly identified editorial demonstration values used to make aggregate queries meaningful.

67. **What does a problem with no contributions mean?**
    No contribution is recorded in this small catalogue. It does not mean no mathematician has ever studied the problem.

68. **Why are primary keys not edited in the forms?**
    They are stable identifiers used by relationships. Users edit descriptive facts while the database manages identity.

69. **How would you extend the project later?**
    Add authenticated administration, pagination, structured bibliographic sources, and richer collaboration modeling after agreeing on a larger schema.

70. **What are the main limitations of this version?**
    It is a trusted local demonstration with simplified historical labels, no authentication, and a deliberately small three-entity model.

## Short SQL examples to rehearse

```sql
-- Filter and order.
SELECT problem_name FROM MATH_PROBLEM
WHERE status = 'Unsolved' ORDER BY proposed_year;

-- Group and filter groups.
SELECT problem_id, COUNT(*) AS total FROM CONTRIBUTION
GROUP BY problem_id HAVING COUNT(*) > 1;

-- Correlated absence test.
SELECT m.mathematician_name FROM MATHEMATICIAN AS m
WHERE NOT EXISTS (
    SELECT 1 FROM CONTRIBUTION AS c
    WHERE c.mathematician_id = m.mathematician_id
);
```

For historical claims, use [data_sources.md](data_sources.md). For transaction and constraint details, use [database_design.md](database_design.md) and [sql_explanations.md](sql_explanations.md).
