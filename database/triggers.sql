-- OPTIONAL administrator script: simple BEFORE INSERT/UPDATE examples.
-- Triggers repeat a CHECK constraint for teaching; they create no extra tables.
-- DROP/CREATE TRIGGER cause implicit commits, so ROLLBACK cannot undo them.
USE MathMyst;
DROP TRIGGER IF EXISTS validate_contribution_score_insert;
DROP TRIGGER IF EXISTS validate_contribution_score_update;
DELIMITER $$
CREATE TRIGGER validate_contribution_score_insert
BEFORE INSERT ON CONTRIBUTION
FOR EACH ROW
BEGIN
    IF NEW.significance_score IS NOT NULL
       AND (NEW.significance_score < 0 OR NEW.significance_score > 10) THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'Significance score must be between 0 and 10';
    END IF;
END$$
CREATE TRIGGER validate_contribution_score_update
BEFORE UPDATE ON CONTRIBUTION
FOR EACH ROW
BEGIN
    IF NEW.significance_score IS NOT NULL
       AND (NEW.significance_score < 0 OR NEW.significance_score > 10) THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'Significance score must be between 0 and 10';
    END IF;
END$$
DELIMITER ;
