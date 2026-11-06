# MathMyst entity relationship diagram

```mermaid
erDiagram
    MATH_PROBLEM ||--o{ CONTRIBUTION : "has recorded"
    MATHEMATICIAN ||--o{ CONTRIBUTION : "is credited in"
    MATH_PROBLEM {
        INT problem_id PK "AUTO_INCREMENT"
        VARCHAR problem_name UK "100 characters, NOT NULL"
        VARCHAR math_field "50 characters, NOT NULL"
        INT proposed_year "nullable, positive"
        VARCHAR status "Solved or Unsolved"
        DECIMAL prize_amount "12,2; nonnegative"
        BOOLEAN has_prize "default FALSE"
    }
    MATHEMATICIAN {
        INT mathematician_id PK "AUTO_INCREMENT"
        VARCHAR mathematician_name "80 characters, NOT NULL"
        VARCHAR country "40 characters, nullable"
        DATE birth_date "nullable"
        VARCHAR specialization "50 characters, nullable"
    }
    CONTRIBUTION {
        INT contribution_id PK "AUTO_INCREMENT"
        INT problem_id FK "NOT NULL"
        INT mathematician_id FK "NOT NULL"
        INT contribution_year "NOT NULL, positive"
        VARCHAR contribution_type "40 characters, nullable"
        DECIMAL significance_score "4,2; nullable, 0 through 10"
    }
```

The `||` end means exactly one parent, and the `o{` end means zero or many children. Thus, every contribution belongs to one existing problem and one existing mathematician. A problem or mathematician may exist without a contribution.

`MATH_PROBLEM` and `MATHEMATICIAN` have a many-to-many relationship through `CONTRIBUTION`. For example, several mathematicians may contribute to one problem, and one mathematician may contribute to several problems. The contribution table also stores facts about the association: year, contribution type, and significance score.

Both foreign keys use `ON DELETE RESTRICT`: a referenced parent cannot be removed while its contributions remain. Both use `ON UPDATE CASCADE`: if a referenced key is changed directly in SQL, the related foreign-key values follow it. The web forms do not edit primary keys.

Exactly three main application entities are present. Views are saved query definitions rather than additional application entities. Any disposable table used for DDL practice is separate from the application model and must be removed after the exercise.
