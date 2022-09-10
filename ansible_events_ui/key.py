import asyncio
import logging
import os
import shutil
import tempfile

ssh_keygen = shutil.which("ssh-keygen")
logger = logging.getLogger()


async def generate_ssh_keys():

    with tempfile.TemporaryDirectory as local_working_directory:
        cmd = ["-f", "key", "-P", "", "-C", "ansible-events-ui"]
        logger.debug(ssh_keygen)
        logger.debug(cmd)

        proc = await asyncio.create_subprocess_exec(
            ssh_keygen,
            *cmd,
            cwd=local_working_directory,
        )

        await proc.wait()

        with open(os.path.join(local_working_directory, "key")) as f:
            ssh_private_key = f.read()

        with open(os.path.join(local_working_directory, "key.pub")) as f:
            ssh_public_key = f.read()
        return ssh_private_key, ssh_public_key
