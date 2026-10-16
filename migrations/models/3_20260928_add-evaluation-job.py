from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chat" ALTER COLUMN "status" TYPE VARCHAR(10);
        COMMENT ON COLUMN "chat"."status" IS 'VICTORY: victory\nDEFEAT: defeat\nONGOING: ongoing\nEVALUATING: evaluating\nEVALUATED: evaluated';
        CREATE TABLE IF NOT EXISTS "evaluation_job" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT now(),
    "status" VARCHAR(10) NOT NULL  DEFAULT 'pending',
    "result" JSONB,
    "error" TEXT,
    "chat_id" INT NOT NULL UNIQUE REFERENCES "chat" ("id") ON DELETE CASCADE
);
        COMMENT ON COLUMN "evaluation_job"."status" IS 'PENDING: pending\nPROCESSING: processing\nDONE: done\nFAILED: failed';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "evaluation_job";
        ALTER TABLE "chat" ALTER COLUMN "status" TYPE VARCHAR(7);
        COMMENT ON COLUMN "chat"."status" IS 'VICTORY: victory\nDEFEAT: defeat\nONGOING: ongoing';"""


MODELS_STATE = (
    "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"
    "yDj9D4+tHT2ner2H1l4U2qM8svb0H96dVRQ="
)
