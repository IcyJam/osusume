CREATE TYPE "media_type" AS ENUM (
    'TV',
    'MOVIE',
    'OVA',
    'ONA',
    'SPECIAL',
    'MANGA',
    'NOVEL',
    'ARTBOOK',
    'OTHER'
);

CREATE TYPE "status" AS ENUM (
    'UPCOMING',
    'ONGOING',
    'FINISHED',
    'SUSPENDED',
    'CANCELLED',
    'UNKNOWN'
);

CREATE TABLE "media"
(
    "media_id"     serial PRIMARY KEY,
    "type"         media_type NOT NULL,
    "title"        text       NOT NULL,
    "summary"      text,
    "start_date"   date,
    "end_date"     date,
    "external_url" text,
    "image_url"    text,
    "status"       status,
    "created_at"   timestamp default CURRENT_TIMESTAMP,
    "updated_at"   timestamp default CURRENT_TIMESTAMP,
    UNIQUE ("title", "type", "external_url")
);

CREATE TABLE "content_descriptors"
(
    "content_descriptor_id" serial PRIMARY KEY,
    "content_descriptor"    text NOT NULL UNIQUE
);

CREATE TABLE "media_content_descriptors"
(
    "media_id"              int,
    "content_descriptor_id" int,
    PRIMARY KEY ("media_id", "content_descriptor_id"),
    FOREIGN KEY ("media_id") REFERENCES "media" ("media_id") ON DELETE CASCADE,
    FOREIGN KEY ("content_descriptor_id") REFERENCES "content_descriptors" ("content_descriptor_id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ON "media" ("media_id");
CREATE INDEX IF NOT EXISTS ON media(title);

CREATE INDEX IF NOT EXISTS ON content_descriptors(content_descriptor);

CREATE INDEX IF NOT EXISTS ON media_content_descriptors(content_descriptor_id);
CREATE INDEX IF NOT EXISTS ON media_content_descriptors(media_id);

ALTER TABLE "media_content_descriptors"
    ADD FOREIGN KEY ("media_id") REFERENCES "media" ("media_id");

ALTER TABLE "media_content_descriptors"
    ADD FOREIGN KEY ("content_descriptor_id") REFERENCES "content_descriptors" ("content_descriptor_id");
