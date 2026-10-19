"""
Integration tests for Alembic database migrations.
Verifies that database migrations execute cleanly and upgrade to head.
"""
import tempfile
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head_on_clean_database():
    """Verifies that running alembic upgrade head creates all expected tables."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        tmp_path = Path(tmp_db.name)

    try:
        db_url = f"sqlite:///{tmp_path.as_posix()}"
        alembic_cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        # Run migration upgrade to head
        command.upgrade(alembic_cfg, "head")

        # Inspect created tables
        test_engine = create_engine(db_url)
        inspector = inspect(test_engine)
        table_names = inspector.get_table_names()

        expected_tables = [
            "sources",
            "companies",
            "categories",
            "news_records",
            "article_duplicates",
            "source_records",
            "article_companies",
            "article_categories",
            "collection_logs",
            "alembic_version",
        ]

        for expected in expected_tables:
            assert expected in table_names, f"Expected table '{expected}' missing after migration"

        # Check critical indexes and columns
        news_indexes = [idx["name"] for idx in inspector.get_indexes("news_records")]
        assert "ix_news_records_record_hash" in news_indexes
        assert "idx_pub_sym" in news_indexes

        news_cols = [c["name"] for c in inspector.get_columns("news_records")]
        assert "last_seen_at" in news_cols
        assert "validation_status" in news_cols
        assert "provenance" in news_cols

        log_cols = [c["name"] for c in inspector.get_columns("collection_logs")]
        assert "items_failed" in log_cols

        # Test downgrade to base
        command.downgrade(alembic_cfg, "base")
        inspector_down = inspect(test_engine)
        remaining_tables = [t for t in inspector_down.get_table_names() if t != "alembic_version"]
        assert len(remaining_tables) == 0, f"Expected all tables dropped on downgrade base, found: {remaining_tables}"

        # Test re-upgrade to head
        command.upgrade(alembic_cfg, "head")
        inspector_reup = inspect(test_engine)
        for expected in expected_tables:
            assert expected in inspector_reup.get_table_names(), f"Expected table '{expected}' missing after re-upgrade"

    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
