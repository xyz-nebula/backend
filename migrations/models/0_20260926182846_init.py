from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "case" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT NOT NULL,
    "category" VARCHAR(100) NOT NULL,
    "difficulty" VARCHAR(100) NOT NULL,
    "time_limit" INT NOT NULL,
    "preparations" TEXT NOT NULL,
    "system_prompt" TEXT NOT NULL,
    "goal" TEXT NOT NULL,
    "synopsis" TEXT NOT NULL,
    "first_role" TEXT NOT NULL,
    "second_role" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "feedback" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL,
    "session_uuid" UUID NOT NULL,
    "text" TEXT NOT NULL
);
COMMENT ON TABLE "feedback" IS 'Feedback:';
CREATE TABLE IF NOT EXISTS "judgement" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL,
    "session_uuid" UUID NOT NULL,
    "text" TEXT NOT NULL
);
COMMENT ON TABLE "judgement" IS 'Judgement:';
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL,
    "firstname" VARCHAR(100) NOT NULL,
    "lastname" VARCHAR(100) NOT NULL,
    "email" VARCHAR(254) NOT NULL UNIQUE,
    "password" VARCHAR(60) NOT NULL,
    "status" VARCHAR(18) NOT NULL,
    "role" VARCHAR(5) NOT NULL,
    "mfa_enabled" BOOL NOT NULL,
    "mfa_secret" VARCHAR(32)
);
COMMENT ON COLUMN "user"."status" IS 'PENDING_ACTIVATION: pending_activation\nACTIVE: active\nSUSPENDED: suspended';
COMMENT ON COLUMN "user"."role" IS 'USER: user\nADMIN: admin';
CREATE TABLE IF NOT EXISTS "chat" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "status" VARCHAR(7) NOT NULL,
    "case_id" INT NOT NULL REFERENCES "case" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "chat"."status" IS 'VICTORY: victory\nDEFEAT: defeat\nONGOING: ongoing';
CREATE TABLE IF NOT EXISTS "message" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL,
    "sequence" INT NOT NULL,
    "is_ai" BOOL NOT NULL,
    "text" TEXT NOT NULL,
    "chat_id" INT NOT NULL REFERENCES "chat" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "8ezL4JbKRLevwCv/2o2P3/C4cqkg=="
)
