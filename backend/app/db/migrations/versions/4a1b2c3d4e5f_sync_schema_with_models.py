"""sync schema with current models

Drops old tables, alters existing tables, creates new tables.

Revision ID: 4a1b2c3d4e5f
Revises: 3b4be866a3a9
Create Date: 2026-07-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '4a1b2c3d4e5f'
down_revision: Union[str, None] = '3b4be866a3a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. 删除旧的外键 ──────────────────────────────────────
    op.drop_constraint('contracts_source_file_id_fkey', 'contracts', type_='foreignkey')
    op.drop_constraint('acceptance_reports_contract_id_fkey', 'acceptance_reports', type_='foreignkey')
    op.drop_constraint('acceptance_reports_pair_report_id_fkey', 'acceptance_reports', type_='foreignkey')

    # ── 2. 删除不再有 Model 的旧表（按 FK 依赖逆序） ─────
    op.drop_table('line_item_comparisons')
    op.drop_table('comparisons')
    op.drop_table('risk_records')
    op.drop_table('line_items')
    op.drop_table('source_files')
    op.drop_table('audit_log')

    # ── 3. 变更 admins ──────────────────────────────────────
    op.add_column('admins', sa.Column('role', sa.String(length=20), nullable=False, server_default='viewer'))
    op.add_column('admins', sa.Column('city', sa.String(length=20), nullable=True))
    op.add_column('admins', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('admins', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))

    # ── 4. 变更 projects ────────────────────────────────────
    op.add_column('projects', sa.Column('has_front_contract', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('projects', sa.Column('has_back_contract', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('projects', sa.Column('has_front_acceptance', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('projects', sa.Column('has_back_acceptance', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('projects', sa.Column('llm_analyzed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('projects', sa.Column('project_risk', sa.String(length=10), nullable=True))
    op.add_column('projects', sa.Column('audit_status', sa.String(length=20), nullable=False, server_default='待审查'))
    op.add_column('projects', sa.Column('audited_by', sa.String(length=50), nullable=True))
    op.add_column('projects', sa.Column('audited_at', sa.DateTime(timezone=True), nullable=True))

    op.drop_column('projects', 'status')
    op.drop_column('projects', 'risk_level')

    op.create_check_constraint(
        'ck_projects_project_risk',
        'projects',
        "project_risk IN ('低风险', '高风险')",
    )
    op.create_check_constraint(
        'ck_projects_audit_status',
        'projects',
        "audit_status IN ('待审查', '已完成')",
    )

    # ── 5. 变更 contracts ───────────────────────────────────
    op.drop_column('contracts', 'source_file_id')
    op.drop_column('contracts', 'source_file_hash')
    op.drop_column('contracts', 'ocr_raw_text')
    op.drop_column('contracts', 'ocr_engine')
    op.drop_column('contracts', 'llm_model')

    op.drop_index('idx_contracts_type', table_name='contracts')

    op.create_unique_constraint('uq_contracts_no_type', 'contracts', ['contract_no', 'contract_type'])
    op.create_check_constraint(
        'ck_contracts_type',
        'contracts',
        "contract_type IN ('前项', '后项')",
    )

    # ── 6. 变更 acceptance_reports ──────────────────────────
    op.drop_column('acceptance_reports', 'contract_id')
    op.drop_column('acceptance_reports', 'pair_report_id')
    op.drop_column('acceptance_reports', 'comparison_result')
    op.drop_column('acceptance_reports', 'content_diff_detail')
    op.drop_column('acceptance_reports', 'date_logic')
    op.drop_column('acceptance_reports', 'source_file_id')
    op.drop_column('acceptance_reports', 'source_file_hash')
    op.drop_column('acceptance_reports', 'ocr_raw_text')
    op.drop_column('acceptance_reports', 'ocr_engine')
    op.drop_column('acceptance_reports', 'llm_model')

    op.create_unique_constraint('uq_acceptance_no_type', 'acceptance_reports', ['contract_no', 'acceptance_type'])
    op.create_check_constraint(
        'ck_acceptance_type',
        'acceptance_reports',
        "acceptance_type IN ('前项', '后项')",
    )
    op.create_check_constraint(
        'ck_acceptance_result',
        'acceptance_reports',
        "acceptance_result IN ('通过', '不通过', '附条件通过')",
    )

    # ── 7. 创建新表 ─────────────────────────────────────────
    op.create_table('contract_analysis',
        sa.Column('contract_no', sa.String(length=100), nullable=False),
        sa.Column('rate', sa.Numeric(precision=6, scale=4), nullable=True),
        sa.Column('rate_level', sa.String(length=20), nullable=True),
        sa.Column('similarity', sa.String(length=20), nullable=True),
        sa.Column('analysis', sa.Text(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_by', sa.String(length=50), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['contract_no'], ['projects.contract_no'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contract_no', name='uq_contract_analysis_no'),
    )
    op.create_index('idx_contract_analysis_no', 'contract_analysis', ['contract_no'])
    op.create_check_constraint('ck_ca_rate_level', 'contract_analysis', "rate_level IN ('正常', '低毛利', '利润倒挂')")
    op.create_check_constraint('ck_ca_similarity', 'contract_analysis', "similarity IN ('完全一致', '有一致性风险', '完全不一致')")

    op.create_table('acceptance_report_analysis',
        sa.Column('contract_no', sa.String(length=100), nullable=False),
        sa.Column('similarity', sa.String(length=20), nullable=True),
        sa.Column('analysis', sa.Text(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_by', sa.String(length=50), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['contract_no'], ['projects.contract_no'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contract_no', name='uq_acceptance_analysis_no'),
    )
    op.create_index('idx_acceptance_analysis_no', 'acceptance_report_analysis', ['contract_no'])
    op.create_check_constraint('ck_ara_similarity', 'acceptance_report_analysis', "similarity IN ('完全一致', '有一致性风险', '完全不一致')")


def downgrade() -> None:
    """Downgrade 需要重建所有旧表和旧列，此处省略（过于复杂）。"""
    pass
