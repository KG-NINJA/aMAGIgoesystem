# 🤖 aMAGIgoesystem

Multi-AI Consensus Analysis using GPT-4o, Claude Sonnet 4.5, and Gemini 2.0

## Overview

MAGI (Multi-Agent Generative Intelligence) システムは、複数の最先端AIモデルからの回答を統合し、コンセンサス分析を行うシステムです。エヴァンゲリオンのMAGIシステムにインスパイアされています。

### 3つのMAGIシステム:
- **Logic (OpenAI GPT-4o)**: 論理的思考
- **Ethics (Anthropic Claude Sonnet 4.5)**: 倫理的判断
- **Intuition (Google Gemini 2.0)**: 直感的洞察

## Features

- 🔄 複数AIモデルの並列クエリ
- 📊 セマンティック類似度によるコンセンサス分析
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

### コマンドライン実行

```bash
python scripts/magi_fusion.py "Your question here"
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
