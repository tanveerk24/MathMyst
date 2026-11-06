-- MathMyst read-only query practice. Generated from query_catalog.py.
USE MathMyst;

-- 1. Explore every mathematical problem
-- Concept: SELECT
-- SELECT reads columns from a table. The primary key gives each row a stable identity.
SELECT * FROM MATH_PROBLEM ORDER BY problem_id;

-- 2. Find unsolved problems
-- Concept: WHERE
-- WHERE keeps only rows that satisfy a condition before the result is returned.
SELECT problem_name, math_field, proposed_year FROM MATH_PROBLEM WHERE status = 'Unsolved' ORDER BY problem_name;

-- 3. Problems proposed before 1900
-- Concept: WHERE
-- A comparison filters numeric values. Unknown years (NULL) do not satisfy this comparison.
SELECT problem_name, proposed_year FROM MATH_PROBLEM WHERE proposed_year < 1900 ORDER BY proposed_year, problem_name;

-- 4. Explore number theory
-- Concept: WHERE
-- Equality selects problems belonging to a particular mathematical field.
SELECT problem_name, status FROM MATH_PROBLEM WHERE math_field = 'Number Theory' ORDER BY problem_name;

-- 5. Mathematicians from Germany
-- Concept: WHERE
-- This selection operates on the country attribute of the mathematician entity.
SELECT mathematician_name, specialization FROM MATHEMATICIAN WHERE country = 'Germany' ORDER BY mathematician_name;

-- 6. Problems in alphabetical order
-- Concept: ORDER BY
-- ORDER BY sorts the output; ASC requests ascending order.
SELECT problem_name, proposed_year, status FROM MATH_PROBLEM ORDER BY problem_name ASC;

-- 7. Count unsolved problems
-- Concept: COUNT
-- COUNT(*) counts the rows left after WHERE filters the table.
SELECT COUNT(*) AS unsolved_problems FROM MATH_PROBLEM WHERE status = 'Unsolved';

-- 8. Find the highest recorded prize
-- Concept: MAX
-- MAX returns the greatest non-NULL value. Prize amounts are stored as exact DECIMAL values in USD.
SELECT MAX(prize_amount) AS highest_prize FROM MATH_PROBLEM;

-- 9. Average teaching significance score
-- Concept: AVG
-- AVG ignores NULL scores. These example ratings are subjective demonstration data, not historical facts.
SELECT ROUND(AVG(significance_score), 2) AS average_score FROM CONTRIBUTION;

-- 10. Count contributions for every problem
-- Concept: LEFT JOIN · GROUP BY · COUNT
-- LEFT JOIN preserves problems without contributions. COUNT(child_id), unlike COUNT(*), gives zero for an unmatched parent.
SELECT p.problem_id, p.problem_name, COUNT(c.contribution_id) AS contribution_count
FROM MATH_PROBLEM AS p
LEFT JOIN CONTRIBUTION AS c ON c.problem_id = p.problem_id
GROUP BY p.problem_id, p.problem_name
ORDER BY contribution_count DESC, p.problem_name;

-- 11. People contributing to multiple problems
-- Concept: GROUP BY · HAVING · DISTINCT
-- DISTINCT counts different problems, rather than multiple papers on the same problem. HAVING filters the grouped result.
SELECT m.mathematician_id, m.mathematician_name, COUNT(DISTINCT c.problem_id) AS problem_count
FROM MATHEMATICIAN AS m
INNER JOIN CONTRIBUTION AS c ON c.mathematician_id = m.mathematician_id
GROUP BY m.mathematician_id, m.mathematician_name
HAVING COUNT(DISTINCT c.problem_id) > 1
ORDER BY problem_count DESC, m.mathematician_name;

-- 12. Find problems without recorded contributions
-- Concept: LEFT JOIN · IS NULL
-- The NULL child key identifies missing relationships. This means missing from our small dataset, not that nobody has researched the problem.
SELECT p.problem_id, p.problem_name
FROM MATH_PROBLEM AS p
LEFT JOIN CONTRIBUTION AS c ON c.problem_id = p.problem_id
WHERE c.contribution_id IS NULL
ORDER BY p.problem_name;

