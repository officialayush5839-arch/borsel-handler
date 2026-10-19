# Contributing to Borsel Handler

Thank you for your interest in contributing to **Borsel Handler — AI-Powered Indian Financial Intelligence Platform**! We welcome contributions from data engineers, quantitative developers, financial analysts, and software engineers.

---

## 1. Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 2. Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/officialayush5839-arch/borsel-handler.git
   cd borsel-handler
   ```

2. Set up a Python 3.11+ virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Run the test suite to verify baseline setup:
   ```bash
   pytest -v
   ```

---

## 3. Engineering Guidelines

- **Deterministic Tests:** All collectors must include offline deterministic fixtures under `tests/fixtures/`. Tests must never depend on unmocked live third-party network access.
- **Data Engineering Separation:** Keep source-specific parsing isolated within `borsel_handler/collectors/` and shared ingestion logic in `borsel_handler/core/`.
- **Compliance & Security:** Do not implement CAPTCHA bypasses, rotating residential proxy evasion, or credential logging.
- **Relational Schema Migrations:** All database modifications must be managed via Alembic migrations (`alembic/versions/`).
- **Spreadsheet Formula Safety (CWE-1236):** Never export raw untrusted formula strings (`=`, `+`, `-`, `@`) without proper prefix escaping.

---

## 4. Submitting a Pull Request

1. Create a feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Commit your changes with descriptive conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`).
3. Ensure all automated tests pass:
   ```bash
   pytest
   cd frontend && npm run build && cd ..
   ```
4. Push to your fork and submit a Pull Request describing your changes, motivation, and test evidence.
