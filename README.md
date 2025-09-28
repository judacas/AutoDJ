# AutoDJ

App that mixes songs together automatically.

## Quickstart (API)

- Install dependencies (recommended in your virtualenv):
  ```powershell
  pip install -r requirements.txt
  ```
- Set a `.env` file with required credentials (at minimum):
  - `SPOTIFY_CLIENT_ID`
  - `SPOTIFY_CLIENT_SECRET`
- Run the FastAPI service (either of the following):
  - Direct script (PowerShell):
    ```powershell
    python MonolithDev\gettingSongs\api.py
    ```
  - Uvicorn module path:
    ```powershell
    python -m uvicorn MonolithDev.gettingSongs.api:app --host 127.0.0.1 --port 8000 --reload
    ```
- Open docs: http://127.0.0.1:8000/docs

More details in `MonolithDev/gettingSongs/README.md`.
