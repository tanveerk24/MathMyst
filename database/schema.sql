-- MathMyst: MySQL 8.0.16+ or MariaDB 10.4+. Run with an administrator.
-- CREATE DATABASE and CREATE TABLE cause implicit commits in MySQL.
-- This script never drops or truncates an existing application table.
CREATE DATABASE IF NOT EXISTS MathMyst
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE MathMyst;

CREATE TABLE IF NOT EXISTS MATH_PROBLEM (
    problem_id INT NOT NULL AUTO_INCREMENT,
    problem_name VARCHAR(100) NOT NULL,
    math_field VARCHAR(50) NOT NULL,
    proposed_year INT NULL,
    status VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
    prize_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    has_prize BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_math_problem PRIMARY KEY (problem_id),
    CONSTRAINT uq_problem_name UNIQUE (problem_name),
    CONSTRAINT ck_problem_status CHECK (BINARY status IN ('Solved', 'Unsolved')),
    CONSTRAINT ck_problem_prize CHECK (prize_amount >= 0),
    CONSTRAINT ck_problem_year CHECK (proposed_year IS NULL OR proposed_year > 0),
    CONSTRAINT ck_problem_has_prize CHECK (has_prize IN (0, 1)),
    INDEX idx_problem_field_status (math_field, status),
    INDEX idx_problem_year (proposed_year)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS MATHEMATICIAN (
    mathematician_id INT NOT NULL AUTO_INCREMENT,
    mathematician_name VARCHAR(80) NOT NULL,
    country VARCHAR(40) NULL,
    birth_date DATE NULL,
    specialization VARCHAR(50) NULL,
    CONSTRAINT pk_mathematician PRIMARY KEY (mathematician_id),
    INDEX idx_mathematician_name (mathematician_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS CONTRIBUTION (
    contribution_id INT NOT NULL AUTO_INCREMENT,
    problem_id INT NOT NULL,
    mathematician_id INT NOT NULL,
    contribution_year INT NOT NULL,
    contribution_type VARCHAR(40) NULL,
    significance_score DECIMAL(4,2) NULL,
    CONSTRAINT pk_contribution PRIMARY KEY (contribution_id),
    CONSTRAINT fk_contribution_problem FOREIGN KEY (problem_id)
      REFERENCES MATH_PROBLEM (problem_id)
      ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_contribution_mathematician FOREIGN KEY (mathematician_id)
      REFERENCES MATHEMATICIAN (mathematician_id)
      ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT ck_contribution_year CHECK (contribution_year > 0),
    CONSTRAINT ck_contribution_score CHECK (
      significance_score IS NULL OR significance_score BETWEEN 0 AND 10
    ),
    INDEX idx_contribution_problem (problem_id),
    INDEX idx_contribution_mathematician (mathematician_id),
    INDEX idx_contribution_year (contribution_year)
) ENGINE=InnoDB;
