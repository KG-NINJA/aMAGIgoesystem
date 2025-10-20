# scripts/magi_debate_multistage.py
import os, sys, json, requests
from datetime import datetime
import openai, anthropic, google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
from bs4 import BeautifulSoup

# =====================================================
# APIキー設定
# =====================================================
openai.api_key = os.getenv("OPENAI_API_KEY", "").strip()
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
google_search_key = os.getenv("GOOGLE_SEARCH_API_KEY", "").strip()  # ← Google検索用
google_cx = os.getenv("GOOGLE_CX", "").strip()
gemini_key = os.getenv("GEMINI_API_KEY", "").strip()  # ← Gemini用

def validate_api_keys():
    errors = []
    if not openai.api_key:
        errors.append("OPENAI_API_KEY is not set")
    if not google_search_key:
        errors.append("GOOGLE_SEARCH_API_KEY is not set (Custom Search)")
    if not google_cx:
        errors.append("GOOGLE_CX is not set")
    if not gemini_key:
        print("⚠️  Warning: GEMINI_API_KEY is not set - Gemini unavailable")
    if not anthropic_api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY is not set - Claude unavailable")
    if errors:
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

validate_api_keys()
anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
genai.configure(api_key=gemini_key)

# =====================================================
# Google Custom Search
# =====================================================
def google_search(query, num=6, lang="lang_en"):
    """Google Custom Search JSON APIで検索"""
    if not google_search_key or not google_cx:
        raise EnvironmentError("GOOGLE_SEARCH_API_KEY または GOOGLE_CX が設定されていません。")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": google_search_key, "cx": google_cx, "q": query, "lr": lang, "num": num}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        raise RuntimeError(f"Google Search API Error {r.status_code}: {r.text}")
    return r.json().get("items", [])

def clean_text(html):
    return BeautifulSoup(html, "html.parser").get_text()

# =====================================================
# 各モデル呼び出し
# =====================================================
def get_openai_response(prompt, model="gpt-4o"):
    try:
        r = openai.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], timeout=90)
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI Error: {str(e)[:150]}]"

def get_anthropic_response(prompt, model="claude-sonnet-4-5-20250929"):
    if not anthropic_client:
        return "[Anthropic Error: client not initialized]"
    try:
        r = anthropic_client.messages.create(model=model, max_tokens=8192, messages=[{"role": "user", "content": prompt}], timeout=90)
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
# Stage 0: Web Intelligence (Google検索)
# =====================================================
def get_web_intelligence(query):
    print("\n" + "="*70)
    print("STAGE 0: WEB INTELLIGENCE (Google Search Integration)")
    print("="*70 + "\n")

    combined = []
    for lang in ["lang_ja", "lang_en"]:
        try:
            items = google_search(query, num=5, lang=lang)
            for it in items:
                snippet = clean_text(it.get("snippet", ""))
                title = clean_text(it.get("title", ""))
                link = it.get("link", "")
                combined.append(f"[{lang.upper()}] {title}\n{snippet}\nURL: {link}")
        except Exception as e:
            combined.append(f"[{lang.upper()} ERROR: {e}]")

    summary_prompt = f"""
Summarize the following search results about the topic below using factual, verifiable insights only.
Topic: {query}

Results:
{json.dumps(combined, ensure_ascii=False, indent=2)}

Output concise bullet points (JP+EN mix ok). Add publication date and source name if found.
"""
    web_summary = get_gemini_response(summary_prompt)
    timestamp = datetime.utcnow().isoformat()

    obs = {"timestamp": timestamp, "query": query, "web_summary": web_summary}
    os.makedirs("results", exist_ok=True)
    with open("results/web_observation.json", "w", encoding="utf-8") as f:
        json.dump(obs, f, ensure_ascii=False, indent=2)
    print("✓ Web intelligence observation saved.")
    return web_summary

# =====================================================
# Debate Prompts
# =====================================================
def ask_primary(name, role, query):
    return f"""You are {name}, representing {role} in the MAGI system.

Topic: {query}

Provide your independent analysis from your perspective ({role}).
Be comprehensive and multi-angled."""

