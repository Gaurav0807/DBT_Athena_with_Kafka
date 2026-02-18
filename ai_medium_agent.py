from pathlib import Path
import os

from langchain_core.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub
from langchain_core.output_parsers import StrOutputParser

# 1. Read README
readme = Path("README.md").read_text()

# 2. LLM
llm = HuggingFaceHub(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    model_kwargs={"temperature": 0.5, "max_new_tokens": 800}
)

# 3. Prompt
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

# 4. Chain
chain = prompt | llm | StrOutputParser()

# 5. Run
blog = chain.invoke({"readme": readme[:6000]})

# 6. Write output
Path("medium.md").write_text(blog)

print(" medium.md generated from README")
