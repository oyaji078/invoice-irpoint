import os
import time
from contextlib import contextmanager

@contextmanager
def file_lock(lock_path: str, timeout: float = 5.0):
    """Simple cross-platform file lock using a sidecar .lock file."""
    lock_dir = os.path.dirname(lock_path)
    if lock_dir:
        os.makedirs(lock_dir, exist_ok=True)

    if os.name == "nt":
        import msvcrt  # type: ignore

        fh = open(lock_path, "a+")
        start = time.time()
        while True:
            try:
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                if time.time() - start > timeout:
                    fh.close()
                    raise TimeoutError(f"Timeout acquiring lock: {lock_path}")
                time.sleep(0.05)
        try:
            yield
        finally:
            try:
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            finally:
                fh.close()
    else:
        import fcntl  # type: ignore

        fh = open(lock_path, "a+")
        start = time.time()
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.time() - start > timeout:
                    fh.close()
                    raise TimeoutError(f"Timeout acquiring lock: {lock_path}")
                time.sleep(0.05)
        try:
            yield
        finally:
            try:
                fcntl.flock(fh, fcntl.LOCK_UN)
            finally:
                fh.close()
