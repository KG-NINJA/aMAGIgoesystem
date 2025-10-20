import os, sys, json, datetime
import openai, anthropic, google.generativeai as genai
from sentence_transformers import SentenceTransformer, util

# APIキーを取得し、前後の空白と改行を削除
openai.api_key = os.getenv("OPENAI_API_KEY", "").strip()
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()

# APIキーの検証
def validate_api_keys():
    errors = []
    if not openai.api_key:
        errors.append("OPENAI_API_KEY is not set")
    if not google_api_key:
        errors.append("GOOGLE_API_KEY is not set")
    
    if not anthropic_api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY is not set - Claude will be unavailable")
    
    if errors:
        print("ERROR: Missing required API keys:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

validate_api_keys()

# Anthropic clientは条件付きで初期化
anthropic_client = None
if anthropic_api_key:
    try:
        anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize Anthropic client: {e}")

genai.configure(api_key=google_api_key)

# =====================================================
# Stage 0: Web Intelligence (証拠収集)
# =====================================================

def get_web_intelligence(query, target_date="2025-10-20"):
    """Stage 0: Web検索による証拠収集"""
    search_prompt = f"""
You are a cautious web analyst. DO NOT speculate.

Task: Summarize **published** information about:
"{query}"

Cut-off date (UTC): <= {target_date}
Languages: include **Japanese** and **English**
Sources (must be verifiable URLs): at least **≥3 JP** and **≥3 EN** from:
  JP: ipa.go.jp, jpcert.or.jp, nisc.go.jp, soumu.go.jp, metro.tokyo.lg.jp, *.ac.jp, major JP media
  EN: cisa.gov, nist.gov, enisa.europa.eu, europol.europa.eu, who.int, cloudsecurityalliance.org, aws.amazon.com/security/blog, major media

Rules:
- Every claim needs an inline citation: [LANG][YYYY-MM-DD] Publisher — Title — URL
- If evidence is missing, write exactly: INSUFFICIENT EVIDENCE.
- No future tense or predictions. No invented URLs. Only publicly published pages.

Output:
## Key Findings
- JP/EN mixed bullets with inline citations

## Source List
- [JP] YYYY-MM-DD Publisher — Title — URL
- [EN] YYYY-MM-DD Publisher — Title — URL
"""
    
    return get_openai_response(search_prompt, model="gpt-4o")

# =====================================================
# Stage 1: Primary Debate (独立思考)
# =====================================================

def ask_primary(system_name, role, query_with_web):
    """第一ラウンド：各AIが独立に回答（証拠ベース）"""
    prompt = f"""You are {system_name} ({role}).
Use ONLY claims that appear explicitly in [Web Intelligence Summary] with their citations.
If a needed claim is missing → write INSUFFICIENT EVIDENCE. No new facts. No predictions.

{query_with_web}

Deliver your analysis from your role, grounding each claim with a cited bullet from Stage 0."""
    
    return prompt

def get_openai_response(prompt, model="gpt-4o"):
    try:
        print(f"    Querying OpenAI {model}...")
        r = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=60
        )
        response = r.choices[0].message.content.strip()
        print("    ✓ OpenAI response received")
        return response
    except Exception as e:
        print(f"    ✗ OpenAI failed: {str(e)[:100]}")
        return f"[OpenAI Error: {str(e)[:200]}]"

def get_anthropic_response(prompt, model="claude-sonnet-4-5-20250929"):
    if not anthropic_client:
        return "[Anthropic Error: API client not initialized]"
    
    try:
        print(f"    Querying Anthropic {model}...")
        r = anthropic_client.messages.create(
            model=model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
            timeout=60
        )
        response = r.content[0].text.strip()
        print("    ✓ Anthropic response received")
        return response
    except Exception as e:
        print(f"    ✗ Anthropic failed: {str(e)[:100]}")
        return f"[Anthropic Error: {str(e)[:200]}]"

def get_gemini_response(prompt, model="gemini-2.0-flash-exp"):
    try:
        print(f"    Querying Google {model}...")
        m = genai.GenerativeModel(model)
        r = m.generate_content(
            prompt,
            generation_config={"max_output_tokens": 2048, "temperature": 0.2}
        )
        text = (r.text or "").strip()
        if not text:
            # one quick retry
            print("    Retrying Gemini (empty response)...")
            r = m.generate_content(
                prompt,
                generation_config={"max_output_tokens": 2048, "temperature": 0.2}
            )
            text = (r.text or "").strip()
        response = text if text else "[Gemini Error: empty response]"
        if not response.startswith("["):
            print("    ✓ Gemini response received")
        else:
            print(f"    ✗ Gemini: {response}")
        return response
    except Exception as e:
        print(f"    ✗ Gemini failed: {str(e)[:100]}")
        return f"[Gemini Error: {str(e)[:150]}]"

# =====================================================
# Stage 2: Rebuttal Round (協調的再思考)
# =====================================================