def create_rebuttal_prompt(name, role, original, others, query):
    o = {"BALTHASAR-2 (Logic)": ["CASPER-3 (Ethics)", "MELCHIOR-1 (Intuition)"],
         "CASPER-3 (Ethics)": ["BALTHASAR-2 (Logic)", "MELCHIOR-1 (Intuition)"],
         "MELCHIOR-1 (Intuition)": ["BALTHASAR-2 (Logic)", "CASPER-3 (Ethics)"]}[name]
    return f"""You are {name}, representing {role}.
Query: {query}

=== Round 1 ===
Your response:
{original}

{o[0]}'s response:
{others[0]}

{o[1]}'s response:
{others[1]}

Now re-evaluate your stance:
1. Identify valuable insights you missed
2. Correct flaws
3. Defend valid points others missed
4. Output your refined stance."""

def create_consensus_prompt(query, r1, r2):
    return f"""You are the Meta-Consensus AI analyzing Logic, Ethics, and Intuition.

Query: {query}

=== Round 1 ===
Logic: {r1['logic']}
Ethics: {r1['ethics']}
Intuition: {r1['intuition']}

=== Round 2 ===
Logic: {r2['logic']}
Ethics: {r2['ethics']}
Intuition: {r2['intuition']}

=== TASK ===
1. Identify convergence and divergence
2. Integrate all into a unified synthesis
3. Rate confidence (High/Medium/Low)
4. Provide a clear final consensus."""

# =====================================================
# Similarity Metric
# =====================================================
def calculate_similarity(vecs):
    total = count = 0
    for i in range(len(vecs)):
        for j in range(i + 1, len(vecs)):
            total += float(util.cos_sim(vecs[i], vecs[j]))
            count += 1
    return total / count if count else 0

# =====================================================
# メイン実行
# =====================================================
def run_multistage_debate(query):
    print("="*70)
    print("🧠 MAGI MULTI-STAGE DEBATE SYSTEM")
    print("="*70)
    print(f"Query: {query}\n")

    # ---- Stage 0 ----
    web_summary = get_web_intelligence(query)
    enriched_query = f"{query}\n\n[Web Intelligence Summary]\n{web_summary}"

    # ---- Stage 1 ----
    print("\n" + "="*70)
    print("STAGE 1: PRIMARY DEBATE")
    print("="*70)
    r1_logic = get_gemini_response(ask_primary("BALTHASAR-2 (Logic)", "Logical Analysis", enriched_query))
    r1_ethics = get_anthropic_response(ask_primary("CASPER-3 (Ethics)", "Ethical Evaluation", enriched_query))
    r1_intuition = get_openai_response(ask_primary("MELCHIOR-1 (Intuition)", "Intuitive Insight", enriched_query))
    r1 = {"logic": r1_logic, "ethics": r1_ethics, "intuition": r1_intuition}

    # ---- Stage 2 ----
    print("\n" + "="*70)
    print("STAGE 2: REBUTTAL ROUND")
    print("="*70)
    r2_logic = get_gemini_response(create_rebuttal_prompt("BALTHASAR-2 (Logic)", "Logical Analysis", r1_logic, [r1_ethics, r1_intuition], query))
    r2_ethics = get_anthropic_response(create_rebuttal_prompt("CASPER-3 (Ethics)", "Ethical Evaluation", r1_ethics, [r1_logic, r1_intuition], query))
    r2_intuition = get_openai_response(create_rebuttal_prompt("MELCHIOR-1 (Intuition)", "Intuitive Insight", r1_intuition, [r1_logic, r1_ethics], query))
    r2 = {"logic": r2_logic, "ethics": r2_ethics, "intuition": r2_intuition}

    # ---- Stage 3 ----
    print("\n" + "="*70)
    print("STAGE 3: META-CONSENSUS")
    print("="*70)
    consensus = get_openai_response(create_consensus_prompt(query, r1, r2))

    # ---- 類似度 ----
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

    # ---- 保存 ----
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "stage0_web_intelligence": web_summary,
        "stage1_primary_debate": r1,
        "stage2_rebuttal_round": r2,
        "stage3_meta_consensus": consensus,
        "similarity_analysis": {"round1": sim1, "round2": sim2, "convergence": conv},
    }
    os.makedirs("results", exist_ok=True)
    with open("results/magi_web_debate.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n✓ Results saved to results/magi_web_debate.json\n")
    print("--- META CONSENSUS OUTPUT ---\n")
    print(consensus)

# =====================================================
# 実行エントリポイント
# =====================================================
if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "ランサムウェアとAWS障害の関連を分析せよ"
    run_multistage_debate(query)
