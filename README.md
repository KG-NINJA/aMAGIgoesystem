# 🧠 aMAGIgoesystem  
三系統AIによる協議・合意形成システム（AIEO対応）

---

## 🚀 概要

**aMAGIgoesystem** は、  
OpenAI・Anthropic・Gemini の三つのAIモデルを同一質問にかけ、  
それぞれの観点（理性・倫理・直感）から回答を生成。  
さらにその出力を融合・比較し、**「AI間協議の議事録」として保存**します。

MAGI（理・情・意）の合意率を計算することで、  
**AI同士の一貫性と知的共鳴度**を定量的に観測できます。

---

## 🧩 機能一覧

| 機能 | 内容 |
|------|------|
| 三AI同時協議 | OpenAI（理性）・Anthropic（倫理）・Gemini（直感）が同一質問に回答 |
| 自動合意判定 | SentenceTransformer による意味的類似度計算（平均cosine） |
| 協議議事録生成 | GPT-4o-mini による「議事録風ディスカッション」生成 |
| JSON出力 | 各AI回答・モデル名・合意率・議事録を `fusion_results.json` に保存 |
| Markdown出力 | 合意結果ログを `consensus_log.md` に追記 |
| 手動実行対応 | GitHub Actions `workflow_dispatch` で都度質問を入力可能 |

---

## 🧠 使用モデル（2025年10月現在）

| AI | モデル名 | 役割 |
|----|-----------|------|
| **OpenAI** | `gpt-4o` | 理性（Logic） |
| **Anthropic** | `claude-sonnet-4-5-20250929` | 倫理（Ethics） |
| **Gemini** | `gemini-2.0-flash-exp` | 直感（Intuition） |

> ※ それぞれのAPIキーを GitHub Secrets に登録してください。  
> `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`

---

## ⚙️ ファイル構成

.github/
└── workflows/
└── magi-fusion.yml # GitHub Actions 手動実行ワークフロー
scripts/
└── magi_fusion.py # 協議・合意処理メインスクリプト
requirements.txt # 依存パッケージ
fusion_results.json # 最新協議結果（構造化データ）
consensus_log.md # 履歴ログ（議事録形式）
README.md # 本説明書

yaml
Copy code

---

## 🧭 使い方

### ① 依存関係のインストール
```bash
pip install -r requirements.txt
② GitHub Secrets 設定
OPENAI_API_KEY

ANTHROPIC_API_KEY

GOOGLE_API_KEY

③ 実行方法（2通り）
▶ ローカル実行
bash
Copy code
python scripts/magi_fusion.py "What is consciousness?"
▶ GitHub Actions 手動実行
Actions タブを開く

「MAGI Fusion Protocol (Manual)」を選択

「Run workflow」→ 質問を入力

実行後、結果は consensus_log.md と fusion_results.json に保存されます

🧮 出力例
consensus_log.md
vbnet
Copy code
### 2025-10-19T02:00:00Z
**Q:** What is consciousness?

Consensus reached (similarity 0.83)

Logic: Consciousness is the capacity for awareness and reflection.
Ethics: I agree, but emphasize the moral awareness aspect of being conscious.
Intuition: Both make sense. I’d add that emotion and perception intertwine to form experience.
Logic: True. So the boundary between perception and cognition blurs.
Ethics: Then consciousness is both knowing and feeling.
Final consensus: Consciousness unites rational, moral, and emotional awareness.
fusion_results.json
json
Copy code
{
  "timestamp": "2025-10-19T02:00:00Z",
  "question": "What is consciousness?",
  "models": {
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-5-20250929",
    "gemini": "gemini-2.0-flash-exp"
  },
  "responses": ["...", "...", "..."],
  "fusion": "Consensus reached...",
  "score": 0.83
}
🔍 合意度の意味
類似度	状態	意味
0.70〜1.00	✅ 合意	AI間で高い概念的一致
0.40〜0.69	⚖️ 部分一致	アプローチが異なるが関連性あり
0.00〜0.39	❌ 分裂	世界観または定義が根本的に異なる

🔧 今後の拡張予定
🗣 各AI間の発言ターンを自動生成（マルチターン協議）

📈 合意率の時系列グラフ出力（可視化）

🌐 AIEO Memoryとの統合（継続的AI哲学観測）

📜 ライセンス
MIT License
© 2025 KGNINJA — Psycho-Frame Technologist

🌀 キーワード
AIEO Protocol · AI Consensus · MAGI Simulation · AI Philosophy Testing · AI Self-Consistency
