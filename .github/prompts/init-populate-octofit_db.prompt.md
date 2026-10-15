---
mode: 'agent'
description: 'Configure SQLite and seed andresfit.db for the AndresFit multi-tier application'
---

Set up and populate the data tier for `andresfit-tracker/backend`.

Requirements:

1. Use SQLite with SQLAlchemy ORM.
2. Use SQLite database file `andresfit.db` in the backend directory.
3. Create SQLAlchemy models for users, teams, activities, leaderboard, and workouts.
4. Add a seed script at `app/seed.py`.
5. Include this help/description text in the seed script comments or logs:
   `Seed the andresfit database with test data`.
6. Insert realistic sample data for all tables.
7. Verify data creation with API route responses.
