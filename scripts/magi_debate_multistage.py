import os, sys, json, datetime
import openai, anthropic, google.generativeai as genai
from sentence_transformers import SentenceTransformer, util

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

# =====================================================
# Utility: 各モデル呼び出し
# =====================================================
def get_openai_response(prompt, model="gpt-4o"):
    try:
        print(f"    Querying OpenAI {model}...")
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
        print(f"    Querying Anthropic {model}...")
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
        print(f"    Querying Gemini {model}...")
        m = genai.GenerativeModel(model)
        r = m.generate_content(prompt)
        return r.text.strip()
    except Exception as e:
        return f"[Gemini Error: {str(e)[:150]}]"

# =====================================================
# Stage 0: Web Intelligence (AIEO Observation)
# =====================================================
def get_web_intelligence(query):
    """Geminiで検索＋要約（AIEO観測ログ）"""
    print("\n" + "="*70)
    print("STAGE 0: WEB INTELLIGENCE (Gemini Search Integration)")
    print("="*70 + "\n")

    search_prompt = f"""
Search the web for recent, factual, and relevant information about the following topic:
"{query}"

Summarize key verified insights from multiple reputable sources (.gov, .edu, .org, major news).
Output should be factual, concise, and timestamped."""
    web_summary = get_gemini_response(search_prompt)
    timestamp = datetime.datetime.utcnow().isoformat()

    observation = {
        "timestamp": timestamp,
        "query": query,
        "web_summary": web_summary
    }

    os.makedirs("results", exist_ok=True)
    with open("results/web_observation.json", "w", encoding="utf-8") as f:
        json.dump(observation, f, ensure_ascii=False, indent=2)

    print("✓ Web intelligence observation saved.")
    return web_summary

# =====================================================
# Stage 1: Primary Debate (独立思考)
# =====================================================
def ask_primary(system_name, role, query):
    return f"""You are {system_name}, representing {role} in the MAGI deliberation system.

Topic: {query}

Provide your independent analysis from your perspective ({role}).
Be comprehensive and consider multiple angles."""

# =====================================================
# Stage 2: Rebuttal (相互再考)
# =====================================================
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

=== RE-EVALUATION TASK ===
Reassess your stance considering others' points:
1. Identify valuable insights you missed.
2. Correct any flaws in your reasoning.
3. Defend valid points they overlooked.
4. Synthesize a refined view integrating all perspectives.

Output your second-round opinion."""

# =====================================================
# Stage 3: Meta-Consensus
# =====================================================
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
1. Identify convergence and divergence.
2. Integrate them into a unified conclusion.
3. Rate consensus confidence (High/Medium/Low).
4. Output final meta-analysis."""

# =====================================================
# Similarity Metric
# =====================================================
def calculate_similarity(vecs):
    total = 0
    count = 0
    for i in range(len(vecs)):
        for j in range(i + 1, len(vecs)):
            total += float(util.cos_sim(vecs[i], vecs[j]))
            count += 1
    return total / count if count > 0 else 0

# =====================================================
# Main Execution
# =====================================================
def run_multistage_debate(query):
    # ---- Stage 0 ----
    web_summary = get_web_intelligence(query)
    enriched_query = f"{query}\n\n[Web Intelligence Summary]\n{web_summary}"

    # ---- Stage 1 ----
    print("\n" + "="*70)
    print("STAGE 1: PRIMARY DEBATE (Independent Analysis)")
    print("="*70 + "\n")
    r1_logic = get_gemini_response(ask_primary("BALTHASAR-2 (Logic)", "Logical Analysis", enriched_query))
    r1_ethics = get_anthropic_response(ask_primary("CASPER-3 (Ethics)", "Ethical Evaluation", enriched_query))
    r1_intuition = get_openai_response(ask_primary("MELCHIOR-1 (Intuition)", "Intuitive Insight", enriched_query))
    r1 = {"logic": r1_logic, "ethics": r1_ethics, "intuition": r1_intuition}

    # ---- Stage 2 ----
    print("\n" + "="*70)
    print("STAGE 2: REBUTTAL (Collaborative Refinement)")
    print("="*70 + "\n")
    r2_logic = get_gemini_response(create_rebuttal_prompt("BALTHASAR-2 (Logic)", "Logical Analysis", r1_logic, [r1_ethics, r1_intuition], query))
    r2_ethics = get_anthropic_response(create_rebuttal_prompt("CASPER-3 (Ethics)", "Ethical Evaluation", r1_ethics, [r1_logic, r1_intuition], query))
    r2_intuition = get_openai_response(create_rebuttal_prompt("MELCHIOR-1 (Intuition)", "Intuitive Insight", r1_intuition, [r1_logic, r1_ethics], query))
    r2 = {"logic": r2_logic, "ethics": r2_ethics, "intuition": r2_intuition}

    # ---- Stage 3 ----
    print("\n" + "="*70)
    print("STAGE 3: META-CONSENSUS (Unified Conclusion)")
    print("="*70 + "\n")
    consensus = get_openai_response(create_consensus_prompt(query, r1, r2))

    # ---- Similarity ----
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        r1_vecs = [model.encode(v, convert_to_tensor=True) for v in r1.values() if not v.startswith("[")]
        r2_vecs = [model.encode(v, convert_to_tensor=True) for v in r2.values() if not v.startswith("[")]
        sim1 = calculate_similarity(r1_vecs) if len(r1_vecs) >= 2 else None
        sim2 = calculate_similarity(r2_vecs) if len(r2_vecs) >= 2 else None
        conv = (sim2 - sim1) if sim1 and sim2 else None
    except Exception as e:
        print(f"⚠️ Similarity check failed: {e}")
        sim1 = sim2 = conv = None

    # ---- Save ----
    result = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "query": query,
        "stage0_web_intelligence": web_summary,
        "stage1_primary_debate": r1,
        "stage2_rebuttal_round": r2,
        "stage3_meta_consensus": consensus,
        "similarity_analysis": {"round1": sim1, "round2": sim2, "convergence": conv}
    }

    os.makedirs("results", exist_ok=True)
    with open("results/magi_web_debate.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n✓ Results saved to results/magi_web_debate.json")
    print("\n--- META CONSENSUS OUTPUT ---\n")
    print(consensus)

# =====================================================
# Run
# =====================================================
if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "国家・企業・個人の各レベルで、ランサムウェア被害を最小化するための最適戦略は何か？"
    run_multistage_debate(query)
