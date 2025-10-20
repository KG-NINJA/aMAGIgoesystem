# ============================================================
# MAGI GOE System — Multi-AI Consensus Framework (Full Version)
# Google Custom Search 対応版
# ============================================================

import os
import json
import datetime
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup

# === Google Custom Search API設定 ===
def google_search(query, num=10, lang="lang_ja"):
    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CX")
    if not api_key or not cx:
        raise EnvironmentError("GOOGLE_API_KEY または GOOGLE_CX が設定されていません。")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": num,
        "lr": lang,
        "safe": "off"
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("items", [])


def fetch_page_excerpt(url, max_chars=500):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text().split())
        return text[:max_chars]
    except Exception:
        return ""


def get_web_intelligence(query, target_date="2025-10-20"):
    """Stage 0: Web情報収集（日英ソース）"""
    print("\n=== Stage 0: Web Intelligence via Google CSE ===")
    results = []
    jp_query = f"{query} site:ipa.go.jp OR site:jpcert.or.jp OR site:nisc.go.jp OR site:aws.amazon.com"
    en_query = f"{query} site:cisa.gov OR site:aws.amazon.com OR site:cloudsecurityalliance.org OR site:bbc.com"

    for q, lang in [(jp_query, "lang_ja"), (en_query, "lang_en")]:
        items = google_search(q, num=6, lang=lang)
        for item in items:
            url = item.get("link")
            if not url:
                continue
            text = fetch_page_excerpt(url)
            results.append({
                "lang": "JP" if lang == "lang_ja" else "EN",
                "title": item.get("title", ""),
                "url": url,
                "snippet": item.get("snippet", ""),
                "excerpt": text
            })

    bullet_lines = []
    for r in results:
        bullet_lines.append(
            f"- [{r['lang']}] {r['title']} — {r['url']}\n"
            f"  Snippet: {r['snippet']}\n"
            f"  Extract: {r['excerpt']}\n"
        )

    web_pack = f"Cut-off: <= {target_date}\n\nSources (JP+EN):\n" + "\n".join(bullet_lines)
    timestamp = datetime.datetime.utcnow().isoformat()

    os.makedirs("results", exist_ok=True)
    with open("results/web_observation.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "query": query,
            "target_date": target_date,
            "sources": [{"lang": r["lang"], "url": r["url"]} for r in results],
            "raw_text": web_pack
        }, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(results)} sources fetched via Google CSE.")
    return web_pack


# === OpenAI APIを使ったAI議論フェーズ ===
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_model(role_name, query, web_summary, system_prompt):
    prompt = f"{system_prompt}\n\n[Web Intelligence Summary]\n{web_summary}\n\nQuery: {query}"
    resp = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": role_name},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return resp.choices[0].message.content.strip()


def run_multistage_debate(query):
    print(f"\n🧠 Running MAGI Debate for query:\n{query}\n")

    # --- Stage 0: Web情報収集 ---
    web_summary = get_web_intelligence(query)

    # --- Stage 1: 各AIの独立分析 ---
    print("\n=== Stage 1: Primary Debate ===")
    logic = ask_model("You are BALTHASAR-2, Logic AI. Provide analytical reasoning only based on evidence.", query, web_summary,
                      "Perform logical analysis using evidence only.")
    ethics = ask_model("You are CASPER-3, Ethics AI. Evaluate ethical and evidential integrity.", query, web_summary,
                       "Perform ethical and evidential analysis.")
    intuition = ask_model("You are MELCHIOR-1, Intuition AI. Provide intuitive insights from subtle patterns.", query, web_summary,
                          "Perform intuitive, contextual analysis based on evidence.")

    # --- Stage 2: 反論・統合 ---
    print("\n=== Stage 2: Rebuttal ===")
    rebuttal_prompt = f"""
Below are three independent analyses of the query.

[LOGIC]
{logic}

[ETHICS]
{ethics}

[INTUITION]
{intuition}

Now integrate their perspectives, address disagreements, and refine their conclusions step-by-step.
"""
    synthesis = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are MAGI Integrator, combining multiple AI opinions into a coherent synthesis."},
            {"role": "user", "content": rebuttal_prompt}
        ],
        temperature=0.4
    ).choices[0].message.content.strip()

    # --- Stage 3: メタ合意（Meta-Consensus）---
    print("\n=== Stage 3: Meta-Consensus ===")
    meta_prompt = f"""
You are the final arbiter (MAGI Meta-Consensus).
Unify the reasoning, ethics, and intuition into a single coherent conclusion.
State confidence level, verified evidence, and remaining uncertainty.

[Synthesis Notes]
{synthesis}
"""
    meta = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are MAGI Meta-Consensus AI."},
            {"role": "user", "content": meta_prompt}
        ],
        temperature=0.4
    ).choices[0].message.content.strip()

    # --- 保存 ---
    report = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "query": query,
        "Stage0_WebObservation": web_summary,
        "Stage1_Logic": logic,
        "Stage1_Ethics": ethics,
        "Stage1_Intuition": intuition,
        "Stage2_Synthesis": synthesis,
        "Stage3_MetaConsensus": meta
    }

    os.makedirs("results", exist_ok=True)
    with open("results/magi_debate_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n✅ MAGI Debate complete. Results saved to results/magi_debate_report.json")
    return report


# === CLI実行用 ===
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scripts/magi_debate_multistage.py \"<query>\"")
        sys.exit(1)
    query = sys.argv[1]
    run_multistage_debate(query)
