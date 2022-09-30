from fastapi import APIRouter

from ansible_events_ui.key import generate_ssh_keys
from ansible_events_ui.managers import secretsmanager

router = APIRouter()


@router.get("/api/ssh-public-key")
async def ssh_public_key():
    if secretsmanager.has_secret("ssh-public-key"):
        return {"public_key": secretsmanager.get_secret("ssh-public-key")}
    else:
        ssh_private_key, ssh_public_key = await generate_ssh_keys()
        secretsmanager.set_secret("ssh-public-key", ssh_public_key)
        secretsmanager.set_secret("ssh-private-key", ssh_private_key)
        return {"public_key": secretsmanager.get_secret("ssh-public-key")}
