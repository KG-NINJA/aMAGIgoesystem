#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, datetime
import openai, anthropic, google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
from pathlib import Path

# =====================================================
# APIキー設定
# =====================================================
openai.api_key = os.getenv("OPENAI_API_KEY", "").strip()
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()

def validate_api_keys():
    errors = []
    if not openai.api_key:
        errors.append("OPENAI_API_KEY is not set")
    if not google_api_key:
        errors.append("GOOGLE_API_KEY is not set")
    if not anthropic_api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY is not set - Claude will be unavailable")
    if errors:
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

validate_api_keys()
anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
genai.configure(api_key=google_api_key)

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)
timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

# =====================================================
# Utility: 各モデル呼び出し
# =====================================================
def get_openai_response(prompt, model="gpt-4o"):
    try:
        r = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=90
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI Error: {str(e)[:150]}]"

def get_anthropic_response(prompt, model="claude-sonnet-4-5-20250929"):
    if not anthropic_client:
        return "[Anthropic Error: API client not initialized]"
    try:
        r = anthropic_client.messages.create(
            model=model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
            timeout=90
        )
        return r.content[0].text.strip()
    except Exception as e:
        return f"[Anthropic Error: {str(e)[:150]}]"

def get_gemini_response(prompt, model="gemini-2.0-flash-exp"):
    try:
        m = genai.GenerativeModel(model)
        r = m.generate_content(prompt)
        return r.text.strip()
    except Exception as e:
        return f"[Gemini Error: {str(e)[:150]}]"

# =====================================================
# Stage 0: Web Intelligence (AIEO Observation)
# =====================================================
def get_web_intelligence(query):
    search_prompt = f"""
Search the web for recent, factual, and relevant information about the following topic:
"{query}"
Summarize key verified insights from multiple reputable sources (.gov, .edu, .org, major news).
Output should be factual, concise, and timestamped."""
    web_summary = get_gemini_response(search_prompt)
    observation = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "query": query,
        "web_summary": web_summary
    }
    with open(RESULTS_DIR / "web_observation.json", "w", encoding="utf-8") as f:
        json.dump(observation, f, ensure_ascii=False, indent=2)
    return web_summary

# =====================================================
# Debate Prompt Templates
# =====================================================
def ask_primary(system_name, role, query):
    return f"""You are {system_name}, representing {role} in the MAGI deliberation system.

Topic: {query}

Provide your independent analysis from your perspective ({role})."""

def create_rebuttal_prompt(system_name, role, original_response, other_responses, query):
    others = {
        "BALTHASAR-2 (Logic)": ["CASPER-3 (Ethics)", "MELCHIOR-1 (Intuition)"],
        "CASPER-3 (Ethics)": ["BALTHASAR-2 (Logic)", "MELCHIOR-1 (Intuition)"],
        "MELCHIOR-1 (Intuition)": ["BALTHASAR-2 (Logic)", "CASPER-3 (Ethics)"]
    }[system_name]
    return f"""You are {system_name}, representing {role} in the MAGI system.

Original Query: {query}

=== PRIMARY DEBATE RESULTS ===
Your response:
{original_response}

{others[0]}'s response:
{other_responses[0]}

{others[1]}'s response:
{other_responses[1]}

=== TASK ===
Reassess your stance considering others' points and synthesize a refined view."""

def create_consensus_prompt(query, r1, r2):
    return f"""You are the Meta-Consensus AI analyzing outputs from Logic, Ethics, and Intuition.

Query: {query}

=== ROUND 1 ===
Logic: {r1['logic']}
Ethics: {r1['ethics']}
Intuition: {r1['intuition']}

=== ROUND 2 ===
Logic: {r2['logic']}
Ethics: {r2['ethics']}
Intuition: {r2['intuition']}

=== TASK ===
Integrate all perspectives into a unified, balanced conclusion.
Rate confidence (High/Medium/Low)."""

