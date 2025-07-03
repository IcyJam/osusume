CREATE TYPE "media_type" AS ENUM (
  'anime',
  'manga'
);

CREATE TYPE "status" AS ENUM (
  'not_yet_released',
  'releasing',
  'finished',
  'suspended',
  'cancelled'
);

CREATE TABLE "media" (
  "media_id" serial PRIMARY KEY,
  "type" media_type NOT NULL,
  "title" text NOT NULL,
  "summary" text,
  "start_date" date,
  "end_date" date,
  "external_url" text,
  "image_url" text,
  "status" status,
  "created_at" timestamp default CURRENT_TIMESTAMP,
  "updated_at" timestamp default CURRENT_TIMESTAMP
);

CREATE TABLE "genres" (
  "genre_id" serial PRIMARY KEY,
  "genre_name" text NOT NULL UNIQUE
);

CREATE TABLE "content_descriptors" (
  "content_descriptor_id" serial PRIMARY KEY,
  "content_descriptor" text NOT NULL UNIQUE
);

CREATE TABLE "media_genres" (
  "media_id" int ON DELETE CASCADE,
  "genre_id" int ON DELETE CASCADE,
  PRIMARY KEY ("media_id", "genre_id")
);

CREATE TABLE "media_content_descriptors" (
  "media_id" int ON DELETE CASCADE,
  "content_descriptor_id" int ON DELETE CASCADE,
  PRIMARY KEY ("media_id", "content_descriptor_id")
);

CREATE INDEX ON "media" ("media_id");

ALTER TABLE "media_genres" ADD FOREIGN KEY ("media_id") REFERENCES "media" ("media_id");

ALTER TABLE "media_genres" ADD FOREIGN KEY ("genre_id") REFERENCES "genres" ("genre_id");

ALTER TABLE "media_content_descriptors" ADD FOREIGN KEY ("media_id") REFERENCES "media" ("media_id");

ALTER TABLE "media_content_descriptors" ADD FOREIGN KEY ("content_descriptor_id") REFERENCES "content_descriptors" ("content_descriptor_id");