def create_rebuttal_prompt(system_name, role, original_response, other_responses, query):
    """反論ラウンド用のプロンプト生成（証拠制約付き）"""
    other_names = {
        "BALTHASAR-2 (Logic)": ["CASPER-3 (Ethics)", "MELCHIOR-1 (Intuition)"],
        "CASPER-3 (Ethics)": ["BALTHASAR-2 (Logic)", "MELCHIOR-1 (Intuition)"],
        "MELCHIOR-1 (Intuition)": ["BALTHASAR-2 (Logic)", "CASPER-3 (Ethics)"]
    }
    
    others = other_names.get(system_name, [])
    
    prompt = f"""You are {system_name} ({role}). Evidence constraint unchanged.
Use ONLY Stage 0 citations already surfaced in Round 1.
If a claim lacks a citation → mark as INSUFFICIENT EVIDENCE and exclude it.

Original Query: {query}

=== YOUR ROUND 1 RESPONSE ===
{original_response}

=== {others[0] if len(others) > 0 else "SYSTEM 2"} RESPONSE ===
{other_responses[0] if len(other_responses) > 0 else "[Not available]"}

=== {others[1] if len(others) > 1 else "SYSTEM 3"} RESPONSE ===
{other_responses[1] if len(other_responses) > 1 else "[Not available]"}

=== RE-EVALUATION INSTRUCTIONS ===
1) Adopt valid evidence-backed points from others
2) Remove unsupported claims from your position
3) Synthesize corrected position with citations
4) No predictions or unsourced claims

Output your refined, evidence-grounded second opinion."""

    return prompt

# =====================================================
# Stage 3: Meta-Consensus (統合判断)
# =====================================================

def create_consensus_prompt(query, round1_responses, round2_responses):
    """メタAIによる最終統合"""
    prompt = f"""You are the Meta-Consensus System analyzing outputs from three AI perspectives.

Original Query: {query}

=== ROUND 1: PRIMARY DEBATE ===
Logic (BALTHASAR-2): {round1_responses['logic']}

Ethics (CASPER-3): {round1_responses['ethics']}

Intuition (MELCHIOR-1): {round1_responses['intuition']}

=== ROUND 2: REBUTTAL & REFINEMENT ===
Logic (BALTHASAR-2): {round2_responses['logic']}

Ethics (CASPER-3): {round2_responses['ethics']}

Intuition (MELCHIOR-1): {round2_responses['intuition']}

=== META-CONSENSUS TASK ===
1. Identify points of convergence across all perspectives
2. Highlight valuable divergences that enrich understanding
3. Synthesize a balanced conclusion that honors all three viewpoints
4. Indicate confidence level (High/Medium/Low) based on consensus strength

Provide a comprehensive meta-analysis and final recommendation."""

    return prompt

# =====================================================
# Main Execution
# =====================================================

