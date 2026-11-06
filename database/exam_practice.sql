-- OPTIONAL MODIFICATION EXERCISES. Read before running as an administrator.
-- No application table is dropped. Exactly three persistent entities remain.
USE MathMyst;

-- DDL: temporary tables belong only to this connection.
-- CREATE/DROP TEMPORARY TABLE do not implicitly commit, but cannot be rolled back.
CREATE TEMPORARY TABLE mathmyst_ddl_demo (
    demo_id INT PRIMARY KEY,
    label VARCHAR(40) NOT NULL
) ENGINE=InnoDB;
-- ALTER TABLE causes an implicit commit, even on a temporary table.
ALTER TABLE mathmyst_ddl_demo ADD COLUMN note VARCHAR(80) DEFAULT 'Exam only';
DROP TEMPORARY TABLE mathmyst_ddl_demo;

-- DML and ROLLBACK: restores all application records at the end.
-- AUTO_INCREMENT numbers consumed by a rolled-back insert are not reclaimed.
START TRANSACTION;
INSERT INTO MATH_PROBLEM (problem_name, math_field, status)
VALUES ('Demonstration record (not historical)', 'Demonstration', 'Unsolved');
SET @demo_problem_id = LAST_INSERT_ID();
UPDATE MATH_PROBLEM SET proposed_year = 2026
WHERE problem_id = @demo_problem_id;
SELECT * FROM MATH_PROBLEM WHERE problem_id = @demo_problem_id;
DELETE FROM MATH_PROBLEM WHERE problem_id = @demo_problem_id;
ROLLBACK;

-- COMMIT a harmless change that matches the existing value.
START TRANSACTION;
UPDATE MATH_PROBLEM SET prize_amount = prize_amount WHERE problem_id = 1;
COMMIT;

-- Inspect constraint definitions and indexes without changing the database.
SHOW CREATE TABLE MATH_PROBLEM;
SHOW CREATE TABLE CONTRIBUTION;
SHOW INDEX FROM CONTRIBUTION;
EXPLAIN SELECT * FROM CONTRIBUTION WHERE problem_id = 7;

-- RIGHT JOIN: retains people without recorded contributions.
SELECT m.mathematician_name, c.contribution_type
FROM CONTRIBUTION AS c RIGHT JOIN MATHEMATICIAN AS m
  ON m.mathematician_id = c.mathematician_id
ORDER BY m.mathematician_name;

-- SELF JOIN: unordered pairs of different problems in the same field.
SELECT a.problem_name AS first_problem, b.problem_name AS second_problem,
       a.math_field
FROM MATH_PROBLEM AS a INNER JOIN MATH_PROBLEM AS b
  ON a.math_field = b.math_field AND a.problem_id < b.problem_id
ORDER BY a.math_field, a.problem_name, b.problem_name;
