import os
from pathlib import Path

import streamlit as st
from groq import Groq

from utils.pdf_processor import extract_pdf, split_into_chunks, rank_chunks
from utils.ai_engine import summarize_paper, compare_papers, answer_question


st.set_page_config(
    page_title="PaperLens | AI Research Summarizer",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background: #f7f8fc; }
    [data-testid="stHeader"] { background: rgba(247,248,252,.92); }
    .block-container { padding-top: 1.7rem; padding-bottom: 3rem; max-width: 1200px; }
    .hero {
        padding: 1.7rem 1.9rem; border-radius: 20px;
        background: linear-gradient(120deg, #14213d 0%, #253c72 55%, #4169a8 100%);
        color: white; margin-bottom: 1.2rem;
    }
    .hero h1 { color: white; font-size: 2.25rem; margin: 0 0 .4rem 0; }
    .hero p { color: #e6edff; font-size: 1.02rem; margin: 0; }
    .eyebrow { color: #b9ccff; text-transform: uppercase; letter-spacing: .12em;
               font-size: .72rem; font-weight: 700; margin-bottom: .55rem; }
    .metric-card {
        background: white; border: 1px solid #e7eaf2; border-radius: 14px;
        padding: 1rem 1.1rem; min-height: 95px;
    }
    .metric-label { color: #68738a; font-size: .82rem; }
    .metric-value { color: #17233c; font-size: 1.45rem; font-weight: 750; }
    .section-note { color: #65718a; font-size: .92rem; }
    div[data-testid="stFileUploader"] {
        background: white; border: 1px dashed #aebbd2; border-radius: 14px; padding: .6rem;
    }
    .stButton > button[kind="primary"] { border-radius: 10px; font-weight: 650; }
    div[data-testid="stTabs"] button { font-weight: 650; }
    .small-muted { color: #748098; font-size: .82rem; }
</style>
""", unsafe_allow_html=True)


def get_secret_key():
    """Read the Groq API key from environment variables or Streamlit Secrets."""
    key = os.getenv("GROQ_API_KEY", "")
    try:
        key = st.secrets.get("GROQ_API_KEY", key)
    except Exception:
        pass
    return key


def get_client(api_key):
    return Groq(api_key=api_key)


def ensure_paper(uploaded_file):
    """Extract and cache a paper once per filename and file size."""
    cache_key = f"{uploaded_file.name}:{uploaded_file.size}"
    if cache_key not in st.session_state.papers:
        with st.spinner(f"Reading {uploaded_file.name}..."):
            extracted = extract_pdf(uploaded_file.getvalue())
            chunks = split_into_chunks(extracted["pages"])
            st.session_state.papers[cache_key] = {
                "key": cache_key,
                "name": uploaded_file.name,
                "pages": extracted["pages"],
                "text": extracted["text"],
                "chunks": chunks,
                "summary": None,
            }
    return st.session_state.papers[cache_key]


def run_summary(paper, client, model):
    if not paper["text"].strip():
        raise ValueError(
            "No selectable text was found in this PDF. "
            "It may be a scanned document."
        )
    paper["summary"] = summarize_paper(
        client, model, paper["name"], paper["chunks"]
    )
    return paper["summary"]


if "papers" not in st.session_state:
    st.session_state.papers = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None
if "comparison_names" not in st.session_state:
    st.session_state.comparison_names = []


with st.sidebar:
    st.markdown("## 📘 PaperLens")
    st.caption("Generative AI research assistant")
    st.markdown("---")
    st.markdown("### AI configuration")

    api_key = st.text_input(
        "Groq API key",
        value=get_secret_key(),
        type="password",
        help="For deployment, store this in Streamlit Secrets instead of sharing it.",
    )

    # Updated Groq model IDs; retired Llama model IDs have been removed.
    model = st.selectbox(
        "Groq model",
        ["openai/gpt-oss-120b", "openai/gpt-oss-20b"],
        index=0,
        help="Choose a model currently available to your Groq account.",
    )

    st.markdown("---")
    st.markdown("### Your workspace")
    st.metric("Papers loaded", len(st.session_state.papers))

    if st.button("Clear session papers", use_container_width=True):
        st.session_state.papers = {}
        st.session_state.chat_history = []
        st.session_state.comparison_result = None
        st.session_state.comparison_names = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<div class="small-muted">PaperLens is an educational prototype. '
        'Always verify AI outputs against the original paper.</div>',
        unsafe_allow_html=True,
    )


st.markdown("""
<div class="hero">
  <div class="eyebrow">Generative AI • Academic productivity</div>
  <h1>Understand research. Faster.</h1>
  <p>Upload papers, explore key findings, compare studies, and ask questions in plain language.</p>
</div>
""", unsafe_allow_html=True)


uploaded_files = st.file_uploader(
    "Upload research paper PDF files",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload one paper to summarize or multiple papers to compare. Text-based PDFs work best.",
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            ensure_paper(uploaded_file)
        except Exception as exc:
            st.error(f"Could not read {uploaded_file.name}: {exc}")


papers = list(st.session_state.papers.values())

if papers:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="metric-card"><div class="metric-label">Papers in workspace</div>'
            f'<div class="metric-value">{len(papers)}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        total_pages = sum(len(paper["pages"]) for paper in papers)
        st.markdown(
            '<div class="metric-card"><div class="metric-label">PDF pages processed</div>'
            f'<div class="metric-value">{total_pages}</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        ready = sum(1 for paper in papers if paper["summary"])
        st.markdown(
            '<div class="metric-card"><div class="metric-label">Summaries generated</div>'
            f'<div class="metric-value">{ready}</div></div>',
            unsafe_allow_html=True,
        )


st.markdown("")
tab_summary, tab_compare, tab_chat = st.tabs([
    "📝  Summarize paper",
    "⚖️  Compare research",
    "💬  Chat with paper",
])


with tab_summary:
    st.subheader("Research paper summary")
    st.markdown(
        '<div class="section-note">Create a structured summary with the research question, '
        'methodology, findings, and limitations.</div>',
        unsafe_allow_html=True,
    )

    if not papers:
        st.info("Upload a PDF above to get started.")
    else:
        selected_name = st.selectbox(
            "Choose a paper",
            options=[paper["name"] for paper in papers],
            key="summary_choice",
        )
        selected = next(paper for paper in papers if paper["name"] == selected_name)
        st.caption(
            f"{len(selected['pages'])} pages • {len(selected['text']):,} extracted characters"
        )

        if st.button("Generate summary", type="primary", key="generate_summary"):
            if not api_key:
                st.error("Add your Groq API key in the sidebar first.")
            else:
                try:
                    with st.spinner(
                        "Analyzing the paper. Longer papers may take a little more time..."
                    ):
                        run_summary(selected, get_client(api_key), model)
                    st.success("Summary generated.")
                except Exception as exc:
                    st.error(f"Could not generate summary: {exc}")

        if selected["summary"]:
            st.markdown(selected["summary"])
            safe_name = Path(selected["name"]).stem.replace(" ", "_")
            st.download_button(
                "⬇️ Download summary (.md)",
                data=selected["summary"],
                file_name=f"{safe_name}_summary.md",
                mime="text/markdown",
                key=f"download_{selected['key']}",
            )

        with st.expander("Preview extracted PDF text"):
            st.text(selected["text"][:7000] or "No selectable text found.")
            if len(selected["text"]) > 7000:
                st.caption("Preview shortened.")


with tab_compare:
    st.subheader("Compare research papers")
    st.markdown(
        '<div class="section-note">Compare the research problem, methods, findings, '
        'and limitations across two or more papers.</div>',
        unsafe_allow_html=True,
    )

    if len(papers) < 2:
        st.info("Upload at least two PDF papers to use research comparison.")
    else:
        paper_names = [paper["name"] for paper in papers]
        chosen_names = st.multiselect(
            "Select papers to compare",
            options=paper_names,
            default=paper_names[:min(2, len(paper_names))],
            max_selections=4,
        )

        if st.button("Compare selected papers", type="primary", key="compare_button"):
            if not api_key:
                st.error("Add your Groq API key in the sidebar first.")
            elif len(chosen_names) < 2:
                st.warning("Select at least two papers.")
            else:
                chosen = [
                    paper for paper in papers if paper["name"] in chosen_names
                ]
                try:
                    client = get_client(api_key)
                    with st.spinner("Preparing paper summaries and comparing them..."):
                        for paper in chosen:
                            if not paper["summary"]:
                                run_summary(paper, client, model)

                        comparison = compare_papers(
                            client,
                            model,
                            [
                                {"name": paper["name"], "summary": paper["summary"]}
                                for paper in chosen
                            ],
                        )

                    st.session_state["comparison_result"] = comparison
                    st.session_state["comparison_names"] = chosen_names
                except Exception as exc:
                    st.error(f"Comparison failed: {exc}")

        if st.session_state.get("comparison_result"):
            st.markdown(st.session_state["comparison_result"])
            st.download_button(
                "⬇️ Download comparison (.md)",
                data=st.session_state["comparison_result"],
                file_name="research_paper_comparison.md",
                mime="text/markdown",
                key="download_comparison",
            )


with tab_chat:
    st.subheader("Ask questions about your paper")
    st.markdown(
        '<div class="section-note">Ask about concepts, methods, results, or limitations. '
        'Answers are grounded in relevant extracted passages and the generated summary '
        'when available.</div>',
        unsafe_allow_html=True,
    )

    if not papers:
        st.info("Upload a PDF above to start a research conversation.")
    else:
        chat_paper_names = st.multiselect(
            "Choose paper(s) for this question",
            options=[paper["name"] for paper in papers],
            default=[papers[0]["name"]],
            key="chat_paper_choices",
        )
        question = st.text_area(
            "Your question",
            placeholder="Example: What problem does this paper solve, and what evidence supports its main conclusion?",
            height=90,
            key="chat_question",
        )

        if st.button("Ask PaperLens", type="primary", key="ask_button"):
            if not api_key:
                st.error("Add your Groq API key in the sidebar first.")
            elif not question.strip():
                st.warning("Enter a question first.")
            elif not chat_paper_names:
                st.warning("Choose at least one paper.")
            else:
                chosen = [
                    paper for paper in papers if paper["name"] in chat_paper_names
                ]
                try:
                    client = get_client(api_key)
                    context_items = []

                    for paper in chosen:
                        if not paper["summary"]:
                            with st.spinner(
                                f"Creating a quick summary for {paper['name']}..."
                            ):
                                run_summary(paper, client, model)

                        relevant = rank_chunks(paper["chunks"], question, limit=4)
                        context_items.append({
                            "name": paper["name"],
                            "summary": paper["summary"],
                            "passages": relevant,
                        })

                    with st.spinner("Preparing an answer..."):
                        answer = answer_question(
                            client, model, question, context_items
                        )

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "papers": chat_paper_names[:],
                    })
                except Exception as exc:
                    st.error(f"Could not answer the question: {exc}")

        if st.session_state.chat_history:
            st.markdown("---")
            for item in reversed(st.session_state.chat_history):
                with st.chat_message("user"):
                    st.write(item["question"])
                with st.chat_message("assistant"):
                    st.markdown(item["answer"])
                    st.caption("Sources selected: " + ", ".join(item["papers"]))

            if st.button("Clear chat history", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()


st.markdown("---")
st.caption(
    "PaperLens • Built with Python, Streamlit, Groq, and PyPDF. "
    "AI-generated content may contain errors; check the original publication."
)
