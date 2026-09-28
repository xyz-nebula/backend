from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "case" ADD "second_role_preparations" TEXT NOT NULL DEFAULT '';
        ALTER TABLE "case" ADD "first_role_preparations" TEXT NOT NULL DEFAULT '';
        ALTER TABLE "case" DROP COLUMN "preparations";
        ALTER TABLE "chat" ADD "preparations" TEXT NOT NULL DEFAULT '';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "case" ADD "preparations" TEXT NOT NULL DEFAULT '';
        ALTER TABLE "case" DROP COLUMN "second_role_preparations";
        ALTER TABLE "case" DROP COLUMN "first_role_preparations";
        ALTER TABLE "chat" DROP COLUMN "preparations";"""


MODELS_STATE = (
    "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"
)