-- 13. Find people without recorded contributions
-- Concept: NOT EXISTS · Correlated subquery
-- The subquery depends on each outer mathematician. NOT EXISTS succeeds when no matching child row exists.
SELECT m.mathematician_id, m.mathematician_name
FROM MATHEMATICIAN AS m
WHERE NOT EXISTS (SELECT 1 FROM CONTRIBUTION AS c WHERE c.mathematician_id = m.mathematician_id)
ORDER BY m.mathematician_name;

-- 14. Read the research relationships
-- Concept: INNER JOIN
-- Two joins traverse the junction entity and replace foreign-key IDs with readable parent names.
SELECT c.contribution_id, m.mathematician_name, p.problem_name, c.contribution_year, c.contribution_type
FROM CONTRIBUTION AS c
INNER JOIN MATHEMATICIAN AS m ON m.mathematician_id = c.mathematician_id
INNER JOIN MATH_PROBLEM AS p ON p.problem_id = c.problem_id
ORDER BY c.contribution_year, c.contribution_id;

-- 15. Problems with more than one contribution
-- Concept: GROUP BY · HAVING
-- WHERE filters individual rows, whereas HAVING filters groups after aggregates are computed.
SELECT p.problem_id, p.problem_name, COUNT(c.contribution_id) AS contribution_count
FROM MATH_PROBLEM AS p
INNER JOIN CONTRIBUTION AS c ON c.problem_id = p.problem_id
GROUP BY p.problem_id, p.problem_name
HAVING COUNT(c.contribution_id) > 1
ORDER BY contribution_count DESC, p.problem_name;

-- 16. Research contributions after 1950
-- Concept: WHERE · ORDER BY
-- A numeric comparison followed by descending order shows recent contributions first.
SELECT contribution_id, contribution_year, contribution_type FROM CONTRIBUTION WHERE contribution_year > 1950 ORDER BY contribution_year DESC, contribution_id;

-- 17. Prizes above the database average
-- Concept: Scalar subquery · AVG
-- The scalar subquery produces one value for the outer comparison. This average includes zero-prize records.
SELECT problem_name, prize_amount
FROM MATH_PROBLEM
WHERE prize_amount > (SELECT AVG(prize_amount) FROM MATH_PROBLEM)
ORDER BY prize_amount DESC, problem_name;

-- 18. People with the most recorded contributions
-- Concept: Subquery · HAVING · MAX
-- A derived table counts each person's contributions. Comparing against its maximum returns all tied leaders, not an arbitrary LIMIT 1 winner.
SELECT m.mathematician_id, m.mathematician_name, COUNT(c.contribution_id) AS contribution_count
FROM MATHEMATICIAN AS m
INNER JOIN CONTRIBUTION AS c ON c.mathematician_id = m.mathematician_id
GROUP BY m.mathematician_id, m.mathematician_name
HAVING COUNT(c.contribution_id) = (
  SELECT MAX(counts.total) FROM (
    SELECT COUNT(*) AS total FROM CONTRIBUTION GROUP BY mathematician_id
  ) AS counts
)
ORDER BY m.mathematician_name;

-- 19. Count problems in each field
-- Concept: GROUP BY · COUNT
-- GROUP BY collects matching field values into one row per field.
SELECT math_field, COUNT(*) AS problem_count FROM MATH_PROBLEM GROUP BY math_field ORDER BY problem_count DESC, math_field;

-- 20. Find the earliest proposed problem
-- Concept: Scalar subquery · MIN
-- MIN ignores unknown years. The outer equality preserves ties for the earliest known proposal year.
SELECT problem_name, proposed_year FROM MATH_PROBLEM WHERE proposed_year = (SELECT MIN(proposed_year) FROM MATH_PROBLEM) ORDER BY problem_name;

-- 21. List the recorded countries
-- Concept: DISTINCT
-- DISTINCT removes duplicate values from the selected columns.
SELECT DISTINCT country FROM MATHEMATICIAN WHERE country IS NOT NULL ORDER BY country;

-- 22. Search names containing Prime
-- Concept: LIKE
-- The percent wildcard matches any number of characters before or after the search term.
SELECT problem_name, math_field FROM MATH_PROBLEM WHERE problem_name LIKE '%Prime%' ORDER BY problem_name;

-- 23. Teaching scores between eight and nine
-- Concept: BETWEEN
-- BETWEEN includes both endpoints. NULL scores do not satisfy the range comparison.
SELECT contribution_id, contribution_type, significance_score FROM CONTRIBUTION WHERE significance_score BETWEEN 8.00 AND 9.00 ORDER BY significance_score, contribution_id;

