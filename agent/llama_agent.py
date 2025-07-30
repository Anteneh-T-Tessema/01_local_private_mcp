
# LlamaIndex Agent skeleton


import requests
import json


class LlamaAgent:
    def __init__(self, server_url="http://127.0.0.1:8000", model="llama2"):
        self.server_url = server_url
        self.model = model

    def ollama_generate(self, prompt, model=None):
        """Call local Ollama API for text generation (handles streaming JSON lines)."""
        if model is None:
            model = self.model
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt},
                stream=True
            )
            resp.raise_for_status()
            responses = []
            for line in resp.iter_lines():
                if line:
                    print(f"Ollama raw line: {line}")  # Debug print
                    try:
                        data = json.loads(line)
                        # Only append non-empty responses
                        if "response" in data and data["response"]:
                            responses.append(data["response"])
                    except Exception as e:
                        print(f"ollama_generate parse error: {e}\nLine: {line}")
            answer = "".join(responses).strip()
            if answer:
                return answer
            else:
                return "[Ollama returned no response for this prompt]"
        except Exception as e:
            print(f"ollama_generate error: {e}")
            return {"error": str(e)}

    def update_data(self, data_id, content):
        resp = requests.put(f"{self.server_url}/update_data", json={"id": data_id, "content": content})
        try:
            return resp.json()
        except Exception as e:
            print(f"update_data error: {e}\nStatus: {resp.status_code}\nText: {resp.text}")
            return {"error": str(e), "status": resp.status_code, "text": resp.text}

    def delete_data(self, data_id):
        resp = requests.delete(f"{self.server_url}/delete_data/{data_id}")
        try:
            return resp.json()
        except Exception as e:
            print(f"delete_data error: {e}\nStatus: {resp.status_code}\nText: {resp.text}")
            return {"error": str(e), "status": resp.status_code, "text": resp.text}

    def search_data(self, query):
        resp = requests.get(f"{self.server_url}/search_data", params={"q": query})
        try:
            return resp.json()
        except Exception as e:
            print(f"search_data error: {e}\nStatus: {resp.status_code}\nText: {resp.text}")
            return {"error": str(e), "status": resp.status_code, "text": resp.text}

    def list_data(self):
        resp = requests.get(f"{self.server_url}/list_data")
        try:
            return resp.json()
        except Exception as e:
            print(f"list_data error: {e}\nStatus: {resp.status_code}\nText: {resp.text}")
            return {"error": str(e), "status": resp.status_code, "text": resp.text}

    def add_data(self, content):
        resp = requests.post(f"{self.server_url}/add_data", json={"content": content})
        try:
            return resp.json()
        except Exception as e:
            print(f"add_data error: {e}\nStatus: {resp.status_code}\nText: {resp.text}")
            return {"error": str(e), "status": resp.status_code, "text": resp.text}

    def read_data(self, data_id):
        resp = requests.get(f"{self.server_url}/read_data/{data_id}")
        try:
            return resp.json()
        except Exception as e:
            print(f"read_data error: {e}\nStatus: {resp.status_code}\nText: {resp.text}")
            return {"error": str(e), "status": resp.status_code, "text": resp.text}

    def handle_query(self, query):
        # AI-powered response using Ollama
        ai_response = self.ollama_generate(query)
        # Store the query and AI response
        self.add_data(f"Q: {query}\nA: {ai_response}")
        return {"ai_response": ai_response}
