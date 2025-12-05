CREATE TABLE "users" (
  "user_id" SERIAL PRIMARY KEY,
  "username" "VARCHAR(50)",
  "email" "VARCHAR(100)" UNIQUE,
  "password_hash" TEXT,
  "xp_total" INT,
  "level" INT,
  "streak_days" INT,
  "created_at" TIMESTAMP
);

CREATE TABLE "roadmap_nodes" (
  "node_id" SERIAL PRIMARY KEY,
  "day_number" INT,
  "title" "VARCHAR(100)",
  "description" TEXT,
  "xp_reward" INT,
  "recommended_games" JSON
);

CREATE TABLE "user_roadmap" (
  "user_roadmap_id" SERIAL PRIMARY KEY,
  "user_id" INT,
  "node_id" INT,
  "is_completed" BOOLEAN,
  "xp_earned" INT,
  "completion_date" TIMESTAMP
);

CREATE TABLE "game_types" (
  "game_type_id" SERIAL PRIMARY KEY,
  "name" "VARCHAR(50)",
  "description" TEXT
);

CREATE TABLE "games" (
  "game_id" SERIAL PRIMARY KEY,
  "game_type_id" INT,
  "difficulty" "VARCHAR(20)",
  "config_data" JSON
);

CREATE TABLE "sessions" (
  "session_id" SERIAL PRIMARY KEY,
  "user_roadmap_id" INT,
  "start_time" TIMESTAMP,
  "end_time" TIMESTAMP,
  "total_score" INT,
  "xp_gained" INT
);

CREATE TABLE "session_games" (
  "session_game_id" SERIAL PRIMARY KEY,
  "session_id" INT,
  "game_id" INT,
  "score" INT,
  "accuracy" FLOAT,
  "time_spent_sec" INT
);

CREATE TABLE "achievements" (
  "achievement_id" SERIAL PRIMARY KEY,
  "name" "VARCHAR(50)",
  "description" TEXT,
  "condition_type" "VARCHAR(50)",
  "threshold" INT
);

CREATE TABLE "achievement_user" (
  "user_id" INT,
  "achievement_id" INT,
  "date_earned" TIMESTAMP,
  PRIMARY KEY ("user_id", "achievement_id")
);

CREATE TABLE "stats" (
  "stat_id" SERIAL PRIMARY KEY,
  "user_id" INT,
  "memory_avg" FLOAT,
  "reflex_avg" FLOAT,
  "logic_avg" FLOAT,
  "focus_avg" FLOAT,
  "updated_at" TIMESTAMP
);

ALTER TABLE "user_roadmap" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");

ALTER TABLE "user_roadmap" ADD FOREIGN KEY ("node_id") REFERENCES "roadmap_nodes" ("node_id");

ALTER TABLE "games" ADD FOREIGN KEY ("game_type_id") REFERENCES "game_types" ("game_type_id");

ALTER TABLE "sessions" ADD FOREIGN KEY ("user_roadmap_id") REFERENCES "user_roadmap" ("user_roadmap_id");

ALTER TABLE "session_games" ADD FOREIGN KEY ("session_id") REFERENCES "sessions" ("session_id");

ALTER TABLE "session_games" ADD FOREIGN KEY ("game_id") REFERENCES "games" ("game_id");

ALTER TABLE "achievement_user" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");

ALTER TABLE "achievement_user" ADD FOREIGN KEY ("achievement_id") REFERENCES "achievements" ("achievement_id");

ALTER TABLE "stats" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");
