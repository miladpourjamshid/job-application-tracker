import os
import shutil
import subprocess


def _run_alembic(*arguments: str, database_url: str) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("alembic")
    assert executable is not None, "Alembic CLI is not installed"
    return subprocess.run(
        [executable, *arguments],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "DATABASE_URL": database_url},
    )


def test_migrations_upgrade_and_downgrade_cleanly(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'migration.db'}"

    upgrade = _run_alembic("upgrade", "head", database_url=database_url)
    assert upgrade.returncode == 0, upgrade.stderr

    downgrade = _run_alembic("downgrade", "base", database_url=database_url)
    assert downgrade.returncode == 0, downgrade.stderr

    re_upgrade = _run_alembic("upgrade", "head", database_url=database_url)
    assert re_upgrade.returncode == 0, re_upgrade.stderr
