
import streamlit as st
from agent.llama_agent import LlamaAgent
import sqlite3
import bcrypt
import smtplib
from email.mime.text import MIMEText
import os
# --- Email Notification ---
def send_email(to_email, subject, body):
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    from_email = os.environ.get("SMTP_FROM", smtp_user)
    if not (smtp_host and smtp_user and smtp_pass and to_email):
        return False
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False

st.title("MCP Client: AI & Data Interface")



# --- Model Selection ---
available_models = [
    "llama3:latest",
    "llama2:latest",
    "mistral:latest",
    "phi3:latest",
    "openchat:latest"
]
selected_model = st.sidebar.selectbox("AI Model", available_models, index=0)

# Store the selected model in session state to persist across reruns
if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = selected_model
if selected_model != st.session_state["selected_model"]:
    st.session_state["selected_model"] = selected_model

agent = LlamaAgent(model=st.session_state["selected_model"])

# --- Guardrail AI Agent ---
def guardrail_ai_response(response, banned_words=None, max_length=1200):
    """
    Checks the AI response for banned words and excessive length.
    Returns (is_safe, message).
    """
    if not isinstance(response, str):
        return False, "AI response is not a string."
    if banned_words is None:
        banned_words = ["hate", "violence", "kill", "terrorist", "racist", "sexist"]
    for word in banned_words:
        if word.lower() in response.lower():
            return False, f"Guardrail: Response blocked due to inappropriate content (word: '{word}')."
    if len(response) > max_length:
        return False, f"Guardrail: Response too long (>{max_length} characters)."
    return True, response


menu = [
    "Ask AI", "List Data", "Search Data", "Add Data", "Update Data", "Delete Data", "File Upload", "Export Data", "Import Data"
]
choice = st.sidebar.selectbox("Menu", menu)



