# MCP Client: Local Private AI & Data Platform

A secure, local, and private AI-powered data management platform with a modern UI, user authentication, admin tools, and one-click Docker or Codespaces setup. Built with Python, FastAPI, Streamlit, SQLite, and supports local LLMs (Ollama, Llama, etc).

---

## Features
- **Ask AI:** Chat with local LLMs (Llama, Mistral, etc) with guardrails and conversation history.
- **Data Management:** CRUD, search, import/export, and file upload for your data.
- **User Authentication:** Register, login, password reset, account lockout, and email notifications.
- **Admin Panel:** List users, audit log, and role-based access.
- **Audit Logging:** All actions are logged for security.
- **One-click Setup:** Docker and GitHub Codespaces support for easy cross-platform deployment.

---

## Quick Start (Docker)
1. **Clone the repo:**
   ```sh
   git clone https://github.com/Anteneh-T-Tessema/01_local_private_mcp.git
   cd 01_local_private_mcp
   ```
2. **Copy `.env.example` to `.env` and edit as needed.**
3. **Run:**
   ```sh
   docker-compose up --build
   ```
4. **Open:** [http://localhost:8501](http://localhost:8501)

---

## Quick Start (GitHub Codespaces)
1. Open the repo in Codespaces (green **Code** button → **Codespaces** tab → **Create codespace**).
2. In the Codespaces terminal:
   ```sh
   pip install -r requirements.txt
   streamlit run cli_app.py --server.port 8501 --server.address 0.0.0.0
   ```
3. Click the forwarded port link to open the app.

---

## Manual Local Setup
1. Install Python 3.11+
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the app:
   ```sh
   streamlit run cli_app.py
   ```

---

## Configuration
- Edit `.env` for SMTP/email settings (optional, for notifications).
- User data is stored in `users.db` (SQLite, local and private).

---

## Security & Privacy
- All data and AI runs locally by default.
- No data leaves your machine unless you configure external services.

---

## License
MIT

---

## Author
[Anteneh T. Tessema](https://github.com/Anteneh-T-Tessema)
