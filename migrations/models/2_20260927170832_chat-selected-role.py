from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chat" ADD "selected_role" SMALLINT NOT NULL DEFAULT 0;
        COMMENT ON COLUMN chat."selected_role" IS 'FIRST: 0\nSECOND: 1';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chat" DROP COLUMN "selected_role";"""


MODELS_STATE = (
    "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"
    "L3/wOpRaTe"
)
