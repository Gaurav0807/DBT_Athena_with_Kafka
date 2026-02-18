from pathlib import Path
import os
import sys
import requests


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
    url = f"https://api-inference.huggingface.co/models/{repo_id}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    try:
        data = resp.json()
    except ValueError:
        resp.raise_for_status()

    if resp.status_code != 200:
        # try to surface helpful error
        if isinstance(data, dict) and "error" in data:
            raise RuntimeError(f"Hugging Face API error: {data['error']}")
        raise RuntimeError(f"Hugging Face API returned status {resp.status_code}: {resp.text}")

    # Handle different response shapes
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    if isinstance(data, list):
        # e.g. [{'generated_text': '...'}] or [{'generated_text': '...'}, ...]
        parts = []
        for item in data:
            if isinstance(item, dict) and "generated_text" in item:
                parts.append(item["generated_text"])
            elif isinstance(item, dict) and "generated_texts" in item:
                parts.extend(item["generated_texts"])
        return "\n".join(parts)

    # fallback: try raw string
    if isinstance(data, str):
        return data

    raise RuntimeError("Unexpected response shape from Hugging Face Inference API")


def main():
    readme_path = Path("./Readme.md")
    if not readme_path.exists():
        print("Readme.md not found in repo root", file=sys.stderr)
        sys.exit(1)

    readme = readme_path.read_text()

    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not hf_token:
        print(
            "Environment variable HUGGINGFACEHUB_API_TOKEN is required.\n"
            "Set it in your environment or as a GitHub Actions secret.",
            file=sys.stderr,
        )
        sys.exit(1)

    repo_id = os.getenv("HF_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")

    prompt = build_prompt(readme[:6000])

    try:
        print(f"Calling Hugging Face Inference API for model {repo_id}...")
        output = call_hf_inference(repo_id, prompt, hf_token)
    except Exception as e:
        print(f"Error while calling Hugging Face API: {e}", file=sys.stderr)
        sys.exit(1)

    Path("medium.md").write_text(output)
    print("medium.md generated from README")


if __name__ == "__main__":
    main()
