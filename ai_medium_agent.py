import os
import subprocess
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub
from langchain_core.output_parsers import StrOutputParser

# 1. Read README
readme = Path("README.md").read_text() if Path("README.md").exists() else ""

# 2. Get last commit diff + message
try:
    diff = subprocess.check_output(["git", "diff", "HEAD~1..HEAD"]).decode()
    commit_msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).decode()
except Exception:
    diff = ""
    commit_msg = ""

# 3. LLM
llm = HuggingFaceHub(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    model_kwargs={"temperature": 0.5, "max_new_tokens": 900}
)

# 4. Prompt
prompt = PromptTemplate.from_template("""
You are a senior technical writer.

Generate a high-quality Medium-style article based on:

- Project README
- Latest git commit message
- Code diff

Requirements:
- Catchy title
- Clear problem statement
- Architecture overview
- What changed in this commit
- Why it matters
- Conclusion

README:
{readme}

Commit message:
{commit_msg}

Code diff:
{diff}
""")

# 5. Chain
chain = prompt | llm | StrOutputParser()
blog = chain.invoke({
    "readme": readme[:4000],   # trim to avoid token explosion
    "commit_msg": commit_msg[:1000],
    "diff": diff[:4000],
})

# 6. Write medium.md
Path("medium.md").write_text(blog)
print("✅ medium.md generated")
