-- FIRST-RUN DATA ONLY: import into empty MathMyst tables after schema.sql.
-- Fixed IDs make the teaching dataset and its foreign keys easy to inspect.
-- Do not rerun against populated tables: duplicate keys intentionally fail.
-- In batch mode, stop on the first error; never use the mysql --force option.
-- Research sources, scope caveats and every contribution: docs/data_sources.md.
-- Scores are fictional teaching ratings, not historical or objective measures.
USE MathMyst;
SET NAMES utf8mb4;
START TRANSACTION;

INSERT INTO MATH_PROBLEM
 (problem_id, problem_name, math_field, proposed_year, status, prize_amount, has_prize)
VALUES
 (1, 'Riemann Hypothesis', 'Number Theory', 1859, 'Unsolved', 1000000.00, TRUE),
 (2, 'Goldbach''s Conjecture', 'Number Theory', 1742, 'Unsolved', 0.00, FALSE),
 (3, 'Collatz Conjecture', 'Number Theory', 1937, 'Unsolved', 0.00, FALSE),
 (4, 'Twin Prime Conjecture', 'Number Theory', 1849, 'Unsolved', 0.00, FALSE),
 (5, 'Fermat''s Last Theorem', 'Number Theory', 1637, 'Solved', 0.00, FALSE),
 (6, 'P versus NP', 'Theoretical Computer Science', 1971, 'Unsolved', 1000000.00, TRUE),
 (7, 'Poincaré Conjecture', 'Topology', 1904, 'Solved', 0.00, FALSE),
 (8, 'Four Color Theorem', 'Graph Theory', 1852, 'Solved', 0.00, FALSE),
 (9, 'Birch and Swinnerton-Dyer Conjecture', 'Number Theory', 1965, 'Unsolved', 1000000.00, TRUE),
 (10, 'Navier–Stokes Existence and Smoothness', 'Analysis', 2000, 'Unsolved', 1000000.00, TRUE);

-- Country is an educational origin label, not a complete citizenship history.
-- NULL dates deliberately avoid asserting an unverified biographical detail.
INSERT INTO MATHEMATICIAN
 (mathematician_id, mathematician_name, country, birth_date, specialization)
VALUES
 (1, 'Bernhard Riemann', 'Germany', '1826-09-17', 'Number Theory'),
 (2, 'Andrew Wiles', 'United Kingdom', '1953-04-11', 'Number Theory'),
 (3, 'Terence Tao', 'Australia', '1975-07-17', 'Analysis and Number Theory'),
 (4, 'Grigori Perelman', 'Russia', '1966-06-13', 'Geometry and Topology'),
 (5, 'Kenneth Appel', 'United States', '1932-10-08', 'Graph Theory'),
 (6, 'Wolfgang Haken', 'Germany', '1928-06-21', 'Topology and Graph Theory'),
 (7, 'James Maynard', 'United Kingdom', NULL, 'Number Theory'),
 (8, 'Yitang Zhang', 'China', NULL, 'Number Theory'),
 (9, 'Richard Taylor', 'United Kingdom', NULL, 'Number Theory'),
 (10, 'Srinivasa Ramanujan', 'India', '1887-12-22', 'Number Theory');

-- A row is one mathematician's involvement in one research work.
-- Coauthors produce separate rows; distinct papers on one problem also do.
-- Partial results are not proofs of their associated open conjectures.
INSERT INTO CONTRIBUTION
 (contribution_id, problem_id, mathematician_id, contribution_year,
  contribution_type, significance_score)
VALUES
 (1, 1, 1, 1859, 'Zeta-function paper and formulation', 10.00),
 (2, 5, 2, 1995, 'Modularity proof of Fermat theorem', 10.00),
 (3, 5, 2, 1995, 'Hecke-algebra proof ingredient', 9.50),
 (4, 5, 9, 1995, 'Hecke-algebra proof ingredient', 9.50),
 (5, 3, 3, 2019, 'Almost-all orbits; partial result', 8.50),
 (6, 2, 3, 2012, 'Five-prime weak variant; related', 7.00),
 (7, 10, 3, 2014, 'Averaged-equation barrier; related', 8.00),
 (8, 4, 3, 2014, 'Polymath8b bounded gaps; partial', 8.50),
 (9, 7, 4, 2002, 'Ricci-flow entropy paper', 9.50),
 (10, 7, 4, 2003, 'Ricci flow with surgery', 10.00),
 (11, 7, 4, 2003, 'Finite extinction-time paper', 10.00),
 (12, 8, 5, 1977, 'Part I: discharging proof', 9.00),
 (13, 8, 6, 1977, 'Part I: discharging proof', 9.00),
 (14, 8, 5, 1977, 'Part II: reducibility proof', 9.00),
 (15, 8, 6, 1977, 'Part II: reducibility proof', 9.00),
 (16, 4, 7, 2013, 'Multidimensional sieve; partial', 8.50),
 (17, 4, 8, 2013, 'Bounded prime gaps; partial', 9.00);

COMMIT;
