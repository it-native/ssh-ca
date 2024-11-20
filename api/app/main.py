"""
    An API for signing SSH keys.
    TODO: Better docs...
"""

import os
from typing import Union
import subprocess

from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse

from . import schemas

app: FastAPI = FastAPI()

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
async def sign_certificate(
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