-- 24. Problems in topology or graph theory
-- Concept: IN
-- IN tests whether a value is a member of a fixed list, avoiding repeated OR comparisons.
SELECT problem_name, math_field, status FROM MATH_PROBLEM WHERE math_field IN ('Topology', 'Graph Theory') ORDER BY math_field, problem_name;

-- 25. Total recorded active prize amounts
-- Concept: SUM
-- SUM adds exact decimal amounts. COALESCE returns zero when no qualifying rows exist.
SELECT COALESCE(SUM(prize_amount), 0) AS total_prize_usd FROM MATH_PROBLEM WHERE has_prize = TRUE;

-- 26. Earliest and latest proposal years
-- Concept: MIN · MAX
-- Several aggregate functions can summarize one table in a single result row.
SELECT MIN(proposed_year) AS earliest_year, MAX(proposed_year) AS latest_year FROM MATH_PROBLEM;

-- 27. Problems with recorded research
-- Concept: EXISTS · Correlated subquery
-- EXISTS asks only whether a matching row exists, so multiple child records do not duplicate the outer problem.
SELECT p.problem_id, p.problem_name
FROM MATH_PROBLEM AS p
WHERE EXISTS (SELECT 1 FROM CONTRIBUTION AS c WHERE c.problem_id = p.problem_id)
ORDER BY p.problem_name;

-- 28. People with a teaching score of at least nine
-- Concept: IN subquery
-- The inner SELECT supplies a set of IDs to the outer IN condition. Duplicate IDs do not duplicate the outer people.
SELECT mathematician_name FROM MATHEMATICIAN WHERE mathematician_id IN (SELECT mathematician_id FROM CONTRIBUTION WHERE significance_score >= 9.00) ORDER BY mathematician_name;

-- 29. Contributions above their problem's average
-- Concept: Correlated subquery · AVG
-- The average is recalculated logically for the current outer problem. Comparison with a per-problem average makes this a correlated subquery.
SELECT c.contribution_id, p.problem_name, c.significance_score
FROM CONTRIBUTION AS c
INNER JOIN MATH_PROBLEM AS p ON p.problem_id = c.problem_id
WHERE c.significance_score > (SELECT AVG(other.significance_score) FROM CONTRIBUTION AS other WHERE other.problem_id = c.problem_id)
ORDER BY p.problem_name, c.contribution_id;

-- 30. Preserve all mathematicians with a right join
-- Concept: RIGHT JOIN
-- RIGHT JOIN retains the right-hand mathematician table. Unmatched contribution columns contain NULL.
SELECT m.mathematician_name, c.contribution_id, c.contribution_type
FROM CONTRIBUTION AS c
RIGHT JOIN MATHEMATICIAN AS m ON m.mathematician_id = c.mathematician_id
ORDER BY m.mathematician_name, c.contribution_id;

-- 31. Pair different problems in the same field
-- Concept: SELF JOIN
-- Two aliases join a table to itself. The less-than key condition excludes self-pairs and reversed duplicates.
SELECT a.problem_name AS first_problem, b.problem_name AS second_problem, a.math_field
FROM MATH_PROBLEM AS a
INNER JOIN MATH_PROBLEM AS b ON a.math_field = b.math_field AND a.problem_id < b.problem_id
ORDER BY a.math_field, a.problem_name, b.problem_name;

-- 32. Sort problems by proposal year
-- Concept: ORDER BY · NULL handling
-- Unknown years appear last. A second key sorts known years from newest to oldest, and names break ties.
SELECT problem_name, proposed_year FROM MATH_PROBLEM ORDER BY proposed_year IS NULL, proposed_year DESC, problem_name;

-- 33. Find incomplete biographical records
-- Concept: IS NULL
-- IS NULL tests missing information. Equality to NULL does not work because SQL uses three-valued logic.
SELECT mathematician_name, country FROM MATHEMATICIAN WHERE birth_date IS NULL ORDER BY mathematician_name;

-- 34. Problems proposed during the twentieth century
-- Concept: BETWEEN · ORDER BY
-- The inclusive numeric range uses the conventional years 1901 through 2000 for the twentieth century.
SELECT problem_name, proposed_year FROM MATH_PROBLEM WHERE proposed_year BETWEEN 1901 AND 2000 ORDER BY proposed_year, problem_name;
