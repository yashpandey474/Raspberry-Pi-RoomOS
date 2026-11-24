import httpx
import json

payload = {
    "model": "qwen3.5:2b-q4_K_M",
    "messages": [
        {
            "role": "user",
            "content": (
                "Use the calculate tool to calculate 12500 * 0.18. "
                "Do not calculate it yourself."
            ),
        }
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a mathematical expression.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string"
                        }
                    },
                    "required": ["expression"],
                    "additionalProperties": False,
                },
            },
        }
    ],
    "stream": False,
    "options": {
        "temperature": 0
    },
}

response = httpx.post(
    "http://127.0.0.1:11434/api/chat",
    json=payload,
    timeout=120,
)

response.raise_for_status()

message = response.json()["message"]

print(json.dumps(message, indent=2))

print("\nTool calls:", message.get("tool_calls", []))