def run_multistage_debate(query):
    print("="*70)
    print("MAGI MULTI-STAGE DELIBERATION SYSTEM")
    print("="*70)
    print(f"\nQuery: {query}\n")
    
    # ===== STAGE 0: WEB INTELLIGENCE =====
    print("\n" + "="*70)
    print("STAGE 0: WEB INTELLIGENCE (Evidence Collection)")
    print("="*70 + "\n")
    
    web_summary = get_web_intelligence(query, target_date="2025-10-20")
    
    print("✓ Web intelligence collected")
    print(f"Summary length: {len(web_summary)} chars\n")
    
    # クエリにWeb情報を統合
    query_with_web = f"""Original Query: {query}

=== WEB INTELLIGENCE SUMMARY ===
{web_summary}

=== YOUR TASK ===
Analyze the query using ONLY the evidence provided above.
"""
    
    # ===== STAGE 1: PRIMARY DEBATE =====
    print("\n" + "="*70)
    print("STAGE 1: PRIMARY DEBATE (Independent Perspectives)")
    print("="*70 + "\n")
    
    logic_prompt = ask_primary("BALTHASAR-2", "Logical Analysis", query_with_web)
    ethics_prompt = ask_primary("CASPER-3", "Ethical Evaluation", query_with_web)
    intuition_prompt = ask_primary("MELCHIOR-1", "Intuitive Insight", query_with_web)
    
    round1_logic = get_openai_response(logic_prompt)
    round1_ethics = get_anthropic_response(ethics_prompt)
    round1_intuition = get_gemini_response(intuition_prompt)
    
    round1_responses = {
        "logic": round1_logic,
        "ethics": round1_ethics,
        "intuition": round1_intuition
    }
    
    # ===== STAGE 2: REBUTTAL ROUND =====
    print("\n" + "="*70)
    print("STAGE 2: REBUTTAL ROUND (Collaborative Re-thinking)")
    print("="*70 + "\n")
    
    # Logic re-evaluates
    logic_rebuttal_prompt = create_rebuttal_prompt(
        "BALTHASAR-2 (Logic)", "Logical Analysis",
        round1_logic, [round1_ethics, round1_intuition], query
    )
    round2_logic = get_openai_response(logic_rebuttal_prompt)
    
    # Ethics re-evaluates
    ethics_rebuttal_prompt = create_rebuttal_prompt(
        "CASPER-3 (Ethics)", "Ethical Evaluation",
        round1_ethics, [round1_logic, round1_intuition], query
    )
    round2_ethics = get_anthropic_response(ethics_rebuttal_prompt)
    
    # Intuition re-evaluates
    intuition_rebuttal_prompt = create_rebuttal_prompt(
        "MELCHIOR-1 (Intuition)", "Intuitive Insight",
        round1_intuition, [round1_logic, round1_ethics], query
    )
    round2_intuition = get_gemini_response(intuition_rebuttal_prompt)
    
    round2_responses = {
        "logic": round2_logic,
        "ethics": round2_ethics,
        "intuition": round2_intuition
    }
    
    # ===== STAGE 3: META-CONSENSUS =====
    print("\n" + "="*70)
    print("STAGE 3: META-CONSENSUS (Final Synthesis)")
    print("="*70 + "\n")
    
    consensus_prompt = create_consensus_prompt(query, round1_responses, round2_responses)
    meta_consensus = get_openai_response(consensus_prompt, model="gpt-4o")
    
    # ===== SIMILARITY ANALYSIS =====
    print("\n" + "="*70)
    print("SIMILARITY ANALYSIS")
    print("="*70 + "\n")
    
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Round 1 similarity
        r1_vecs = [model.encode(r, convert_to_tensor=True) for r in round1_responses.values() if not r.startswith("[")]
        if len(r1_vecs) >= 2:
            r1_sim = calculate_similarity(r1_vecs)
            print(f"Round 1 Similarity: {r1_sim:.3f}")
        else:
            r1_sim = None
        
        # Round 2 similarity
        r2_vecs = [model.encode(r, convert_to_tensor=True) for r in round2_responses.values() if not r.startswith("[")]
        if len(r2_vecs) >= 2:
            r2_sim = calculate_similarity(r2_vecs)
            print(f"Round 2 Similarity: {r2_sim:.3f}")
            
            if r1_sim is not None:
                convergence = r2_sim - r1_sim
                print(f"Convergence Rate: {convergence:+.3f} ({'increased' if convergence > 0 else 'decreased'} consensus)")
            else:
                convergence = None
        else:
            r2_sim = None
            convergence = None
            
    except Exception as e:
        print(f"⚠️  Similarity analysis failed: {str(e)[:100]}")
        print("Continuing without similarity metrics...")
        r1_sim = None
        r2_sim = None
        convergence = None
    
    # ===== SAVE RESULTS =====
    timestamp = datetime.datetime.utcnow().isoformat()
    
    result_data = {
        "timestamp": timestamp,
        "query": query,
        "stage0_web_intelligence": web_summary,
        "stage1_primary_debate": round1_responses,
        "stage2_rebuttal_round": round2_responses,
        "stage3_meta_consensus": meta_consensus,
        "similarity_analysis": {
            "round1": r1_sim if r1_sim is not None else "N/A",
            "round2": r2_sim if r2_sim is not None else "N/A",
            "convergence": convergence if convergence is not None else "N/A"
        }
    }
    
    os.makedirs("results", exist_ok=True)
    
    with open("results/multistage_debate.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    with open("results/multistage_log.md", "a", encoding="utf-8") as f:
        f.write(f"\n\n## {timestamp}\n\n")
        f.write(f"**Query:** {query}\n\n")
        f.write(f"### Stage 0: Web Intelligence\n\n")
        f.write(f"{web_summary[:800]}...\n\n")
        f.write(f"### Stage 1: Primary Debate\n\n")
        for name, resp in round1_responses.items():
            f.write(f"**{name.upper()}:**\n{resp[:500]}...\n\n")
        f.write(f"### Stage 2: Rebuttal Round\n\n")
        for name, resp in round2_responses.items():
            f.write(f"**{name.upper()}:**\n{resp[:500]}...\n\n")
        f.write(f"### Stage 3: Meta-Consensus\n\n{meta_consensus}\n\n")
        f.write(f"---\n")
    
    print(f"\n" + "="*70)
    print("META-CONSENSUS OUTPUT")
    print("="*70 + "\n")
    print(meta_consensus)
    print(f"\n" + "="*70)
    print(f"Results saved to:")
    print(f"  - results/multistage_debate.json")
    print(f"  - results/multistage_log.md")
    print("="*70)

def calculate_similarity(vecs):
    """ベクトル間の平均類似度を計算"""
    total = 0
    count = 0
    for i in range(len(vecs)):
        for j in range(i + 1, len(vecs)):
            total += float(util.cos_sim(vecs[i], vecs[j]))
            count += 1
    return total / count if count > 0 else 0

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Should AI systems have rights?"
    run_multistage_debate(query)
