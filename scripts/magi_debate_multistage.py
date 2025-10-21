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
    
    # Anthropicはオプショナルとして扱う
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

def ask_openai(q):
    try:
        print("    Querying OpenAI GPT-4o (Intuition)...")
        r = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": q}],
            timeout=30
        )
        response = r.choices[0].message.content.strip()
        print("    ✓ OpenAI response received")
        return response
    except Exception as e:
        print(f"    ✗ OpenAI failed: {str(e)[:100]}")
        return f"[OpenAI Error: {str(e)[:200]}]"

def ask_anthropic(q):
    if not anthropic_client:
        return "[Anthropic Error: API client not initialized]"
    
    try:
        print("    Querying Anthropic Claude Sonnet 4.5...")
        r = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            messages=[{"role": "user", "content": q}],
            timeout=30
        )
        response = r.content[0].text.strip()
        print("    ✓ Anthropic response received")
        return response
    except anthropic.BadRequestError as e:
        error_msg = str(e)
        if "credit balance" in error_msg.lower():
            print("    ✗ Anthropic failed: Credit balance too low")
            return "[Anthropic Error: Credit balance too low - API access unavailable]"
        print(f"    ✗ Anthropic failed: {error_msg[:100]}")
        return f"[Anthropic Error: {error_msg[:200]}]"
    except Exception as e:
        print(f"    ✗ Anthropic failed: {str(e)[:100]}")
        return f"[Anthropic Error: {str(e)[:200]}]"

def ask_gemini(q):
    try:
        print("    Querying Google Gemini 2.0 (Logic)...")
        m = genai.GenerativeModel("gemini-2.0-flash-exp")
        r = m.generate_content(q)
        response = r.text.strip()
        print("    ✓ Gemini response received")
        return response
    except Exception as e:
        print(f"    ✗ Gemini failed: {str(e)[:100]}")
        return f"[Gemini Error: {str(e)[:200]}]"

def fuse(responses):
    # エラーレスポンスを除外して有効なレスポンスのみ取得
    valid_responses = []
    valid_indices = []
    names = ["Logic(Gemini)", "Ethics(Anthropic)", "Intuition(OpenAI)"]
    
    for i, r in enumerate(responses):
        if not (r.startswith("[") and "Error" in r):
            valid_responses.append(r)
            valid_indices.append(i)
    
    error_count = len(responses) - len(valid_responses)
    if error_count > 0:
        print(f"\n⚠️  {error_count} MAGI system(s) unavailable")
    
    if len(valid_responses) == 0:
        return "All MAGI systems failed. No consensus possible.", 0.0
    
    if len(valid_responses) == 1:
        print(f"\n✓ Only {names[valid_indices[0]]} available")
        return f"Single system response from {names[valid_indices[0]]}:\n\n{valid_responses[0]}", 1.0
    
    # 類似度計算
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        if len(valid_responses) == 3:
            vecs = [model.encode(r, convert_to_tensor=True) for r in valid_responses]
            sim = float(
                util.cos_sim(vecs[0], vecs[1]) + 
                util.cos_sim(vecs[1], vecs[2]) + 
                util.cos_sim(vecs[0], vecs[2])
            ) / 3
        else:  # len(valid_responses) == 2
            vecs = [model.encode(r, convert_to_tensor=True) for r in valid_responses]
            sim = float(util.cos_sim(vecs[0], vecs[1]))
    except Exception as e:
        print(f"⚠️  Similarity calculation failed: {str(e)[:100]}")
        print("Using fallback consensus detection...")
        # フォールバック: 簡易的な類似度（文字列長の比較）
        sim = 0.5  # デフォルト値
    
    # 結果の整形
    combined_parts = []
    for i, (name, response) in enumerate(zip(names, responses)):
        status = "✓" if i in valid_indices else "✗"
        combined_parts.append(f"[{status} {name}]\n{response}")
    
    combined = "\n\n---\n\n".join(combined_parts)
    
    if sim > 0.7:
        result = f"✓ Consensus reached (similarity: {sim:.2f})\n{len(valid_responses)}/3 systems operational\n\n{combined}"
    else:
        result = f"✗ Consensus failed (similarity: {sim:.2f})\nMAGI systems diverged\n{len(valid_responses)}/3 systems operational\n\n{combined}"
    
    return result, sim

def main():
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is consciousness?"
    
    print(f"="*60)
    print(f"MAGI SYSTEM - Multi-AI Consensus Analysis")
    print(f"="*60)
    print(f"\nQuery: {q}\n")
    print("Consulting MAGI systems...\n")
    
    # 各AIに順次問い合わせ
    openai_response = ask_openai(q)
    anthropic_response = ask_anthropic(q)
    gemini_response = ask_gemini(q)
    
    responses = [openai_response, anthropic_response, gemini_response]
    
    print("\n" + "="*60)
    print("Analyzing consensus...")
    print("="*60)
    
    fusion, score = fuse(responses)
    
    timestamp = datetime.datetime.utcnow().isoformat()
    
    result_data = {
        "timestamp": timestamp, 
        "question": q, 
        "models": {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-5-20250929",
            "gemini": "gemini-2.0-flash-exp"
        },
        "responses": {
            "gemini": gemini_response,
            "anthropic": anthropic_response,
            "openai": openai_response
        },
        "fusion": fusion, 
        "score": score
    }
    
    # 結果を保存
    os.makedirs("results", exist_ok=True)
    
    with open("results/fusion_results.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    with open("results/consensus_log.md", "a", encoding="utf-8") as f:
        f.write(f"\n\n## {timestamp}\n\n**Query:** {q}\n\n{fusion}\n\n---\n")
    
    print(f"\n{fusion}")
    print(f"\n" + "="*60)
    print(f"Results saved to:")
    print(f"  - results/fusion_results.json")
    print(f"  - results/consensus_log.md")
    print(f"="*60)

if __name__ == "__main__":
    main()
