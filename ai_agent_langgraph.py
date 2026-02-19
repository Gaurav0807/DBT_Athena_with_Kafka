from pathlib import Path
import os
import sys


from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field


class BlogState(BaseModel):
    readme: str = Field(default="", description="README content")
    blog: str = Field(default="", description="Generated blog")
    score: int = Field(default=0, description="Quality score")
    rewrite_count: int = Field(default=0, description="Number of rewrites")

def get_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is required")

    return ChatOpenAI(
        model="mistralai/mistral-7b-instruct",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.5,
        max_tokens=800,
    )


def load_readme(state: BlogState) -> BlogState:
    readme_path = Path("./Readme.md")
    if not readme_path.exists():
        raise FileNotFoundError("Readme.md not found")

    state.readme = readme_path.read_text(encoding="utf-8")
    return state

def generate_blog(state: BlogState) -> BlogState:
    llm = get_llm()

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

    Please Don't create Image Just architecture and highlevel about everything. Also do proper formatting of the article

    README:
    {readme}
    """)

    chain = prompt | llm | StrOutputParser()
    state.blog = chain.invoke({"readme": state.readme[:6000000]})
    return state

def evaluate_blog(state: BlogState) -> BlogState:
    llm = get_llm()

    judge_prompt = f"""
    Rate the quality of the following blog from 1 to 10.
    Only return a single number. Give number based on proper spacing and proper read able content

    Blog:
    {state.blog}
    """

    score_text = llm.invoke(judge_prompt).content.strip()

    try:
        state.score = int(score_text)
    except:
        state.score = 5

    print(f" Blog Quality Score: {state.score}/10")
    return state

def rewrite_blog(state: BlogState) -> BlogState:
    llm = get_llm()

    rewrite_prompt = f"""
    Improve the following blog to be more engaging, structured, and developer-friendly.

    Blog:
    {state.blog}
    """

    state.blog = llm.invoke(rewrite_prompt).content
    state.rewrite_count += 1

    print(f"✍️ Rewriting blog... Attempt #{state.rewrite_count}")
    return state



#Save Blog
def save_blog(state: BlogState) -> BlogState:
    Path("./medium_blog_with_langraph.md").write_text(state.blog, encoding="utf-8")
    print("✅ medium.md generated successfully!")
    return state


#Router Logic
def quality_router(state: BlogState):
    # Stop after 3 rewrite attempts
    if state.score < 7 and state.rewrite_count < 3:
        return "rewrite_blog"
    return "save_blog"





def build_graph():
    graph = StateGraph(BlogState)

    graph.add_node("load_readme", load_readme)
    graph.add_node("generate_blog", generate_blog)
    graph.add_node("evaluate_blog", evaluate_blog)
    graph.add_node("rewrite_blog", rewrite_blog)
    graph.add_node("save_blog", save_blog)

    graph.add_edge(START, "load_readme")
    graph.add_edge("load_readme", "generate_blog")
    graph.add_edge("generate_blog", "evaluate_blog")

    graph.add_conditional_edges(
        "evaluate_blog",
        quality_router,
        {
            "rewrite_blog": "rewrite_blog",
            "save_blog": "save_blog",
        },
    )

    graph.add_edge("rewrite_blog", "evaluate_blog")
    graph.add_edge("save_blog", END)

    return graph.compile()

if __name__ == "__main__":
    app = build_graph()
    app.invoke(BlogState())