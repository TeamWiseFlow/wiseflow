import os
import uvicorn
from .app import app

def main():
    port = int(os.environ.get("WISEFLOW_BACKEND_PORT", 8077))
    uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    main()
