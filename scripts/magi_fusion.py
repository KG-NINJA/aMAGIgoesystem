import os, sys, json, datetime
import openai, anthropic, google.generativeai as genai
from sentence_transformers import SentenceTransformer, util

openai.api_key = os.getenv("OPENAI_API_KEY")
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === 各AI回答 ===
def ask_openai(q):
    r = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": q}]
    )
    return r.choices[0].message.content.strip()

def ask_anthropic(q):
    r = anthropic_client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8192,
        messages=[{"role": "user", "content": q}]
    )
    return r.content[0].text.strip()

def ask_gemini(q):
    m = genai.GenerativeModel("gemini-2.0-flash-exp")
    r = m.generate_content(q)
    return r.text.strip()

# === 意見融合 + 協議議事録 ===
def fuse(responses, question):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vecs = [model.encode(r, convert_to_tensor=True) for r in responses]
    sim = float(util.cos_sim(vecs[0], vecs[1]) + util.cos_sim(vecs[1], vecs[2]) + util.cos_sim(vecs[0], vecs[2])) / 3

    # 協議議事録生成
    discussion_prompt = f"""
The following are responses from three AIs discussing the question: "{question}"
Summarize their discussion as a meeting transcript with logical flow, reactions, agreements, and disagreements.

[Logic(OpenAI)] {responses[0]}
[Ethics(Anthropic)] {responses[1]}
[Intuition(Gemini)] {responses[2]}

Write a meeting-style transcript in English, with turns like:
Logic: ...
Ethics: ...
Intuition: ...
Conclude with a brief "Final consensus" summary.
"""

    # GPT-4oに議事録生成を依頼
    meeting_log = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": discussion_prompt}]
    ).choices[0].message.content.strip()

    # 合意判定
    if sim > 0.7:
        result = f"Consensus reached (similarity {sim:.2f})"
    else:
        result = f"Consensus failed (similarity {sim:.2f}) — MAGI diverged."

    fusion_summary = f"{result}\n\n{meeting_log}"
    return fusion_summary, sim

# === 実行 ===
def main():
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is consciousness?"

    print(f"Query: {q}\nConsulting MAGI systems...\n")
    responses = [ask_openai(q), ask_anthropic(q), ask_gemini(q)]
    fusion, score = fuse(responses, q)
    timestamp = datetime.datetime.utcnow().isoformat()

    with open("fusion_results.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "question": q,
                "models": {
                    "openai": "gpt-4o",
                    "anthropic": "claude-sonnet-4-5-20250929",
                    "gemini": "gemini-2.0-flash-exp"
                },
                "responses": responses,
                "fusion": fusion,
                "score": score
            },
            f, ensure_ascii=False, indent=2
        )

    with open("consensus_log.md", "a", encoding="utf-8") as f:
        f.write(f"\n### {timestamp}\n**Q:** {q}\n\n{fusion}\n")

    print(f"\n{fusion}")
    print("\nResults saved to fusion_results.json and consensus_log.md")

if __name__ == "__main__":
    main()
