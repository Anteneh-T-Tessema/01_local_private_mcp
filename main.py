# Entry point for MCP Client project
from agent.llama_agent import LlamaAgent
from db.sqlite_db import SQLiteDB


def main():
    print("MCP Client project initialized.")
    agent = LlamaAgent()
    # Demo: Add and read data via agent
    print(agent.handle_query("Test Query"))
    # Demo: List all data via agent
    print("All data:", agent.list_data())

if __name__ == "__main__":
    main()
