# Contributing to Dashboard Metabase + Colección Analítica para E-commerce

Thank you for your interest in contributing! This is a portfolio project that demonstrates an analytical dashboard for e-commerce using PostgreSQL, Metabase, and synthetic data. Whether you're fixing a bug, improving docs, or suggesting a feature — you're welcome here.

---

## How to Contribute

| Type | Where | How |
|------|-------|-----|
| **Bug reports** | [Issues](https://github.com/Fisherk2/dashboard-metabase-analiticas/issues) | Open a new issue with reproduction steps |
| **Feature suggestions** | [Issues](https://github.com/Fisherk2/dashboard-metabase-analiticas/issues) / [Discussions](https://github.com/Fisherk2/dashboard-metabase-analiticas/discussions) | Describe the idea and why it fits |
| **Documentation** | Pull requests | Fix typos, clarify wording, add examples |
| **Code improvements** | Pull requests | Refactoring, optimization, new features |

All contributions are subject to the [MIT License](LICENSE).

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork:

   ```bash
   git clone https://github.com/your-username/dashboard-metabase-analiticas.git
   ```

3. **Create a branch:**

   ```bash
   git checkout -b feature/your-feature
   ```

4. **Set up and run the project:**

   ```bash
   cp .env.example .env
   make setup
   ```

   This installs dependencies, starts services, initializes the database, and generates synthetic data.

---

## Development Workflow

This project follows **TDD + vertical slicing**:

- **RED** — Write a failing test that describes the expected behavior.
- **GREEN** — Write the minimum code to make it pass.
- **REFACTOR** — Clean up while keeping tests green.

**Before committing:**

- Run `make test` and confirm all tests pass.
- For SQL changes, validate with `EXPLAIN ANALYZE` (target: <2s per query).

**Commit messages** follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add monthly rotation materialized view
fix: correct stock alert threshold calculation
docs: update Metabase setup guide
refactor: simplify data generator class
test: add persistence roundtrip test
```

---

## Code Standards

Full conventions are documented in [docs/CODE_STYLE.md](docs/CODE_STYLE.md). Key rules:

**SQL**
- Keywords in `UPPERCASE`, 4-space indent.
- Explicit `INNER JOIN` / `LEFT JOIN` only — never implicit joins.
- Always list columns explicitly, never `SELECT *`.
- Run `EXPLAIN ANALYZE` before committing any query.

**Python**
- PEP 8, `snake_case` for variables/functions, `PascalCase` for classes.
- Type hints on all public functions.
- Google-style docstrings for classes and functions.
- Use transactions (`BEGIN`/`COMMIT`) in all database scripts.

**Makefile**
- Targets use `kebab-case` with a `##` comment for `make help`.
- Load credentials from `.env` — never hardcode them.

**Credentials**
- All secrets go in `.env` (never committed).
- Never hardcode passwords in SQL, Python, YAML, or scripts.

---

## Pull Request Process

1. Ensure all tests pass: `make test`
2. Keep PRs **focused on a single change** — split large changes into separate PRs.
3. Reference related issues: `Closes #123` or `Related to #456`.
4. Target the **`develop`** branch, not `main`.
5. Wait for review before merging. Address all feedback before the final merge.

---

## Reporting Issues

When opening an issue, please include:

- **Description** — What happened and why it's a problem.
- **Steps to reproduce** — Commands, actions, or inputs to trigger the issue.
- **Expected vs. actual behavior** — What you expected and what actually happened.
- **Environment** — OS, Docker version, Python version, and any relevant config.

---

## Code of Conduct

Be respectful, constructive, and patient. This is a learning project built by one person — every contribution is appreciated. Harassment, trolling, and disrespectful behavior will not be tolerated.

---

*Happy contributing!* 🚀
