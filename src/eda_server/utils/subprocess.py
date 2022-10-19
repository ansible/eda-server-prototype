import asyncio
import subprocess
from typing import Any, Optional

__all__ = (
    "TimeoutExpired",
    "CalledProcessError",
    "CompletedProcess",
)


TimeoutExpired = subprocess.TimeoutExpired

CalledProcessError = subprocess.CalledProcessError

CompletedProcess = subprocess.CompletedProcess


async def run(
    *cmd: str,
    timeout: Optional[int] = None,
    check: bool = False,
    encoding: Optional[str] = None,
    **kwargs: Any,
):
    """Asynchronous analogue of the ``subprocess.run`` call.

    :param cmd: The arguments used to launch the process.
    :param timeout: If the timeout expires, the child process will be killed.
    :param check: If ``True`` and the process exists with non-zero exit code,
        a ``CalledProcessError`` exception will be raised.
    :param encoding: If set, stdout and stderr are decoded with
        specified encoding.
    :param kwargs: Passed to the ``asyncio.create_subprocess_exec``.
    :return:
    """
    process = await asyncio.create_subprocess_exec(*cmd, **kwargs)
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        # NOTE(cutwater): This is a workaround for issue in CPython
        #  https://github.com/python/cpython/issues/88050
        #  which is expected to be fixed in 3.11
        process._transport.close()
        raise subprocess.TimeoutExpired(cmd, timeout, None, None)

    if encoding is not None:
        if stdout is not None:
            stdout = stdout.decode(encoding)
        if stderr is not None:
            stderr = stderr.decode(encoding)

    if check and process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode, cmd, stdout, stderr
        )

    return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
