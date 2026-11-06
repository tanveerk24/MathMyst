-- OPTIONAL administrator script. Routine DDL causes implicit commits.
-- DELIMITER is a mysql/mariadb CLIENT command, not server SQL.
-- No EXECUTE grant is needed by the Flask app; this is an examination example.
USE MathMyst;
DROP PROCEDURE IF EXISTS GetProblemContributions;
DELIMITER $$
CREATE PROCEDURE GetProblemContributions(IN selected_problem_id INT)
SQL SECURITY INVOKER
READS SQL DATA
BEGIN
    SELECT c.contribution_id, m.mathematician_name,
           c.contribution_year, c.contribution_type, c.significance_score
    FROM CONTRIBUTION AS c
    INNER JOIN MATHEMATICIAN AS m
      ON m.mathematician_id = c.mathematician_id
    WHERE c.problem_id = selected_problem_id
    ORDER BY c.contribution_year, c.contribution_id;
END$$
DELIMITER ;
CALL GetProblemContributions(7);
