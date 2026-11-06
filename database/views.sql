-- OPTIONAL administrator script. CREATE VIEW causes an implicit commit.
USE MathMyst;
CREATE OR REPLACE SQL SECURITY INVOKER VIEW contribution_details AS
SELECT c.contribution_id, p.problem_name, m.mathematician_name,
       c.contribution_year, c.contribution_type, c.significance_score
FROM CONTRIBUTION AS c
INNER JOIN MATH_PROBLEM AS p ON p.problem_id = c.problem_id
INNER JOIN MATHEMATICIAN AS m ON m.mathematician_id = c.mathematician_id;

CREATE OR REPLACE SQL SECURITY INVOKER VIEW problem_summary AS
SELECT p.problem_id, p.problem_name, p.status,
       COUNT(c.contribution_id) AS contribution_count,
       ROUND(AVG(c.significance_score), 2) AS average_score
FROM MATH_PROBLEM AS p
LEFT JOIN CONTRIBUTION AS c ON c.problem_id = p.problem_id
GROUP BY p.problem_id, p.problem_name, p.status;

SELECT * FROM problem_summary ORDER BY contribution_count DESC, problem_name;
