#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import asyncio
import logging
import os
import shutil
import tempfile

ssh_keygen = shutil.which("ssh-keygen")
logger = logging.getLogger()


async def generate_ssh_keys():

    with tempfile.TemporaryDirectory() as local_working_directory:
        cmd = ["-f", "key", "-P", "", "-C", "eda-server"]
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
