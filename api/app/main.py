"""
    An API for signing SSH keys.
    TODO: Better docs...
"""

import os
import random
from typing import Union
import subprocess

from fastapi import FastAPI, Response, Request
from fastapi.responses import PlainTextResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from . import schemas

class SetupBody(BaseModel):
    """
        Required to send the SSH public key
        as a body parameter.
    """
    ssh_key: str

app: FastAPI = FastAPI()

templates: Jinja2Templates = Jinja2Templates(directory="api/templates")

@app.get(
    "/v1/sign/{name}",
    responses={
        200: {
            "model": str
        },
        403: {
            "description": (
                "You did something nasty. Refer to the "
                "message to find out what went wrong."
            ),
            "model": str
        },
        404: {
            "description": (
                "The name you want to use does not exist. "
                "Setting up a name via API will be implemented "
                "in a later release; you will currently have to "
                "do it by hand."
            ),
            "model": str
        }
    },
    response_class=PlainTextResponse
)
async def sign_certificate_v1(
    name: str,
    response: Response,
) -> str:
    """
        Check if this certificate name exists and if so,
        sign it using the cert.sh script.
        Return the value of the new certificate.
    """

    if name in [
        "api",
        ".git",
        "checks",
        "docs",
        "env",
    ]:
        # Disallowed names.
        response.status_code = 403
        return f"{name} is not allowed."

    if not os.path.isdir(name):
        response.status_code = 404
        return f"{name} does not exist."

    subprocess.call([
        "./cert.sh",
        name
    ])

    with open(os.path.join(name, "current-cert.pub"), "r") as fin:
        data = fin.readline().strip()

    return data

@app.get(
    "/v1/ca_certificate",
    response_class=PlainTextResponse
)
async def get_ca_certificate() -> str:
    with open("ca.pub", "r") as fin:
        data = fin.readline().strip()

    return data

@app.get(
    "/v1/setup_script_helper/systemd_timer",
    response_class=PlainTextResponse
)
async def get_systemd_timer(
    request: Request
) -> str:
    return templates.TemplateResponse(
        request=request,
        name="ssh-host-certificate-renew.timer"
    )
@app.get(
    "/v1/setup_script_helper/systemd_service",
    response_class=PlainTextResponse
)
async def get_systemd_service(
    request: Request
) -> str:
    return templates.TemplateResponse(
        request=request,
        name="ssh-host-certificate-renew.service"
    )
@app.get(
    "/v1/setup_script_helper/certificate_checker",
    response_class=PlainTextResponse
)
async def get_script_checker(
    request: Request,
) -> str:

    return templates.TemplateResponse(
        request=request,
        name="check-ssh-host-certificate-renew.sh",
    )

@app.get(
    "/v1/setup_script_helper/certificate_renew/{hostname}",
    response_class=PlainTextResponse
)
async def get_script_renewer(
    request: Request,
    hostname: str
) -> str:

    return templates.TemplateResponse(
        request=request,
        name="renew-ssh-host-certificate.sh",
        context={
            "id": 42,
            "hostname": hostname
        }
    )
@app.get(
    "/v1/setup_script_helper/ssh_config_file",
    response_class=PlainTextResponse
)
async def get_ssh_config_file(
    request: Request,

) -> str:

    return templates.TemplateResponse(
        request=request,
        name="ca-config.conf",
    )
@app.post(
    "/v1/setup_script_helper/setup_host/{hostname}",
    status_code=201
)
async def setup_host_v1(
    request: Request,
    hostname: str,
    body: SetupBody
) -> None:

    client_ip = request.client.host

    # Create directory
    os.mkdir(hostname)

    # Write principals file
    with open(f"{hostname}/principals", "w") as fout:
        fout.write(f"{client_ip},{hostname}")

    # Write SSH key file
    with open(f"{hostname}/ssh_host_ed25519_key.pub", "w") as fout:
        fout.write(body.ssh_key)

@app.get(
    "/v1/setup_script/{hostname}",
    responses={
        200: {
            "model": str
        },
    },
    response_class=PlainTextResponse
)
async def setup(
    request: Request,
    hostname: str,
) -> str:
    """
        Usage: `curl https://domain.com/v1/setup_script/foobar.domain.com | bash
    """

    return templates.TemplateResponse(
        request=request,
        name="setup_script.sh",
        context={
            "id": 42,
            "hostname": hostname
        }
    )
