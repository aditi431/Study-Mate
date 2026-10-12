"""Initial StudyMate schema with user-scoped RLS."""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["id"], ["auth.users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profiles_email", "profiles", ["email"])

    op.create_table(
        "notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("topics_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("topics_count >= 0", name="ck_notes_topics_count_nonnegative"),
        sa.ForeignKeyConstraint(["user_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notes_user_id", "notes", ["user_id"])
    op.create_index("ix_notes_user_created", "notes", ["user_id", "created_at"])

    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False, server_default="text"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "chunk_index", name="ix_document_chunks_document_index"),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])

    op.create_table(
        "embeddings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chunk_id", sa.Uuid(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["chunk_id"], ["document_chunks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chunk_id"),
    )

    op.execute(
        """
        CREATE FUNCTION public.handle_new_studymate_user()
        RETURNS trigger
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public
        AS $$
        BEGIN
            INSERT INTO public.profiles (id, email, name)
            VALUES (
                NEW.id,
                NEW.email,
                NULLIF(NEW.raw_user_meta_data->>'full_name', '')
            )
            ON CONFLICT (id) DO UPDATE
            SET email = EXCLUDED.email,
                name = COALESCE(EXCLUDED.name, public.profiles.name);
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER on_auth_user_created_studymate
        AFTER INSERT OR UPDATE OF email, raw_user_meta_data ON auth.users
        FOR EACH ROW EXECUTE FUNCTION public.handle_new_studymate_user()
        """
    )
    op.execute(
        """
        INSERT INTO public.profiles (id, email, name)
        SELECT
            u.id,
            u.email,
            NULLIF(u.raw_user_meta_data->>'full_name', '')
        FROM auth.users AS u
        ON CONFLICT (id) DO UPDATE
        SET email = EXCLUDED.email,
            name = COALESCE(EXCLUDED.name, public.profiles.name)
        """
    )

    for table in ("profiles", "notes", "documents", "document_chunks", "embeddings"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")

    op.execute(
        """
        CREATE POLICY profiles_owner ON public.profiles
        FOR ALL TO authenticated
        USING (id = auth.uid())
        WITH CHECK (id = auth.uid());
        """
    )
    op.execute(
        """
        CREATE POLICY notes_owner ON public.notes
        FOR ALL TO authenticated
        USING (user_id = auth.uid())
        WITH CHECK (user_id = auth.uid());
        """
    )
    op.execute(
        """
        CREATE POLICY documents_owner ON public.documents
        FOR ALL TO authenticated
        USING (user_id = auth.uid())
        WITH CHECK (user_id = auth.uid());
        """
    )
    op.execute(
        """
        CREATE POLICY chunks_owner ON public.document_chunks
        FOR ALL TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM public.documents d
                WHERE d.id = document_id AND d.user_id = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM public.documents d
                WHERE d.id = document_id AND d.user_id = auth.uid()
            )
        );
        """
    )
    op.execute(
        """
        CREATE POLICY embeddings_owner ON public.embeddings
        FOR ALL TO authenticated
        USING (
            EXISTS (
                SELECT 1
                FROM public.document_chunks c
                JOIN public.documents d ON d.id = c.document_id
                WHERE c.id = chunk_id AND d.user_id = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1
                FROM public.document_chunks c
                JOIN public.documents d ON d.id = c.document_id
                WHERE c.id = chunk_id AND d.user_id = auth.uid()
            )
        );
        """
    )
    op.execute(
        """
        GRANT USAGE ON SCHEMA public TO authenticated;
        GRANT SELECT, INSERT, UPDATE, DELETE ON public.profiles, public.notes,
            public.documents, public.document_chunks, public.embeddings TO authenticated
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS on_auth_user_created_studymate ON auth.users")
    op.execute("DROP FUNCTION IF EXISTS public.handle_new_studymate_user()")
    for table in ("embeddings", "document_chunks", "documents", "notes", "profiles"):
        op.drop_table(table)
