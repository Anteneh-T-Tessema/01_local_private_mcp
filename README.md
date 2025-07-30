# MCP Client: One-Click Setup (Windows, Mac, Linux)

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac)
- [Docker Engine](https://docs.docker.com/engine/install/) (Linux)

## Setup Steps
1. Copy `.env.example` to `.env` and fill in your SMTP/email settings (optional for email notifications).
2. Open a terminal in this folder.
3. Run:

   ```sh
   docker-compose up --build
   ```

4. Open [http://localhost:8501](http://localhost:8501) in your browser.

- All dependencies, Python, and environment variables are handled by Docker.
- User data is stored in `users.db` in this folder (persistent across restarts).

## Updating
- To update code, stop Docker (`Ctrl+C`), make changes, then run `docker-compose up --build` again.

## Stopping
- Press `Ctrl+C` in the terminal, or run:
  ```sh
  docker-compose down
  ```

---

For advanced users: you can still run locally with Python and `requirements.txt` if you prefer.
