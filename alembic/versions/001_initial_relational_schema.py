"""001_initial_relational_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-19 16:50:00.000000

Baseline migration establishing complete relational schema:
- sources
- companies
- categories
- news_records (articles)
- article_duplicates
- source_records
- article_companies
- article_categories
- collection_logs (collection_runs)
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. sources
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('source_type', sa.String(length=64), nullable=False),
        sa.Column('base_url', sa.String(length=1024), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('rate_limit_rps', sa.Float(), nullable=False, server_default='2.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    try:
        op.create_index('ix_sources_id', 'sources', ['id'], unique=False)
        op.create_index('ix_sources_code', 'sources', ['code'], unique=True)
        op.create_index('ix_sources_source_type', 'sources', ['source_type'], unique=False)
    except Exception:
        pass

    # 2. companies
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('symbol', sa.String(length=32), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('isin', sa.String(length=32), nullable=True),
        sa.Column('bse_code', sa.String(length=32), nullable=True),
        sa.Column('sector', sa.String(length=128), nullable=True),
        sa.Column('industry', sa.String(length=128), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    try:
        op.create_index('ix_companies_id', 'companies', ['id'], unique=False)
        op.create_index('ix_companies_symbol', 'companies', ['symbol'], unique=True)
        op.create_index('ix_companies_isin', 'companies', ['isin'], unique=True)
        op.create_index('ix_companies_bse_code', 'companies', ['bse_code'], unique=False)
        op.create_index('ix_companies_sector', 'companies', ['sector'], unique=False)
    except Exception:
        pass

    # 3. categories
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_category', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    try:
        op.create_index('ix_categories_id', 'categories', ['id'], unique=False)
        op.create_index('ix_categories_code', 'categories', ['code'], unique=True)
    except Exception:
        pass

    # 4. news_records (articles)
    op.create_table(
        'news_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('record_hash', sa.String(length=64), nullable=False),
        sa.Column('canonical_url', sa.String(length=1024), nullable=False),
        sa.Column('original_url', sa.String(length=2048), nullable=False),
        sa.Column('source_name', sa.String(length=128), nullable=False),
        sa.Column('source_type', sa.String(length=64), nullable=False),
        sa.Column('source_record_id', sa.String(length=256), nullable=True),
        sa.Column('title', sa.String(length=1024), nullable=False),
        sa.Column('snippet', sa.Text(), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('collected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('validation_status', sa.String(length=32), nullable=False, server_default='valid'),
        sa.Column('company_name', sa.String(length=256), nullable=True),
        sa.Column('symbol', sa.String(length=32), nullable=True),
        sa.Column('sector', sa.String(length=128), nullable=True),
        sa.Column('category', sa.String(length=128), nullable=False, server_default='general_financial_news'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('raw_metadata', sa.JSON(), nullable=False),
        sa.Column('provenance', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_name', 'source_record_id', name='uq_source_record_id'),
        if_not_exists=True,
    )
    try:
        op.create_index('ix_news_records_id', 'news_records', ['id'], unique=False)
        op.create_index('ix_news_records_record_hash', 'news_records', ['record_hash'], unique=True)
        op.create_index('ix_news_records_canonical_url', 'news_records', ['canonical_url'], unique=False)
        op.create_index('ix_news_records_source_name', 'news_records', ['source_name'], unique=False)
        op.create_index('ix_news_records_source_type', 'news_records', ['source_type'], unique=False)
        op.create_index('ix_news_records_published_at', 'news_records', ['published_at'], unique=False)
        op.create_index('ix_news_records_company_name', 'news_records', ['company_name'], unique=False)
        op.create_index('ix_news_records_symbol', 'news_records', ['symbol'], unique=False)
        op.create_index('ix_news_records_sector', 'news_records', ['sector'], unique=False)
        op.create_index('ix_news_records_category', 'news_records', ['category'], unique=False)
        op.create_index('idx_pub_sym', 'news_records', ['symbol', 'published_at'], unique=False)
        op.create_index('idx_cat_pub', 'news_records', ['category', 'published_at'], unique=False)
        op.create_index('idx_src_pub', 'news_records', ['source_name', 'published_at'], unique=False)
    except Exception:
        pass

    # 5. article_duplicates
    op.create_table(
        'article_duplicates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('canonical_article_id', sa.Integer(), nullable=True),
        sa.Column('duplicate_url', sa.String(length=2048), nullable=False),
        sa.Column('duplicate_title', sa.String(length=1024), nullable=False),
        sa.Column('duplicate_source', sa.String(length=128), nullable=False),
        sa.Column('duplicate_hash', sa.String(length=64), nullable=False),
        sa.Column('detection_stage', sa.String(length=64), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['canonical_article_id'], ['news_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    try:
        op.create_index('ix_article_duplicates_id', 'article_duplicates', ['id'], unique=False)
        op.create_index('ix_article_duplicates_canonical_article_id', 'article_duplicates', ['canonical_article_id'], unique=False)
        op.create_index('ix_article_duplicates_duplicate_hash', 'article_duplicates', ['duplicate_hash'], unique=False)
    except Exception:
        pass

    # 6. source_records
    op.create_table(
        'source_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=True),
        sa.Column('source_name', sa.String(length=128), nullable=False),
        sa.Column('source_record_id', sa.String(length=256), nullable=True),
        sa.Column('raw_payload', sa.JSON(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_status', sa.String(length=32), nullable=False, server_default='processed'),
        sa.ForeignKeyConstraint(['article_id'], ['news_records.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    try:
        op.create_index('ix_source_records_id', 'source_records', ['id'], unique=False)
        op.create_index('ix_source_records_article_id', 'source_records', ['article_id'], unique=False)
        op.create_index('ix_source_records_source_name', 'source_records', ['source_name'], unique=False)
    except Exception:
        pass

    # 7. article_companies
    op.create_table(
        'article_companies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=32), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('extraction_method', sa.String(length=64), nullable=False, server_default='regex_boundary'),
        sa.ForeignKeyConstraint(['article_id'], ['news_records.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    try:
        op.create_index('ix_article_companies_id', 'article_companies', ['id'], unique=False)
        op.create_index('ix_article_companies_article_id', 'article_companies', ['article_id'], unique=False)
        op.create_index('ix_article_companies_company_id', 'article_companies', ['company_id'], unique=False)
        op.create_index('ix_article_companies_symbol', 'article_companies', ['symbol'], unique=False)
    except Exception:
        pass

    # 8. article_categories
    op.create_table(
        'article_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('category_code', sa.String(length=64), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.ForeignKeyConstraint(['article_id'], ['news_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    try:
        op.create_index('ix_article_categories_id', 'article_categories', ['id'], unique=False)
        op.create_index('ix_article_categories_article_id', 'article_categories', ['article_id'], unique=False)
        op.create_index('ix_article_categories_category_code', 'article_categories', ['category_code'], unique=False)
    except Exception:
        pass

    # 9. collection_logs (collection_runs)
    op.create_table(
        'collection_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_name', sa.String(length=128), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='running'),
        sa.Column('items_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_inserted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_duplicate', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    try:
        op.create_index('ix_collection_logs_id', 'collection_logs', ['id'], unique=False)
        op.create_index('ix_collection_logs_source_name', 'collection_logs', ['source_name'], unique=False)
    except Exception:
        pass


def downgrade() -> None:
    op.drop_table('article_categories')
    op.drop_table('article_companies')
    op.drop_table('source_records')
    op.drop_table('article_duplicates')
    op.drop_table('collection_logs')
    op.drop_table('news_records')
    op.drop_table('categories')
    op.drop_table('companies')
    op.drop_table('sources')
