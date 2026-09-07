"""Full-Facts grounding — docker-compose services + Makefile targets.

Parity with faf-cli 7.10's src/interrogate/{compose,build-files}.ts.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from interrogate import (  # noqa: E402
    interrogate_build_files,
    interrogate_compose,
    interrogate_repo,
)


class TestCompose:
    def test_no_compose_file_is_empty(self, tmp_path):
        assert interrogate_compose(str(tmp_path)) == {}

    def test_maps_service_images_to_slots(self, tmp_path):
        (tmp_path / "docker-compose.yml").write_text(
            "services:\n"
            "  db:\n    image: postgres:16-alpine\n"
            "  kv:\n    image: redis:7\n"
            "  es:\n    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0\n"
            "  files:\n    image: minio/minio:latest\n"
        )
        s = interrogate_compose(str(tmp_path))
        assert s["database"] == "PostgreSQL"
        assert s["cache"] == "Redis"
        assert s["search"] == "Elasticsearch"
        assert s["storage"] == "MinIO (S3-compatible)"
        assert s["hosting"] == "Docker Compose"

    def test_registry_host_and_tag_stripped(self, tmp_path):
        (tmp_path / "compose.yaml").write_text(
            "services:\n  db:\n    image: ghcr.io/acme/postgres:15\n"
        )
        assert interrogate_compose(str(tmp_path))["database"] == "PostgreSQL"

    def test_multiple_dbs_joined(self, tmp_path):
        (tmp_path / "docker-compose.yml").write_text(
            "services:\n"
            "  pg:\n    image: postgres:16\n"
            "  ch:\n    image: clickhouse/clickhouse-server:latest\n"
        )
        db = interrogate_compose(str(tmp_path))["database"]
        assert "PostgreSQL" in db and "ClickHouse" in db

    def test_compose_present_no_infra_still_reports_hosting(self, tmp_path):
        (tmp_path / "docker-compose.yml").write_text(
            "services:\n  web:\n    build: .\n"
        )
        assert interrogate_compose(str(tmp_path)) == {"hosting": "Docker Compose"}

    def test_finds_compose_one_dir_deep(self, tmp_path):
        (tmp_path / "deploy").mkdir()
        (tmp_path / "deploy" / "docker-compose.yml").write_text(
            "services:\n  db:\n    image: mysql:8\n"
        )
        assert interrogate_compose(str(tmp_path))["database"] == "MySQL"


class TestBuildFiles:
    def test_no_makefile_is_empty(self, tmp_path):
        assert interrogate_build_files(str(tmp_path)) == {}

    def test_makefile_targets_to_commands(self, tmp_path):
        (tmp_path / "Makefile").write_text(
            ".PHONY: test build lint\n"
            "test:\n\tpytest -q\n"
            "build:\n\tpython -m build\n"
            "lint:\n\truff check .\n"
        )
        c = interrogate_build_files(str(tmp_path))
        assert c == {"test": "make test", "build": "make build", "lint": "make lint"}

    def test_check_all_maps_to_lint(self, tmp_path):
        (tmp_path / "Makefile").write_text("check-all:\n\truff && mypy\ntest:\n\tpytest\n")
        c = interrogate_build_files(str(tmp_path))
        assert c["lint"] == "make check-all"

    def test_justfile_supported(self, tmp_path):
        (tmp_path / "justfile").write_text("test:\n    cargo test\nbuild:\n    cargo build\n")
        c = interrogate_build_files(str(tmp_path))
        assert c == {"test": "just test", "build": "just build"}

    def test_root_makefile_wins_over_nested(self, tmp_path):
        (tmp_path / "Makefile").write_text("test:\n\tpytest\nbuild:\n\tbuild\nlint:\n\tlint\n")
        (tmp_path / "backend").mkdir()
        (tmp_path / "backend" / "Makefile").write_text("test:\n\tgo test ./...\n")
        c = interrogate_build_files(str(tmp_path))
        assert c["test"] == "make test"

    def test_nested_makefile_used_when_no_root(self, tmp_path):
        (tmp_path / "api").mkdir()
        (tmp_path / "api" / "pyproject.toml").write_text("[project]\nname='x'\n")
        (tmp_path / "api" / "Makefile").write_text("test:\n\tpytest\n")
        c = interrogate_build_files(str(tmp_path))
        assert c["test"] == "cd api && make test"

    def test_variable_assignments_not_treated_as_targets(self, tmp_path):
        (tmp_path / "Makefile").write_text("CC := gcc\nPYTHON ?= python3\ntest:\n\tpytest\n")
        c = interrogate_build_files(str(tmp_path))
        assert c == {"test": "make test"}


class TestInterrogateRepo:
    def test_merges_stack_and_commands(self, tmp_path):
        (tmp_path / "docker-compose.yml").write_text(
            "services:\n  db:\n    image: postgres:16\n"
        )
        (tmp_path / "Makefile").write_text("test:\n\tpytest\n")
        r = interrogate_repo(str(tmp_path))
        assert r["stack"]["database"] == "PostgreSQL"
        assert r["commands"]["test"] == "make test"

    def test_empty_repo(self, tmp_path):
        assert interrogate_repo(str(tmp_path)) == {"stack": {}, "commands": {}}
