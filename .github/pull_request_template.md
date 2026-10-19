## Overview
Briefly describe the purpose of this Pull Request and what problems it solves.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New data source collector (financial news / regulatory / exchange)
- [ ] Core data pipeline enhancement (normalization / deduplication / entity resolution)
- [ ] Database schema migration or ORM optimization
- [ ] Frontend enhancement or UI fix
- [ ] Documentation update

## Verification & Testing
- [ ] All tests pass locally (`pytest -v`)
- [ ] Offline deterministic fixtures provided in `tests/fixtures/` for any new collector
- [ ] No unmocked live third-party network calls in test suite
- [ ] Frontend builds cleanly (`cd frontend && npm run build`)
- [ ] Security checks verified (no leaked credentials, safe database queries, CWE-1236 safe)

## Related Issues
Closes #(issue)