# --- User Authentication (SQLite + bcrypt) ---
def get_db():
    conn = sqlite3.connect("users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            failed_attempts INTEGER DEFAULT 0,
            locked_until DATETIME
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    """)
    return conn

def log_action(username, action, details=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO audit_log (username, action, details) VALUES (?, ?, ?)", (username, action, details))
    conn.commit()
    conn.close()

def register_form():
    st.subheader("Register New User")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    new_email = st.text_input("Email (optional)")
    is_admin = False
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    conn.close()
    # Only allow admin registration if logged in as admin or first user
    if user_count == 0 or (st.session_state.get("authenticated") and st.session_state.get("role") == "admin"):
        is_admin = st.checkbox("Register as admin", value=(user_count == 0))
    if st.button("Register"):
        if not new_username or not new_password:
            st.warning("Username and password required.")
            return
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username=?", (new_username,))
        if cur.fetchone():
            st.error("Username already exists.")
        else:
            pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            role = "admin" if (user_count == 0 or is_admin) else "user"
            cur.execute("INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)", (new_username, pw_hash, new_email, role))
            conn.commit()
            log_action(new_username, "register", f"role={role}")
            if new_email:
                send_email(new_email, "Welcome to MCP Client", f"Hello {new_username},\n\nYour account has been created.\nRole: {role}\n")
            st.success(f"Registration successful! You are registered as '{role}'. Please log in.")
        conn.close()
    if st.button("Back to Login"):
        st.session_state["show_register"] = False
        st.experimental_rerun()

# --- Password Reset ---
def password_reset_form():
    st.subheader("Reset Password")
    username = st.text_input("Username to reset")
    new_password = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        if not username or not new_password:
            st.warning("Username and new password required.")
            return
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT username, email FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if not row:
            st.error("Username does not exist.")
        else:
            pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            cur.execute("UPDATE users SET password_hash=? WHERE username=?", (pw_hash, username))
            conn.commit()
            log_action(username, "password_reset")
            if row[1]:
                send_email(row[1], "MCP Client Password Reset", f"Hello {username},\n\nYour password has been reset. If you did not request this, please contact support.")
            st.success("Password reset successful! Please log in.")
        conn.close()

def login_form():
    import datetime
    st.title("Login to MCP Client")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT password_hash, role, failed_attempts, locked_until FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        now = datetime.datetime.now()
        if row:
            pw_hash, role, failed_attempts, locked_until = row
            # Check lockout
            if locked_until:
                try:
                    locked_until_dt = datetime.datetime.fromisoformat(locked_until)
                except Exception:
                    locked_until_dt = None
                if locked_until_dt and now < locked_until_dt:
                    mins = int((locked_until_dt - now).total_seconds() // 60) + 1
                    st.error(f"Account locked due to too many failed attempts. Try again in {mins} minutes.")
                    conn.close()
                    return
            if bcrypt.checkpw(password.encode(), pw_hash.encode()):
                # Reset failed attempts
                cur.execute("UPDATE users SET failed_attempts=0, locked_until=NULL WHERE username=?", (username,))
                conn.commit()
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = role
                log_action(username, "login")
                st.success(f"Login successful! Role: {role}")
            else:
                failed_attempts = (failed_attempts or 0) + 1
                lockout = False
                if failed_attempts >= 5:
                    locked_until_dt = now + datetime.timedelta(minutes=10)
                    cur.execute("UPDATE users SET failed_attempts=?, locked_until=? WHERE username=?", (failed_attempts, locked_until_dt.isoformat(), username))
                    lockout = True
                else:
                    cur.execute("UPDATE users SET failed_attempts=? WHERE username=?", (failed_attempts, username))
                conn.commit()
                if lockout:
                    st.error("Account locked due to too many failed attempts. Try again in 10 minutes.")
                else:
                    st.error(f"Invalid username or password. {5 - failed_attempts} attempts left before lockout.")
        else:
            st.error("Invalid username or password.")
        conn.close()
    if st.button("Create an account"):
        st.session_state["show_register"] = True
        st.experimental_rerun()
    st.info(":blue[Forgot your password?]")
    if st.button("Forgot Password?"):
        st.session_state["show_reset"] = True


# Show registration or password reset form if requested
if st.session_state.get("show_register"):
    register_form()
elif st.session_state.get("show_reset"):
    password_reset_form()
    if st.button("Back to Login"):
        st.session_state["show_reset"] = False
        st.experimental_rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None

if not st.session_state["authenticated"]:
    login_form()
    st.stop()


# Show user info and logout in sidebar
if st.session_state["authenticated"]:
    st.sidebar.markdown(f"**Logged in as:** `{st.session_state['username']}`  ")
    st.sidebar.markdown(f"**Role:** `{st.session_state['role']}`")
    if st.sidebar.button("Logout"):
        log_action(st.session_state["username"], "logout")
        for key in ["authenticated", "username", "role", "conversation"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

# --- Admin Panel ---
if st.session_state["authenticated"] and st.session_state["role"] == "admin":
    with st.sidebar.expander("Admin Panel", expanded=False):
        if st.button("List All Users"):
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT username, role FROM users")
            users = cur.fetchall()
            conn.close()
            log_action(st.session_state["username"], "admin_list_users")
            st.write("### Registered Users:")
            for u, r in users:
                st.write(f"- {u} ({r})")

if "conversation" not in st.session_state:
    st.session_state["conversation"] = []  # List of (user, ai) tuples

if choice == "Ask AI":
    st.markdown("### Conversation History")
    for i, (user, ai) in enumerate(st.session_state["conversation"]):
        st.markdown(f"**You:** {user}")
        st.markdown(f"**AI:** {ai}")
        st.markdown("---")
    query = st.text_input("Enter your question:")
    if st.button("Ask"):
        # Build conversation context for the agent
        context = "\n".join([f"User: {u}\nAI: {a}" for u, a in st.session_state["conversation"]])
        prompt = f"{context}\nUser: {query}\nAI:"
        # Streaming support: if agent has 'stream_query', use it
        if hasattr(agent, "stream_query"):
            st.markdown("**AI Answer (streaming):**\n")
            response_placeholder = st.empty()
            streamed_answer = ""
            with st.spinner("Thinking..."):
                for chunk in agent.stream_query(prompt):
                    streamed_answer += chunk
                    # Advanced formatting: render markdown with code blocks, tables, images
                    response_placeholder.markdown(streamed_answer, unsafe_allow_html=True)
            is_safe, guardrail_msg = guardrail_ai_response(streamed_answer)
            if is_safe:
                st.session_state["conversation"].append((query, streamed_answer))
            else:
                st.warning(guardrail_msg)
        else:
            with st.spinner("Thinking..."):
                result = agent.handle_query(prompt)
            if "ai_response" in result:
                if isinstance(result["ai_response"], dict) and "error" in result["ai_response"]:
                    st.error(f"AI Error: {result['ai_response']['error']}")
                else:
                    is_safe, guardrail_msg = guardrail_ai_response(result["ai_response"])
                    if is_safe:
                        # Advanced formatting: render markdown with code blocks, tables, images
                        st.markdown(f"**AI Answer:**\n\n{guardrail_msg}", unsafe_allow_html=True)
                        # Add to conversation history
                        st.session_state["conversation"].append((query, guardrail_msg))
                    else:
                        st.warning(guardrail_msg)
            else:
                st.warning("No response from AI.")
    if st.button("Clear Conversation"):
        st.session_state["conversation"] = []

elif choice == "List Data":
    data = agent.list_data()
    if isinstance(data, dict) and "data" in data:
        st.dataframe(data["data"])
    else:
        st.write(data)

elif choice == "Search Data":
    search_term = st.text_input("Search term:")
    if st.button("Search"):
        with st.spinner("Searching..."):
            result = agent.search_data(search_term)
        if isinstance(result, dict) and "data" in result:
            st.dataframe(result["data"])
        else:
            st.write(result)

elif choice == "Add Data":
    content = st.text_area("Content to add:")
    if st.button("Add"):
        result = agent.add_data(content)
        st.write(result)

elif choice == "Delete Data":
    data_id = st.number_input("Data ID to delete:", min_value=1, step=1)
    if st.button("Delete"):

# --- File Upload Feature ---
        result = agent.delete_data(data_id)
        st.write(result)
