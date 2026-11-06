"""Developer-approved read-only SQL. Requests select an ID, never supply SQL.

Keep database/queries.sql synchronized with this catalog. Each statement is a
single SELECT without user interpolation or access to server metadata/files.
"""

QUERIES = [
    {
        "id": "all-problems", "title": "Explore every mathematical problem",
        "concept": "SELECT",
        "sql": "SELECT * FROM MATH_PROBLEM ORDER BY problem_id;",
        "explanation": "SELECT reads columns from a table. The primary key gives each row a stable identity.",
    },
    {
        "id": "unsolved", "title": "Find unsolved problems", "concept": "WHERE",
        "sql": "SELECT problem_name, math_field, proposed_year FROM MATH_PROBLEM WHERE status = 'Unsolved' ORDER BY problem_name;",
        "explanation": "WHERE keeps only rows that satisfy a condition before the result is returned.",
    },
    {
        "id": "before-1900", "title": "Problems proposed before 1900", "concept": "WHERE",
        "sql": "SELECT problem_name, proposed_year FROM MATH_PROBLEM WHERE proposed_year < 1900 ORDER BY proposed_year, problem_name;",
        "explanation": "A comparison filters numeric values. Unknown years (NULL) do not satisfy this comparison.",
    },
    {
        "id": "number-theory", "title": "Explore number theory", "concept": "WHERE",
        "sql": "SELECT problem_name, status FROM MATH_PROBLEM WHERE math_field = 'Number Theory' ORDER BY problem_name;",
        "explanation": "Equality selects problems belonging to a particular mathematical field.",
    },
    {
        "id": "german-mathematicians", "title": "Mathematicians from Germany", "concept": "WHERE",
        "sql": "SELECT mathematician_name, specialization FROM MATHEMATICIAN WHERE country = 'Germany' ORDER BY mathematician_name;",
        "explanation": "This selection operates on the country attribute of the mathematician entity.",
    },
    {
        "id": "alphabetical", "title": "Problems in alphabetical order", "concept": "ORDER BY",
        "sql": "SELECT problem_name, proposed_year, status FROM MATH_PROBLEM ORDER BY problem_name ASC;",
        "explanation": "ORDER BY sorts the output; ASC requests ascending order.",
    },
    {
        "id": "count-unsolved", "title": "Count unsolved problems", "concept": "COUNT",
        "sql": "SELECT COUNT(*) AS unsolved_problems FROM MATH_PROBLEM WHERE status = 'Unsolved';",
        "explanation": "COUNT(*) counts the rows left after WHERE filters the table.",
    },
    {
        "id": "highest-prize", "title": "Find the highest recorded prize", "concept": "MAX",
        "sql": "SELECT MAX(prize_amount) AS highest_prize FROM MATH_PROBLEM;",
        "explanation": "MAX returns the greatest non-NULL value. Prize amounts are stored as exact DECIMAL values in USD.",
    },
    {
        "id": "average-score", "title": "Average teaching significance score", "concept": "AVG",
        "sql": "SELECT ROUND(AVG(significance_score), 2) AS average_score FROM CONTRIBUTION;",
        "explanation": "AVG ignores NULL scores. These example ratings are subjective demonstration data, not historical facts.",
    },
    {
        "id": "contributions-per-problem", "title": "Count contributions for every problem", "concept": "LEFT JOIN · GROUP BY · COUNT",
        "sql": "SELECT p.problem_id, p.problem_name, COUNT(c.contribution_id) AS contribution_count\nFROM MATH_PROBLEM AS p\nLEFT JOIN CONTRIBUTION AS c ON c.problem_id = p.problem_id\nGROUP BY p.problem_id, p.problem_name\nORDER BY contribution_count DESC, p.problem_name;",
        "explanation": "LEFT JOIN preserves problems without contributions. COUNT(child_id), unlike COUNT(*), gives zero for an unmatched parent.",
    },
    {
        "id": "multiple-problems", "title": "People contributing to multiple problems", "concept": "GROUP BY · HAVING · DISTINCT",
        "sql": "SELECT m.mathematician_id, m.mathematician_name, COUNT(DISTINCT c.problem_id) AS problem_count\nFROM MATHEMATICIAN AS m\nINNER JOIN CONTRIBUTION AS c ON c.mathematician_id = m.mathematician_id\nGROUP BY m.mathematician_id, m.mathematician_name\nHAVING COUNT(DISTINCT c.problem_id) > 1\nORDER BY problem_count DESC, m.mathematician_name;",
        "explanation": "DISTINCT counts different problems, rather than multiple papers on the same problem. HAVING filters the grouped result.",
    },
    {
        "id": "problems-without-contributions", "title": "Find problems without recorded contributions", "concept": "LEFT JOIN · IS NULL",
        "sql": "SELECT p.problem_id, p.problem_name\nFROM MATH_PROBLEM AS p\nLEFT JOIN CONTRIBUTION AS c ON c.problem_id = p.problem_id\nWHERE c.contribution_id IS NULL\nORDER BY p.problem_name;",
        "explanation": "The NULL child key identifies missing relationships. This means missing from our small dataset, not that nobody has researched the problem.",
    },
    {
        "id": "people-without-contributions", "title": "Find people without recorded contributions", "concept": "NOT EXISTS · Correlated subquery",
        "sql": "SELECT m.mathematician_id, m.mathematician_name\nFROM MATHEMATICIAN AS m\nWHERE NOT EXISTS (SELECT 1 FROM CONTRIBUTION AS c WHERE c.mathematician_id = m.mathematician_id)\nORDER BY m.mathematician_name;",
        "explanation": "The subquery depends on each outer mathematician. NOT EXISTS succeeds when no matching child row exists.",
    },
    {
        "id": "research-relationships", "title": "Read the research relationships", "concept": "INNER JOIN",
        "sql": "SELECT c.contribution_id, m.mathematician_name, p.problem_name, c.contribution_year, c.contribution_type\nFROM CONTRIBUTION AS c\nINNER JOIN MATHEMATICIAN AS m ON m.mathematician_id = c.mathematician_id\nINNER JOIN MATH_PROBLEM AS p ON p.problem_id = c.problem_id\nORDER BY c.contribution_year, c.contribution_id;",
        "explanation": "Two joins traverse the junction entity and replace foreign-key IDs with readable parent names.",
    },
    {
        "id": "multiple-contributions", "title": "Problems with more than one contribution", "concept": "GROUP BY · HAVING",
        "sql": "SELECT p.problem_id, p.problem_name, COUNT(c.contribution_id) AS contribution_count\nFROM MATH_PROBLEM AS p\nINNER JOIN CONTRIBUTION AS c ON c.problem_id = p.problem_id\nGROUP BY p.problem_id, p.problem_name\nHAVING COUNT(c.contribution_id) > 1\nORDER BY contribution_count DESC, p.problem_name;",
        "explanation": "WHERE filters individual rows, whereas HAVING filters groups after aggregates are computed.",
    },
    {
        "id": "after-1950", "title": "Research contributions after 1950", "concept": "WHERE · ORDER BY",
        "sql": "SELECT contribution_id, contribution_year, contribution_type FROM CONTRIBUTION WHERE contribution_year > 1950 ORDER BY contribution_year DESC, contribution_id;",
        "explanation": "A numeric comparison followed by descending order shows recent contributions first.",
    },
    {
        "id": "above-average-prize", "title": "Prizes above the database average", "concept": "Scalar subquery · AVG",
        "sql": "SELECT problem_name, prize_amount\nFROM MATH_PROBLEM\nWHERE prize_amount > (SELECT AVG(prize_amount) FROM MATH_PROBLEM)\nORDER BY prize_amount DESC, problem_name;",
        "explanation": "The scalar subquery produces one value for the outer comparison. This average includes zero-prize records.",
    },
    {
        "id": "most-contributions", "title": "People with the most recorded contributions", "concept": "Subquery · HAVING · MAX",
        "sql": "SELECT m.mathematician_id, m.mathematician_name, COUNT(c.contribution_id) AS contribution_count\nFROM MATHEMATICIAN AS m\nINNER JOIN CONTRIBUTION AS c ON c.mathematician_id = m.mathematician_id\nGROUP BY m.mathematician_id, m.mathematician_name\nHAVING COUNT(c.contribution_id) = (\n  SELECT MAX(counts.total) FROM (\n    SELECT COUNT(*) AS total FROM CONTRIBUTION GROUP BY mathematician_id\n  ) AS counts\n)\nORDER BY m.mathematician_name;",
        "explanation": "A derived table counts each person's contributions. Comparing against its maximum returns all tied leaders, not an arbitrary LIMIT 1 winner.",
    },
    {
        "id": "problems-by-field", "title": "Count problems in each field", "concept": "GROUP BY · COUNT",
        "sql": "SELECT math_field, COUNT(*) AS problem_count FROM MATH_PROBLEM GROUP BY math_field ORDER BY problem_count DESC, math_field;",
        "explanation": "GROUP BY collects matching field values into one row per field.",
    },
    {
        "id": "earliest-problem", "title": "Find the earliest proposed problem", "concept": "Scalar subquery · MIN",
        "sql": "SELECT problem_name, proposed_year FROM MATH_PROBLEM WHERE proposed_year = (SELECT MIN(proposed_year) FROM MATH_PROBLEM) ORDER BY problem_name;",
        "explanation": "MIN ignores unknown years. The outer equality preserves ties for the earliest known proposal year.",
    },
    {
        "id": "distinct-countries", "title": "List the recorded countries", "concept": "DISTINCT",
        "sql": "SELECT DISTINCT country FROM MATHEMATICIAN WHERE country IS NOT NULL ORDER BY country;",
        "explanation": "DISTINCT removes duplicate values from the selected columns.",
    },
    {
        "id": "prime-search", "title": "Search names containing Prime", "concept": "LIKE",
        "sql": "SELECT problem_name, math_field FROM MATH_PROBLEM WHERE problem_name LIKE '%Prime%' ORDER BY problem_name;",
        "explanation": "The percent wildcard matches any number of characters before or after the search term.",
    },
    {
        "id": "score-range", "title": "Teaching scores between eight and nine", "concept": "BETWEEN",
        "sql": "SELECT contribution_id, contribution_type, significance_score FROM CONTRIBUTION WHERE significance_score BETWEEN 8.00 AND 9.00 ORDER BY significance_score, contribution_id;",
        "explanation": "BETWEEN includes both endpoints. NULL scores do not satisfy the range comparison.",
    },
    {
        "id": "selected-fields", "title": "Problems in topology or graph theory", "concept": "IN",
        "sql": "SELECT problem_name, math_field, status FROM MATH_PROBLEM WHERE math_field IN ('Topology', 'Graph Theory') ORDER BY math_field, problem_name;",
        "explanation": "IN tests whether a value is a member of a fixed list, avoiding repeated OR comparisons.",
    },
    {
        "id": "total-prizes", "title": "Total recorded active prize amounts", "concept": "SUM",
        "sql": "SELECT COALESCE(SUM(prize_amount), 0) AS total_prize_usd FROM MATH_PROBLEM WHERE has_prize = TRUE;",
        "explanation": "SUM adds exact decimal amounts. COALESCE returns zero when no qualifying rows exist.",
    },
    {
        "id": "year-range", "title": "Earliest and latest proposal years", "concept": "MIN · MAX",
        "sql": "SELECT MIN(proposed_year) AS earliest_year, MAX(proposed_year) AS latest_year FROM MATH_PROBLEM;",
        "explanation": "Several aggregate functions can summarize one table in a single result row.",
    },
    {
        "id": "has-contributions", "title": "Problems with recorded research", "concept": "EXISTS · Correlated subquery",
        "sql": "SELECT p.problem_id, p.problem_name\nFROM MATH_PROBLEM AS p\nWHERE EXISTS (SELECT 1 FROM CONTRIBUTION AS c WHERE c.problem_id = p.problem_id)\nORDER BY p.problem_name;",
        "explanation": "EXISTS asks only whether a matching row exists, so multiple child records do not duplicate the outer problem.",
    },
    {
        "id": "high-score-researchers", "title": "People with a teaching score of at least nine", "concept": "IN subquery",
        "sql": "SELECT mathematician_name FROM MATHEMATICIAN WHERE mathematician_id IN (SELECT mathematician_id FROM CONTRIBUTION WHERE significance_score >= 9.00) ORDER BY mathematician_name;",
        "explanation": "The inner SELECT supplies a set of IDs to the outer IN condition. Duplicate IDs do not duplicate the outer people.",
    },
    {
        "id": "above-own-problem-average", "title": "Contributions above their problem's average", "concept": "Correlated subquery · AVG",
        "sql": "SELECT c.contribution_id, p.problem_name, c.significance_score\nFROM CONTRIBUTION AS c\nINNER JOIN MATH_PROBLEM AS p ON p.problem_id = c.problem_id\nWHERE c.significance_score > (SELECT AVG(other.significance_score) FROM CONTRIBUTION AS other WHERE other.problem_id = c.problem_id)\nORDER BY p.problem_name, c.contribution_id;",
        "explanation": "The average is recalculated logically for the current outer problem. Comparison with a per-problem average makes this a correlated subquery.",
    },
    {
        "id": "right-join-people", "title": "Preserve all mathematicians with a right join", "concept": "RIGHT JOIN",
        "sql": "SELECT m.mathematician_name, c.contribution_id, c.contribution_type\nFROM CONTRIBUTION AS c\nRIGHT JOIN MATHEMATICIAN AS m ON m.mathematician_id = c.mathematician_id\nORDER BY m.mathematician_name, c.contribution_id;",
        "explanation": "RIGHT JOIN retains the right-hand mathematician table. Unmatched contribution columns contain NULL.",
    },
    {
        "id": "same-field-pairs", "title": "Pair different problems in the same field", "concept": "SELF JOIN",
        "sql": "SELECT a.problem_name AS first_problem, b.problem_name AS second_problem, a.math_field\nFROM MATH_PROBLEM AS a\nINNER JOIN MATH_PROBLEM AS b ON a.math_field = b.math_field AND a.problem_id < b.problem_id\nORDER BY a.math_field, a.problem_name, b.problem_name;",
        "explanation": "Two aliases join a table to itself. The less-than key condition excludes self-pairs and reversed duplicates.",
    },
    {
        "id": "newest-proposals", "title": "Sort problems by proposal year", "concept": "ORDER BY · NULL handling",
        "sql": "SELECT problem_name, proposed_year FROM MATH_PROBLEM ORDER BY proposed_year IS NULL, proposed_year DESC, problem_name;",
        "explanation": "Unknown years appear last. A second key sorts known years from newest to oldest, and names break ties.",
    },
    {
        "id": "missing-birth-dates", "title": "Find incomplete biographical records", "concept": "IS NULL",
        "sql": "SELECT mathematician_name, country FROM MATHEMATICIAN WHERE birth_date IS NULL ORDER BY mathematician_name;",
        "explanation": "IS NULL tests missing information. Equality to NULL does not work because SQL uses three-valued logic.",
    },
    {
        "id": "twentieth-century", "title": "Problems proposed during the twentieth century", "concept": "BETWEEN · ORDER BY",
        "sql": "SELECT problem_name, proposed_year FROM MATH_PROBLEM WHERE proposed_year BETWEEN 1901 AND 2000 ORDER BY proposed_year, problem_name;",
        "explanation": "The inclusive numeric range uses the conventional years 1901 through 2000 for the twentieth century.",
    },
]

QUERY_BY_ID = {query["id"]: query for query in QUERIES}