# =====================================================
# Utility: Similarity
# =====================================================
def calculate_similarity(vecs):
    total = 0
    count = 0
    for i in range(len(vecs)):
        for j in range(i + 1, len(vecs)):
            total += float(util.cos_sim(vecs[i], vecs[j]))
            count += 1
    return total / count if count else 0

# =====================================================
# Markdown Logger
# =====================================================
def append_markdown_log(query, r1, r2, consensus, web_summary):
    md_path = RESULTS_DIR / "multistage_log.md"
    with open(md_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n## {timestamp}\n\n")
        f.write(f"**Query:** {query}\n\n")
        f.write("### Stage 0: Web Observation\n\n")
        f.write(web_summary[:1000] + "\n\n")
        f.write("### Stage 1: Primary Debate\n\n")
        for k, v in r1.items():
            f.write(f"**{k.upper()}**\n{v[:500]}...\n\n")
        f.write("### Stage 2: Rebuttal\n\n")
        for k, v in r2.items():
            f.write(f"**{k.upper()}**\n{v[:500]}...\n\n")
        f.write("### Stage 3: Meta-Consensus\n\n")
        f.write(consensus + "\n\n---\n")

# =====================================================
# Main Execution
# =====================================================
def run_multistage_debate(query):
    print(f"\n🧠 Running MAGI Debate for query: {query}\n")

    # ---- Stage 0 ----
    web_summary = get_web_intelligence(query)
    enriched_query = f"{query}\n\n[Web Intelligence Summary]\n{web_summary}"

    # ---- Stage 1 ----
    r1 = {
        "logic": get_gemini_response(ask_primary("BALTHASAR-2 (Logic)", "Logical Analysis", enriched_query)),
        "ethics": get_anthropic_response(ask_primary("CASPER-3 (Ethics)", "Ethical Evaluation", enriched_query)),
        "intuition": get_openai_response(ask_primary("MELCHIOR-1 (Intuition)", "Intuitive Insight", enriched_query))
    }

    # ---- Stage 2 ----
    r2 = {
        "logic": get_gemini_response(create_rebuttal_prompt("BALTHASAR-2 (Logic)", "Logical Analysis", r1["logic"], [r1["ethics"], r1["intuition"]], query)),
        "ethics": get_anthropic_response(create_rebuttal_prompt("CASPER-3 (Ethics)", "Ethical Evaluation", r1["ethics"], [r1["logic"], r1["intuition"]], query)),
        "intuition": get_openai_response(create_rebuttal_prompt("MELCHIOR-1 (Intuition)", "Intuitive Insight", r1["intuition"], [r1["logic"], r1["ethics"]], query))
    }

    # ---- Stage 3 ----
    consensus = get_openai_response(create_consensus_prompt(query, r1, r2))

    # ---- Similarity ----
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        v1 = [model.encode(v, convert_to_tensor=True) for v in r1.values() if not v.startswith("[")]
        v2 = [model.encode(v, convert_to_tensor=True) for v in r2.values() if not v.startswith("[")]
        sim1 = calculate_similarity(v1) if len(v1) >= 2 else None
        sim2 = calculate_similarity(v2) if len(v2) >= 2 else None
        conv = (sim2 - sim1) if sim1 and sim2 else None
    except Exception as e:
        sim1 = sim2 = conv = None
        print(f"⚠️ Similarity calc failed: {e}")

    # ---- Save JSON ----
    result = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "query": query,
        "stage0_web_intelligence": web_summary,
        "stage1_primary_debate": r1,
        "stage2_rebuttal_round": r2,
        "stage3_meta_consensus": consensus,
        "similarity_analysis": {"round1": sim1, "round2": sim2, "convergence": conv}
    }
    with open(RESULTS_DIR / "magi_web_debate.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # ---- Markdown Log ----
    append_markdown_log(query, r1, r2, consensus, web_summary)

    print("\n✅ Debate complete. Logs written to results/.")
    print("\n--- META CONSENSUS ---\n")
    print(consensus)

# =====================================================
# Run
# =====================================================
if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "ランサムウェアとAWS障害の相互影響および国家・企業・個人レベルの最適防御策"
    run_multistage_debate(query)
