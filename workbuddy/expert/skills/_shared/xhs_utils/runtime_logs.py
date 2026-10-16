"""Bound XHS runtime diagnostics without changing authentication state."""
from __future__ import annotations

from datetime import date, timedelta
import fcntl
import os
from pathlib import Path
import signal
import subprocess
import sys


LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUPS = 3
DAILY_RETENTION_DAYS = 30


def prune_daily_markers(directory: Path, today: date) -> None:
    cutoff = today - timedelta(days=DAILY_RETENTION_DAYS - 1)
    for path in directory.glob('*.json'):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            day = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if path.name == f'{day.isoformat()}.json' and day < cutoff:
            path.unlink(missing_ok=True)


def _backup(path: Path, number: int) -> Path:
    return path.with_name(f'{path.name}.{number}')


def _trim_existing(path: Path) -> None:
    if not path.exists() or path.stat().st_size <= LOG_MAX_BYTES:
        return
    with path.open('r+b') as stream:
        stream.seek(-LOG_MAX_BYTES, os.SEEK_END)
        tail = stream.read(LOG_MAX_BYTES)
        # Discard the first partial line when preserving an older oversized log.
        newline = tail.find(b'\n')
        if newline >= 0:
            tail = tail[newline + 1:]
        stream.seek(0)
        stream.write(tail)
        stream.truncate()


def append_log(path: Path, data: bytes) -> None:
    """Append under a process lock; keep the active file and three bounded backups."""
    if not data:
        return
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock_fd = os.open(path.with_name(f'{path.name}.lock'), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        for candidate in [path, *(_backup(path, n) for n in range(1, LOG_BACKUPS + 1))]:
            _trim_existing(candidate)
        data = data[-LOG_MAX_BYTES:]
        size = path.stat().st_size if path.exists() else 0
        if size and size + len(data) > LOG_MAX_BYTES:
            for number in range(LOG_BACKUPS, 0, -1):
                source = path if number == 1 else _backup(path, number - 1)
                if source.exists():
                    os.replace(source, _backup(path, number))
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, 'ab') as stream:
            stream.write(data)
    finally:
        os.close(lock_fd)


def logged_worker_command(path: Path, command: list[str]) -> list[str]:
    return [sys.executable, str(Path(__file__).resolve()), str(path), '--', *command]


def run_logged_worker(path: Path, command: list[str]) -> int:
    """Drain a login worker's stdout/stderr continuously into bounded private logs."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    child = subprocess.Popen(
        command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, env={**os.environ, 'PYTHONUNBUFFERED': '1'},
    )
    assert child.stdout is not None
    def forward_signal(signum, _frame):
        try:
            child.send_signal(signum)
        except ProcessLookupError:
            pass

    handlers = {signum: signal.signal(signum, forward_signal)
                for signum in (signal.SIGTERM, signal.SIGINT)}
    try:
        with child.stdout:
            while data := child.stdout.read1(64 * 1024):
                try:
                    append_log(path, data)
                except OSError:
                    # Keep draining: a diagnostic I/O failure must not block login.
                    pass
    finally:
        code = child.wait()
        for signum, handler in handlers.items():
            signal.signal(signum, handler)
    return code if code >= 0 else 128 - code


if __name__ == '__main__':
    if len(sys.argv) < 4 or sys.argv[2] != '--':
        raise SystemExit('Usage: runtime_logs.py <log-path> -- <worker> [args...]')
    raise SystemExit(run_logged_worker(Path(sys.argv[1]), sys.argv[3:]))
