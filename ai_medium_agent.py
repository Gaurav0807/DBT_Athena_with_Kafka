from pathlib import Path
import os
import sys
import requests
from typing import Any

HF_ROUTER_URL = "https://router.huggingface.co/models"


def build_prompt(readme_text: str) -> str:
    return f"""
Convert the following GitHub README into a well-structured Medium blog post.

Requirements:
- Catchy title
- Clear intro
- Architecture overview
- Key features
- Use cases
- Conclusion
- Friendly developer tone

README:
{readme_text}
"""


def call_hf_inference(repo_id: str, prompt: str, token: str, timeout: int = 300) -> str:
    url = f"{HF_ROUTER_URL}/{repo_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True},
        "parameters": {
            "max_new_tokens": 800,
            "temperature": 0.5,
        },
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)

    try:
        data: Any = resp.json()
    except ValueError:
        resp.raise_for_status()

    if resp.status_code != 200:
        if isinstance(data, dict) and "error" in data:
            raise RuntimeError(f"Hugging Face API error: {data['error']}")
        raise RuntimeError(f"Hugging Face API returned {resp.status_code}: {resp.text}")

    # Handle common HF response shapes
    if isinstance(data, list):
        texts = []
        for item in data:
            if isinstance(item, dict) and "generated_text" in item:
                texts.append(item["generated_text"])
        if texts:
            return "\n".join(texts)

    if isinstance(data, dict):
        if "generated_text" in data:
            return data["generated_text"]

    raise RuntimeError(f"Unexpected response shape from Hugging Face: {data}")


def main():
    readme_path = Path("./README.md")  # FIX: correct filename
    if not readme_path.exists():
        print("README.md not found in repo root", file=sys.stderr)
        sys.exit(1)

    readme = readme_path.read_text(encoding="utf-8")

    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not hf_token:
        print("Environment variable HUGGINGFACEHUB_API_TOKEN is required", file=sys.stderr)
        sys.exit(1)

    repo_id = os.getenv("HF_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")

    prompt = build_prompt(readme[:6000])

    try:
        print(f"🤖 Calling Hugging Face Router for model {repo_id}...")
        output = call_hf_inference(repo_id, prompt, hf_token)
    except Exception as e:
        print(f"❌ Error while calling Hugging Face API: {e}", file=sys.stderr)
        sys.exit(1)

    Path("medium.md").write_text(output, encoding="utf-8")
    print("✅ medium.md generated from README")


if __name__ == "__main__":
    main()
