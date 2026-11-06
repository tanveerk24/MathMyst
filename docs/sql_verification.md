# Optional SQL script verification

Verified on **6 November 2026** using the bundled MySQL-compatible command-line
client against **MariaDB 10.4.32**, on the separate disposable database
`mathmyst_test` only. Each script's `USE MathMyst;` statement was changed to
`USE mathmyst_test;` in memory before execution. No application-database data was
changed by this verification.

| Script | Result | Additional checks |
|---|---|---|
| `database/views.sql` | Exit code 0 | `contribution_details` has 17 rows; `problem_summary` has 10 rows, matching their underlying records. |
| `database/procedures.sql` | Exit code 0 | `CALL GetProblemContributions(7)` returned the expected three Poincaré contribution rows. |
| `database/triggers.sql` | Exit code 0 | Both invalid INSERT and UPDATE scores were rejected with trigger-generated error 1644 (`SIGNAL SQLSTATE '45000'`). |
| `database/queries.sql` | Exit code 0 | All 34 approved SELECT statements executed through the command-line client. |
| `database/exam_practice.sql` | Exit code 0 | Temporary-table DDL, transaction examples, inspection, EXPLAIN and joins executed successfully. |

The examination script requires administrator privileges, including
`CREATE TEMPORARY TABLES`. The restricted test account correctly received error
1044 for its temporary-table statement; running that script with the local
administrator connection succeeded. Normal application credentials do not need
these privileges.

Sorted snapshots of every column in all three application tables were compared
before and after the five scripts and trigger checks. They matched exactly:

- MATH_PROBLEM: 10 rows.
- MATHEMATICIAN: 10 rows.
- CONTRIBUTION: 17 rows.
- Combined data SHA-256: `7f24bb00e671ec3fc7559bb98d39b39cd46a0799b882e5786d07b2e878ff9986`.

This comparison covers table contents; AUTO_INCREMENT counters can advance after
rolled-back or rejected inserts, as explained in the examination script. Optional
views, procedures and triggers remain installed in the disposable test database.
