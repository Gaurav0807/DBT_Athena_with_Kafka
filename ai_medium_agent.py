from pathlib import Path
import os
import sys

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


def main():
    readme_path = Path("./Readme.md")  # or README.md
    if not readme_path.exists():
        print("Readme.md not found", file=sys.stderr)
        sys.exit(1)

    readme = readme_path.read_text(encoding="utf-8")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is required", file=sys.stderr)
        sys.exit(1)

    # LangChain LLM via OpenRouter (OpenAI-compatible)
    llm = ChatOpenAI(
        model="mistralai/mistral-7b-instruct",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.5,
        max_tokens=800,
    )

    prompt = PromptTemplate.from_template("""
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
{readme}
""")

    chain = prompt | llm | StrOutputParser()

    blog = chain.invoke({"readme": readme[:6000]})

    Path("./medium.md").write_text(blog, encoding="utf-8")
    print(".............. medium.md generated from README using LangChain + OpenRouter ...................")


if __name__ == "__main__":
    main()


