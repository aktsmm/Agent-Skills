PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY,
  started_at TEXT NOT NULL,
  completed_at TEXT,
  mode TEXT NOT NULL,
  target_set TEXT,
  status TEXT NOT NULL DEFAULT 'running',
  summary TEXT
);

CREATE TABLE IF NOT EXISTS items (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  domain TEXT,
  audience TEXT,
  status TEXT NOT NULL DEFAULT 'new',
  priority TEXT NOT NULL DEFAULT 'medium',
  source TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  item_id TEXT REFERENCES items(id) ON DELETE SET NULL,
  parent_task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  kind TEXT NOT NULL,
  assignee TEXT,
  priority TEXT NOT NULL DEFAULT 'medium',
  status TEXT NOT NULL DEFAULT 'pending',
  instruction TEXT NOT NULL,
  artifact_path TEXT,
  finding_ids_json TEXT,
  input_hash TEXT,
  acceptance_checks_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS claims (
  task_id TEXT PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
  claimed_by TEXT NOT NULL,
  run_id TEXT REFERENCES runs(id) ON DELETE SET NULL,
  claimed_at TEXT NOT NULL,
  heartbeat_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  attempt_count INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS reviews (
  id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(id) ON DELETE SET NULL,
  item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  pass_index INTEGER NOT NULL,
  persona TEXT NOT NULL,
  verdict TEXT NOT NULL,
  priority TEXT,
  finding TEXT NOT NULL,
  action TEXT,
  created_at TEXT NOT NULL,
  UNIQUE (item_id, pass_index, persona)
);

CREATE TABLE IF NOT EXISTS critic_log (
  id TEXT PRIMARY KEY,
  task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  parent_task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  workflow_round INTEGER,
  input_hash TEXT,
  output_hash TEXT,
  finding_ids_json TEXT,
  finding_resolution_json TEXT,
  validation_results_json TEXT,
  repair_task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  layer TEXT,
  role TEXT,
  producer_model TEXT,
  critic_model TEXT,
  producer_family TEXT,
  critic_family TEXT,
  family_resolver TEXT,
  receipt_source TEXT,
  receipt_ref TEXT,
  receipt_hash TEXT,
  independence_verdict TEXT,
  verdict TEXT,
  next_state TEXT,
  reason TEXT,
  evidence_ref TEXT,
  created_at TEXT NOT NULL,
  CHECK (independence_verdict IS NULL OR independence_verdict IN ('different-family', 'same-family', 'unresolved', 'degraded', 'blocked-independence')),
  CHECK (next_state IS NULL OR next_state IN ('repair-started', 'repair-start-failed', 'repair-planned', 'validation-failed', 'replan', 'blocked-independence', 'parked-independence', 'overridden-independence', 'deferred-exhausted', 'complete', 'rejected'))
);

CREATE TABLE IF NOT EXISTS repair_attempts (
  id TEXT PRIMARY KEY,
  parent_task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  repair_task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  workflow_round INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('reserved', 'validation-failed', 'validation-passed', 'repair-start-failed', 'blocked-independence', 'closed')),
  input_hash TEXT,
  output_hash TEXT,
  critic_log_id TEXT REFERENCES critic_log(id) ON DELETE SET NULL,
  reserved_at TEXT NOT NULL,
  finalized_at TEXT,
  evidence_ref TEXT,
  UNIQUE (parent_task_id, workflow_round)
);

CREATE TABLE IF NOT EXISTS artifacts (
  id TEXT PRIMARY KEY,
  task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  item_id TEXT REFERENCES items(id) ON DELETE SET NULL,
  path TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL,
  summary TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outcomes (
  id TEXT PRIMARY KEY,
  item_id TEXT REFERENCES items(id) ON DELETE CASCADE,
  metric TEXT NOT NULL,
  value TEXT NOT NULL,
  provenance TEXT NOT NULL CHECK (provenance IN ('observed', 'estimated', 'assumed')),
  source TEXT,
  recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  actor TEXT,
  event TEXT NOT NULL,
  details TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON tasks(status, priority);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_task_id, status);
CREATE INDEX IF NOT EXISTS idx_reviews_item_pass ON reviews(item_id, pass_index);
CREATE INDEX IF NOT EXISTS idx_critic_log_parent_round ON critic_log(parent_task_id, workflow_round);
CREATE INDEX IF NOT EXISTS idx_repair_attempts_parent_round ON repair_attempts(parent_task_id, workflow_round);
CREATE INDEX IF NOT EXISTS idx_outcomes_item_metric ON outcomes(item_id, metric);