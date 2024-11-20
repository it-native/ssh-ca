"""
    Running the web server for debugging.
"""

import uvicorn
import os

os.chdir(os.path.join(
    os.path.dirname(__file__), # File is ./api/app/__main__.py
    "..", # ./api/
    "..", # ./
))

if __name__ == "__main__":
    uvicorn.run(
        "api.app.main:app",
        host="0.0.0.0",
        port=8999,
        reload=True
    )
