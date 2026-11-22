def _chat(client, model: str, system_prompt: str, user_prompt: str, max_tokens: int = 3500) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or "The model returned an empty response."


def summarize_paper(client, model: str, paper_name: str, chunks: list) -> str:
    if not chunks:
        raise ValueError("No readable text was extracted from this PDF.")

    partial_summaries = []
    system = (
        "You are a careful academic research assistant. Be factual and neutral. "
        "Never invent authors, statistics, methods, citations, or findings. "
        "If the text does not contain an answer, say it is not stated in the provided text."
    )

    for index, chunk in enumerate(chunks, start=1):
        prompt = f"""
Analyze part {index} of {len(chunks)} from the research paper "{paper_name}".
Create concise notes on:
- Research problem and objectives
- Methodology, data, materials, or participants (only if stated)
- Important results and numerical findings
- Authors' interpretation and limitations
Keep exact numbers and relevant page numbers where visible. Do not guess.

PAPER EXCERPT:
{chunk['text']}
"""
        note = _chat(client, model, system, prompt, max_tokens=1400)
        partial_summaries.append(
            f"### Notes from part {index} (pages {chunk['pages']})\n{note}"
        )

    combined_notes = "\n\n".join(partial_summaries)
    final_prompt = f"""
Prepare a student-friendly but academically accurate summary of "{paper_name}".
Use only the notes below, which were extracted from the paper. Do not add unsupported claims.

Use these headings:
# Research Paper Summary
## 1. Paper overview
## 2. Research problem and objectives
## 3. Methodology
## 4. Main findings
## 5. Conclusion and contribution
## 6. Limitations
## 7. Important terms explained simply
## 8. Three points to remember
## 9. What this paper does not establish

Include a short quick summary at the end. If an item is missing from the notes,
write "Not clearly stated in the extracted text." Preserve numbers accurately.
Do not invent the paper's title, author, publication venue, or year.

NOTES:
{combined_notes[:42000]}
"""
    return _chat(client, model, system, final_prompt, max_tokens=3500)


def compare_papers(client, model: str, papers: list) -> str:
    system = (
        "You are an academic comparison assistant. Compare only evidence in the supplied summaries. "
        "Do not assume two papers are directly comparable if their goals or methods differ. "
        "Never invent facts or citations."
    )
    paper_text = "\n\n".join(
        f"## PAPER: {paper['name']}\n{paper['summary']}" for paper in papers
    )
    prompt = f"""
Compare the following research papers for a student.

Create:
# Research Paper Comparison
## 1. Overview of each paper
## 2. Research problems and objectives
## 3. Methodology comparison
## 4. Findings comparison
## 5. Similarities
## 6. Differences
## 7. Strengths and limitations reported
## 8. Research gaps or future directions (only when supported)
## 9. Overall takeaway

Include a compact Markdown comparison table. Use "Not stated" when details are unavailable.
Do not claim one paper is better unless the evidence supports a specific, explained criterion.

PAPER SUMMARIES:
{paper_text[:46000]}
"""
    return _chat(client, model, system, prompt, max_tokens=3500)


def answer_question(client, model: str, question: str, papers: list) -> str:
    system = (
        "You are PaperLens, a research-paper question-answering assistant. "
        "Answer in clear language and ground every factual claim in the supplied context. "
        "If the context does not answer the question, say so. Never fabricate page numbers, "
        "quotes, results, authors, or citations. Distinguish the paper's claims from your explanation."
    )
    context_blocks = []
    for paper in papers:
        passages = "\n\n".join(
            f"Relevant passage (pages {p['pages']}):\n{p['text']}"
            for p in paper["passages"]
        )
        context_blocks.append(
            f"### PAPER: {paper['name']}\n"
            f"SUMMARY:\n{paper['summary'][:10000]}\n\n"
            f"RELEVANT EXTRACTS:\n{passages[:18000]}"
        )
    prompt = f"""
Answer this student question:
{question}

Use the following paper context. If multiple papers are selected, identify which paper
supports each point. If the evidence is incomplete, clearly state the limitation.
End with a short "Based on" line naming the selected paper(s).

CONTEXT:
{chr(10).join(context_blocks)[:40000]}
"""
    return _chat(client, model, system, prompt, max_tokens=2200)
