from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chat" ADD "selected_role" SMALLINT NOT NULL;
        COMMENT ON COLUMN chat."selected_role" IS 'FIRST: 0\nSECOND: 1';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chat" DROP COLUMN "selected_role";"""


MODELS_STATE = (
    "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"
    "8BS52maQ=="
)
