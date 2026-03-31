# 🤖 a MAGi goe System

**Multi-Agent Generative Intelligence Consensus Analysis System**

エヴァンゲリオンのMAGIシステムにインスパイアされた、複数の最先端AIモデルによる協調的思考進化システム

[![GitHub Pages](https://img.shields.io/badge/demo-live-brightgreen)](https://kg-ninja.github.io/aMAGIgoesystem/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![#KGNINJA](https://img.shields.io/badge/%23-KGNINJA-ff6600)](https://github.com/KG-NINJA)

---

## 🎯 Overview

a MAGi goe System は、3つの異なる視点を持つAIシステム（Logic, Ethics, Intuition）が協調的に思考を進化させる、次世代の意思決定支援システムです。

### 3つのMAGIシステム

| System | AI Model | Role | Perspective |
|--------|----------|------|-------------|
| **BALTHASAR-2** | Google Gemini 2.5 Flash | Logic System | 論理的分析・構造的思考 |
| **CASPER-3** | Anthropic Claude Sonnet 4.5 | Ethics System | 倫理的評価・道徳的判断 |
| **MELCHIOR-1** | OpenAI GPT-4o | Intuition System | 直感的洞察・創造的思考 |

---

## ✨ Features

### 🔄 2つの動作モード

#### 1. Simple Fusion Mode（単一ラウンド）
- 各AIが独立して回答を生成
- セマンティック類似度によるコンセンサス分析
- 迅速な意思決定に最適

#### 2. Multi-Stage Debate Mode（多段階ディベート）★推奨★
真の協調的思考進化を実現する3段階プロセス：

```
Stage 1: Primary Debate（観点の拡散）
  ├─ 各AIが完全独立で分析
  └─ Logic, Ethics, Intuition の3視点

       ↓ 相互参照

Stage 2: Rebuttal Round（観点の収束）
  ├─ 他AIの回答を読んで再評価
  ├─ 欠陥の修正 or 立場の防御
  └─ 統合的な第2意見を生成

       ↓ メタ統合

Stage 3: Meta-Consensus（最終統合）
  ├─ 収束点と有益な相違点を特定
  ├─ 信頼度レベル付き最終推奨
  └─ 収束率の定量評価
```

### 📊 高度な分析機能
- **収束率測定**: ラウンド間での意見の収束度を定量化
- **類似度分析**: セマンティック埋め込みによる意見の一致度
- **信頼度評価**: コンセンサス強度に基づく信頼レベル

### 🎨 NERV風UIダッシュボード
- エヴァンゲリオンのMAGI制御画面を再現
- リアルタイムの審議アニメーション
- 3段階ディベートの可視化
- レスポンシブデザイン対応

### 🛡️ 堅牢性
- APIエラー時の自動フォールバック
- 部分的なシステム障害にも対応
- GitHub Actions による自動実行
- 結果の永続化（JSON + Markdown）

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- API Keys:
  - **OpenAI API Key** (必須)
  - **Google AI API Key** (必須 - Gemini用)
  - **Google Custom Search API Key** (推奨 - Web検索用)
  - **Google Custom Search Engine ID (CX)** (推奨)
  - **Anthropic API Key** (オプション)

### Google Custom Search API の設定

Stage 0 の Web Intelligence 機能を使用するには、Google Custom Search API の設定が必要です。

#### 1. Custom Search API を有効化

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを選択（なければ作成）
3. 「APIとサービス」→「ライブラリ」
4. "Custom Search API" を検索して有効化

#### 2. API キーを発行

1. [API認証情報](https://console.cloud.google.com/apis/credentials) にアクセス
2. 「認証情報を作成」→「APIキー」
3. 生成されたキーをコピー（これが `GOOGLE_SEARCH_API_KEY`）

#### 3. Programmable Search Engine を作成

1. [Programmable Search Engine](https://programmablesearchengine.google.com/) にアクセス
2. 「追加」をクリック
3. 以下を設定：
   - 検索するサイト: `ipa.go.jp, jpcert.or.jp, cisa.gov, nist.gov` など
   - または「ウェブ全体を検索」を選択
4. 作成後、「検索エンジンID」をコピー（これが `GOOGLE_CX`）

> **注意**: Google AI API Key (Gemini用) と Google Search API Key は**別物**です！

### Installation

```bash
# リポジトリのクローン
git clone https://github.com/KG-NINJA/aMAGIgoesystem.git
cd aMAGIgoesystem

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."              # Gemini用
export GOOGLE_SEARCH_API_KEY="AIza..."       # Custom Search用
export GOOGLE_CX="c73b36615959a4d48"         # Search Engine ID
export ANTHROPIC_API_KEY="sk-ant-..."        # オプション
```

または `.env` ファイルを作成：

```bash
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
GOOGLE_SEARCH_API_KEY=AIza...
GOOGLE_CX=c73b36615959a4d48
ANTHROPIC_API_KEY=sk-ant-...
```

### Usage

#### Simple Fusion Mode

```bash
python scripts/magi_fusion.py "量子コンピュータの倫理的影響は？"
```

#### Multi-Stage Debate Mode（推奨）

```bash
python scripts/magi_debate_multistage.py "AGIは人類にとって脅威か機会か？"
```

**実行例:**
```bash
# Kaggle競技者の評価
python scripts/magi_debate_multistage.py "KGNINJAのKaggle実力を多角的に評価して"

# 哲学的問い
python scripts/magi_debate_multistage.py "意識とは何か？AIは意識を持ちうるか？"

# 社会問題
python scripts/magi_debate_multistage.py "ベーシックインカムは実現可能か？"
```

---

## 📁 Project Structure

```
aMAGIgoesystem/
├── .github/
│   └── workflows/
│       ├── magi_fusion.yml              # Simple Fusion自動実行
│       ├── magi_multistage.yml          # Multi-Stage Debate自動実行
│       └── magi_multistage_robust.yml   # より堅牢なバージョン
├── scripts/
│   ├── magi_fusion.py                   # Simple Fusionスクリプト
│   └── magi_debate_multistage.py        # Multi-Stage Debateスクリプト
├── results/
│   ├── fusion_results.json              # Simple Fusion結果
│   ├── consensus_log.md                 # Simple Fusionログ
│   ├── multistage_debate.json           # Multi-Stage結果
│   └── multistage_log.md                # Multi-Stageログ
├── docs/
│   ├── index.html                       # NERV風ダッシュボード
│   └── .nojekyll                        # Jekyll無効化
├── requirements.txt                     # Python依存パッケージ
├── .gitignore                          
└── README.md
```

---

## 🌐 Live Demo

**NERV風ダッシュボード:** https://kg-ninja.github.io/aMAGIgoesystem/

- リアルタイムの審議アニメーション
- Simple FusionとMulti-Stage Debateの切り替え
- 完全なトランスクリプトの閲覧
- 収束率の可視化

---

## 🤖 GitHub Actions

### 手動実行

1. リポジトリの **Actions** タブを開く
2. ワークフローを選択:
   - `MAGI Fusion System` - Simple Fusion
   - `MAGI Multi-Stage Deliberation` - Multi-Stage Debate
3. **Run workflow** をクリック
4. クエリを入力して実行

### 自動実行

- **Simple Fusion**: 毎週日曜日 0:00 UTC
- **Multi-Stage Debate**: 毎週日曜日 12:00 UTC

結果は自動的に `results/` ディレクトリにコミットされます。

---

## 📊 Output Format

### Simple Fusion結果

```json
{
  "timestamp": "2025-10-19T12:00:00.000000",
  "question": "Your query",
  "models": {
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-5-20250929",
    "gemini": "gemini-2.5-flash"
  },
  "responses": {
    "openai": "...",
    "anthropic": "...",
    "gemini": "..."
  },
  "fusion": "Consensus analysis",
  "score": 0.85
}
```

### Multi-Stage Debate結果

```json
{
  "timestamp": "2025-10-19T12:00:00.000000",
  "query": "Your query",
  "stage1_primary_debate": {
    "logic": "...",
    "ethics": "...",
    "intuition": "..."
  },
  "stage2_rebuttal_round": {
    "logic": "...",
    "ethics": "...",
    "intuition": "..."
  },
  "stage3_meta_consensus": "Final synthesis",
  "similarity_analysis": {
    "round1": 0.65,
    "round2": 0.82,
    "convergence": 0.17
  }
}
```

---

## 🧠 技術的特徴

### Multi-Stage Debateの仕組み

#### Stage 1: Primary Debate
各AIが完全に独立して分析を行う「観点の拡散」フェーズ。

```python
prompt = f"""You are {system_name}, representing {role}.
Query: {query}
Provide your independent analysis."""
```

#### Stage 2: Rebuttal Round
他のAIの回答を参照して再評価する「観点の収束」フェーズ。

```python
rebuttal_prompt = f"""
Your initial response: {original_response}
Other systems' responses: {other_responses}

Re-evaluate your stance:
1. Identify valuable insights you missed
2. Correct flaws in your reasoning
3. Defend your position if others missed key points
4. Synthesize all perspectives
"""
```

#### Stage 3: Meta-Consensus
メタAIが全ラウンドを統合する「最終統合」フェーズ。

### 収束率の計算

```python
convergence_rate = round2_similarity - round1_similarity
# 正の値 = コンセンサスが向上
# 負の値 = 意見が多様化
```

---

## 🎨 カスタマイズ

### モデルの変更

`scripts/magi_debate_multistage.py` の以下を編集:

```python
# OpenAI
model="gpt-4o"  # or "gpt-4o-mini", "o1-preview"

# Anthropic
model="claude-sonnet-4-5-20250929"  # or "claude-opus-4-1"

# Google
model="gemini-2.5-flash"  # or "gemini-2.5-pro"
```

### UIのカスタマイズ

`docs/index.html` のCSS変数を編集:

```css
:root {
  --color-primary: #00ff00;    /* メインカラー */
  --color-secondary: #00ccff;  /* セカンダリカラー */
  --color-warning: #ff6600;    /* 警告色 */
}
```

---

## 📈 Use Cases

- **研究開発**: 複雑な科学的・技術的問題の多角的分析
- **倫理的判断**: 道徳的ジレンマの構造化された議論
- **戦略立案**: ビジネス意思決定の包括的評価
- **教育**: 批判的思考と多様な視点の学習
- **政策分析**: 社会問題に対する多面的アプローチ

---

## 🤝 Contributing

コントリビューション大歓迎です！

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by the MAGI system from **Neon Genesis Evangelion**
- Powered by:
  - [OpenAI](https://openai.com/) - GPT-4o
  - [Anthropic](https://www.anthropic.com/) - Claude Sonnet 4.5
  - [Google AI](https://ai.google/) - Gemini 2.0
- Built by [**#KGNINJA**](https://github.com/KG-NINJA)

---

## 📞 Contact

- GitHub: [@KG-NINJA](https://github.com/KG-NINJA)
- Project Link: https://github.com/KG-NINJA/aMAGIgoesystem
- Live Demo: https://kg-ninja.github.io/aMAGIgoesystem/

---

<div align="center">

**🤖 a MAGi goe System - Where Logic, Ethics, and Intuition Converge**

Made with 💚 by #KGNINJA

</div>
