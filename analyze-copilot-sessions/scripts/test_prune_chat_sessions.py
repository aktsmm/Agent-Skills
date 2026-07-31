import base64
import importlib.util
import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("prune_chat_sessions.py")
SPEC = importlib.util.spec_from_file_location("prune_chat_sessions", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PruneChatSessionsTests(unittest.TestCase):
    def create_storage(self, root: Path, workspace: Path) -> Path:
        storage = root / "workspaceStorage" / "storage-id"
        (storage / "chatSessions").mkdir(parents=True)
        uri = workspace.as_uri()
        (storage / "workspace.json").write_text(json.dumps({"workspace": uri}), encoding="utf-8")
        return storage

    def create_session(self, storage: Path, session_id: str, modified: datetime) -> Path:
        path = storage / "chatSessions" / f"{session_id}.jsonl"
        path.write_text('{"kind":0,"v":{}}\n', encoding="utf-8")
        timestamp = modified.timestamp()
        os.utime(path, (timestamp, timestamp))
        return path

    def create_auxiliary(self, storage: Path, root_name: str, session_id: str, modified: datetime) -> Path:
        root = storage / root_name
        if root_name == "chat-session-resources":
            root = storage / "GitHub.copilot-chat" / root_name
        path = root / session_id
        path.mkdir(parents=True)
        timestamp = modified.timestamp()
        os.utime(path, (timestamp, timestamp))
        return path

    def local_resource(self, session_id: str) -> str:
        encoded = base64.urlsafe_b64encode(session_id.encode("utf-8")).decode("ascii").rstrip("=")
        return f"vscode-chat-session://local/{encoded}"

    def create_state_database(
        self,
        storage: Path,
        index_entries: dict,
        states: list[dict],
    ) -> Path:
        database = storage / "state.vscdb"
        connection = sqlite3.connect(database)
        try:
            connection.execute("CREATE TABLE ItemTable (key TEXT PRIMARY KEY, value TEXT)")
            connection.executemany(
                "INSERT INTO ItemTable (key, value) VALUES (?, ?)",
                (
                    (MODULE.INDEX_KEY, json.dumps({"version": 1, "entries": index_entries})),
                    (MODULE.STATE_KEY, json.dumps(states)),
                ),
            )
            connection.commit()
        finally:
            connection.close()
        return database

    def create_chronicle_database(self, storage: Path, session_id: str) -> Path:
        database = MODULE.chronicle_database(storage)
        database.parent.mkdir(parents=True)
        connection = sqlite3.connect(database)
        try:
            connection.executescript(
                """
                CREATE TABLE sessions (id TEXT PRIMARY KEY);
                CREATE TABLE turns (session_id TEXT);
                CREATE TABLE checkpoints (session_id TEXT);
                CREATE TABLE session_files (session_id TEXT);
                CREATE TABLE session_refs (session_id TEXT);
                CREATE TABLE search_index (session_id TEXT);
                """
            )
            for table in ("turns", "checkpoints", "session_files", "session_refs", "search_index"):
                connection.execute(f"INSERT INTO {table} (session_id) VALUES (?)", (session_id,))
            connection.execute("INSERT INTO sessions (id) VALUES (?)", (session_id,))
            connection.commit()
        finally:
            connection.close()
        return database

    def test_plan_retains_latest_and_explicitly_protected_sessions(self):
        now = datetime(2026, 7, 31, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace = root / "repo"
            workspace.mkdir()
            storage = self.create_storage(root, workspace)
            old_id = "11111111-1111-4111-8111-111111111111"
            protected_id = "22222222-2222-4222-8222-222222222222"
            recent_id = "33333333-3333-4333-8333-333333333333"
            self.create_session(storage, old_id, now - timedelta(hours=72))
            self.create_session(storage, protected_id, now - timedelta(hours=60))
            self.create_session(storage, recent_id, now - timedelta(hours=1))

            plan = MODULE.build_plan(storage, 36, {protected_id}, keep_latest=1, now=now)

            self.assertEqual([path.stem for path in plan["session_files"]], [old_id])
            self.assertEqual(plan["protected_ids"], {protected_id, recent_id})
            self.assertTrue((storage / "chatSessions" / f"{old_id}.jsonl").exists())

    def test_plan_automatically_protects_pinned_session(self):
        now = datetime(2026, 7, 31, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace = root / "repo"
            workspace.mkdir()
            storage = self.create_storage(root, workspace)
            pinned_id = "11111111-1111-4111-8111-111111111111"
            self.create_session(storage, pinned_id, now - timedelta(hours=72))
            self.create_state_database(
                storage,
                {pinned_id: {"lastMessageDate": (now - timedelta(hours=72)).timestamp() * 1000}},
                [{"resource": self.local_resource(pinned_id), "pinned": True}],
            )

            plan = MODULE.build_plan(storage, 36, set(), keep_latest=0, now=now)

            self.assertEqual(plan["session_files"], [])
            self.assertEqual(plan["pinned_ids"], {pinned_id})
            self.assertIn(pinned_id, plan["protected_ids"])

    def test_apply_deletes_exact_session_auxiliary_and_old_uuid_orphan_only(self):
        now = datetime(2026, 7, 31, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace = root / "repo"
            workspace.mkdir()
            storage = self.create_storage(root, workspace)
            old_id = "11111111-1111-4111-8111-111111111111"
            recent_id = "22222222-2222-4222-8222-222222222222"
            orphan_id = "33333333-3333-4333-8333-333333333333"
            old_session = self.create_session(storage, old_id, now - timedelta(hours=72))
            recent_session = self.create_session(storage, recent_id, now - timedelta(hours=1))
            old_editing = self.create_auxiliary(storage, "chatEditingSessions", old_id, now)
            orphan_resource = self.create_auxiliary(storage, "chat-session-resources", orphan_id, now - timedelta(hours=72))
            non_uuid = self.create_auxiliary(storage, "chatEditingSessions", "not-a-session-id", now - timedelta(hours=72))
            state_database = self.create_state_database(
                storage,
                {
                    old_id: {"lastMessageDate": (now - timedelta(hours=72)).timestamp() * 1000},
                    orphan_id: {"lastMessageDate": (now - timedelta(hours=72)).timestamp() * 1000},
                    recent_id: {"lastMessageDate": (now - timedelta(hours=1)).timestamp() * 1000},
                },
                [
                    {"resource": self.local_resource(old_id), "read": 1},
                    {"resource": self.local_resource(orphan_id), "read": 1},
                    {"resource": self.local_resource(recent_id), "read": 2},
                ],
            )
            chronicle_database = self.create_chronicle_database(storage, old_id)

            plan = MODULE.build_plan(storage, 36, set(), keep_latest=1, now=now)
            deleted = MODULE.apply_plan(plan)
            result = MODULE.report(plan, "apply", deleted)

            self.assertEqual(deleted["session_files"], 1)
            self.assertEqual(deleted["auxiliary_dirs"], 2)
            self.assertEqual(deleted["index_entries"], 2)
            self.assertEqual(deleted["state_entries"], 2)
            self.assertEqual(deleted["chronicle_rows"], 6)
            self.assertEqual(result["workspace_storage_id"], "storage-id")
            self.assertTrue(result["reload_window_required"])
            self.assertEqual(result["remaining_candidate_session_count"], 0)
            self.assertEqual(result["remaining_candidate_auxiliary_count"], 0)
            self.assertFalse(old_session.exists())
            self.assertFalse(old_editing.exists())
            self.assertFalse(orphan_resource.exists())
            self.assertTrue(recent_session.exists())
            self.assertTrue(non_uuid.exists())
            state_connection = sqlite3.connect(state_database)
            try:
                rows = dict(state_connection.execute("SELECT key, value FROM ItemTable"))
            finally:
                state_connection.close()
            self.assertNotIn(old_id, json.loads(rows[MODULE.INDEX_KEY])["entries"])
            self.assertNotIn(orphan_id, json.loads(rows[MODULE.INDEX_KEY])["entries"])
            self.assertIn(recent_id, json.loads(rows[MODULE.INDEX_KEY])["entries"])
            self.assertEqual(
                [state["resource"] for state in json.loads(rows[MODULE.STATE_KEY])],
                [self.local_resource(recent_id)],
            )
            chronicle_connection = sqlite3.connect(chronicle_database)
            try:
                remaining = chronicle_connection.execute(
                    "SELECT COUNT(*) FROM sessions WHERE id = ?", (old_id,)
                ).fetchone()[0]
            finally:
                chronicle_connection.close()
            self.assertEqual(remaining, 0)

    def test_resolves_workspace_root_for_code_workspace_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace = root / "repo"
            workspace.mkdir()
            workspace_file = workspace / "repo.code-workspace"
            workspace_file.write_text("{}", encoding="utf-8")
            storage = self.create_storage(root, workspace_file)

            resolved = MODULE.resolve_workspace_storage(workspace, [root / "workspaceStorage"])

            self.assertEqual(resolved, storage)

    def test_resolves_most_recent_storage_when_folder_and_workspace_match(self):
        now = datetime(2026, 7, 31, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace = root / "repo"
            workspace.mkdir()
            workspace_file = workspace / "repo.code-workspace"
            workspace_file.write_text("{}", encoding="utf-8")
            old_storage = self.create_storage(root / "old", workspace)
            active_storage = self.create_storage(root / "active", workspace_file)
            self.create_session(
                old_storage,
                "11111111-1111-4111-8111-111111111111",
                now - timedelta(days=10),
            )
            self.create_session(
                active_storage,
                "22222222-2222-4222-8222-222222222222",
                now - timedelta(minutes=1),
            )

            resolved = MODULE.resolve_workspace_storage(
                workspace,
                [root / "old" / "workspaceStorage", root / "active" / "workspaceStorage"],
            )

            self.assertEqual(resolved, active_storage)


if __name__ == "__main__":
    unittest.main()