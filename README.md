# 🤖 MAGI Fusion System

Multi-AI Consensus Analysis using GPT-4o, Claude Sonnet 4.5, and Gemini 2.0

## Overview

MAGI (Multi-Agent Generative Intelligence) システムは、複数の最先端AIモデルからの回答を統合し、コンセンサス分析を行うシステムです。エヴァンゲリオンのMAGIシステムにインスパイアされています。

### 3つのMAGIシステム:
- **Logic (OpenAI GPT-4o)**: 論理的思考
- **Ethics (Anthropic Claude Sonnet 4.5)**: 倫理的判断
- **Intuition (Google Gemini 2.0)**: 直感的洞察

## Features

- 🔄 複数AIモデルの並列クエリ
- 🧠 **多段階ディベートシステム（NEW!）**
  - **Stage 1: Primary Debate** - 各AIが独立に分析
  - **Stage 2: Rebuttal Round** - 他のAIの視点を踏まえて再評価
  - **Stage 3: Meta-Consensus** - 統合的な最終判断
- 📊 セマンティック類似度によるコンセンサス分析
- 📈 収束率測定（ラウンド間での意見の収束度）
- 🛡️ 強力なエラーハンドリング（1つのAPIが失敗しても継続）
- 📝 結果の自動保存（JSON + Markdown）
- 🤖 GitHub Actions による自動実行

## Installation

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/aMAGIgoesystem.git
cd aMAGIgoesystem

# 依存パッケージのインストール
pip install -r requirements.txt
```

## Configuration

環境変数に3つのAPIキーを設定：

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AI..."
```

## Usage

### シンプルモード（単一ラウンド）

```bash
python scripts/magi_fusion.py "Your question here"
```

### 多段階ディベートモード（推奨）

```bash
python scripts/magi_debate_multistage.py "Should AI systems have rights?"
```

**多段階モードの構造:**

```
Stage 1: Primary Debate (独立思考)
  ├─ BALTHASAR-2 (Logic): 論理的分析
  ├─ CASPER-3 (Ethics): 倫理的評価  
  └─ MELCHIOR-1 (Intuition): 直感的洞察

       ↓ 各AIが他の回答を参照

Stage 2: Rebuttal Round (協調的再思考)
  ├─ 他の視点を考慮した再評価
  ├─ 欠陥の修正 or 立場の防御
  └─ 統合的な第2意見を生成

       ↓ メタAIによる統合

Stage 3: Meta-Consensus (最終統合)
  └─ 収束点と有益な相違点を特定
  └─ バランスの取れた最終推奨
```

### GitHub Actions で実行

1. リポジトリの Settings → Secrets and variables → Actions
2. 以下のシークレットを追加:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `GOOGLE_API_KEY`
3. Actions タブから "MAGI Fusion System" を手動実行

## Output

実行結果は `results/` ディレクトリに保存されます：

- `fusion_results.json`: 完全な結果データ（JSON形式）
- `consensus_log.md`: 実行履歴ログ（Markdown形式）

## Project Structure

```
aMAGIgoesystem/
├── .github/
│   └── workflows/
│       └── magi_fusion.yml
├── scripts/
│   └── magi_fusion.py
├── results/
│   ├── fusion_results.json
│   └── consensus_log.md
├── requirements.txt
├── .gitignore
└── README.md
```

## Example Output

```
==========================================================
MAGI SYSTEM - Multi-AI Consensus Analysis
==========================================================

Query: What is consciousness?

Consulting MAGI systems...

    Querying OpenAI GPT-4o...
    ✓ OpenAI response received
    Querying Anthropic Claude Sonnet 4.5...
    ✗ Anthropic failed: Credit balance too low
    Querying Google Gemini 2.0...
    ✓ Gemini response received

==========================================================
Analyzing consensus...
==========================================================

⚠️  1 MAGI system(s) unavailable

✓ Consensus reached (similarity: 0.82)
2/3 systems operational

[✓ Logic(OpenAI)]
Consciousness is...

---

[✗ Ethics(Anthropic)]
[Anthropic Error: Credit balance too low]

---

[✓ Intuition(Gemini)]
Consciousness represents...
```

## Requirements

- Python 3.11+
- OpenAI API access
- Anthropic API access (optional)
- Google AI API access

## License

MIT License

## Acknowledgments

Inspired by the MAGI system from Neon Genesis Evangelion
