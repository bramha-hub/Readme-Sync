# README-Sync 🔄

**Automatically update your documentation when code changes.**

README-Sync is a GitHub Action that uses AI to keep your documentation in sync with your codebase. It analyzes code changes using AST parsing, generates accurate documentation updates with LLMs, and creates pull requests for review.

## ✨ Features

-   **🔬 Structure-Aware Analysis**: Uses AST parsing (not regex) to extract exact function signatures, preventing hallucinations
-   **🤖 AI-Powered Updates**: Leverages Google Gemini to generate human-readable documentation
-   **🎯 Precision Targeting**: Only updates technical details that changed, preserving your tone and style
-   **🔄 Automated PRs**: Creates pull requests instead of direct commits, giving you full control
-   **🌐 Multi-Language**: Supports Python, JavaScript, and TypeScript out of the box
-   **⚙️ Configurable**: Customize which files to monitor, what to update, and how the AI behaves

## 🚀 Quick Start

### 1. Add to Your Repository

Create `.github/workflows/readme-sync.yml`:

```yaml
name: README Sync

on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: write
  pull-requests: write

jobs:
  sync-readme:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run README-Sync
        uses: bramha-hub/readme-sync@main
        with:
          gemini-api-key: ${{ secrets.GEMINI_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

That's it — **one file** is all you need. README-Sync will automatically handle change detection, AI generation, and PR creation. 🎉

---

### 2. Add Your Gemini API Key

Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey), then add it as a repository secret:

1. Go to your repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `GEMINI_API_KEY` · Value: your key

README-Sync will now run every time you push code and create a PR with updated documentation.

---

## ⚙️ Configuration (Optional)

README-Sync works out of the box with sensible defaults. To customize behaviour, create `config.yml` in your repository root:

```yaml
# Files to monitor for changes
monitored_extensions:
  - .py
  - .js
  - .ts
  - .jsx
  - .tsx

# Documentation files to keep in sync
documentation_files:
  - README.md

# Paths to exclude from analysis
exclude_patterns:
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/tests/**"
  - "**/node_modules/**"
  - "**/__pycache__/**"
  - "**/dist/**"
  - "**/build/**"

# LLM configuration
llm:
  provider: gemini
  model: models/gemini-2.5-flash   # Latest Gemini Flash model
  temperature: 0.3                  # Lower = more deterministic output
  max_tokens: 16384

# Documentation update rules
update_rules:
  preserve_tone: true               # Keep your original writing voice
  preserve_style: true              # Keep your existing formatting
  update_technical_details: true    # Reflect new/changed API details
  update_examples: true             # Update code examples
  add_breaking_changes_section: true
```

### Configuration Reference

| Option | Default | Description |
|--------|---------|-------------|
| `monitored_extensions` | `.py`, `.js`, `.ts`, `.jsx`, `.tsx` | File types that trigger a README update |
| `documentation_files` | `README.md` | Files to keep updated |
| `exclude_patterns` | `**/tests/**`, etc. | Glob patterns to ignore |
| `llm.model` | `models/gemini-2.5-flash` | Gemini model to use |
| `llm.temperature` | `0.3` | Lower = more deterministic |
| `llm.max_tokens` | `16384` | Maximum tokens in AI response |
| `update_rules.preserve_tone` | `true` | Preserve your writing voice |
| `update_rules.preserve_style` | `true` | Preserve your formatting |

---

## 🔍 How It Works

```
Code Push → Change Detection → AST Parsing → AI Generation → Pull Request
```

1. **Change Detection** — On every push, README-Sync checks which source files changed using `git diff`
2. **AST Parsing** — Changed files are parsed with Python's built-in `ast` module (or regex for JS/TS) to extract exact function signatures, class definitions, and docstrings — no guessing
3. **Prompt Building** — A structured prompt is assembled containing the current README, the code diff, and the extracted structure
4. **AI Generation** — Google Gemini generates an updated README that accurately describes the new/changed code
5. **Pull Request** — The updated README is committed to a new branch and a pull request is opened for your review

> README-Sync **always creates a PR** — it never commits directly to your main branch.

---

## 🏗️ Architecture

```
readme-sync/
├── action.yml                    ← GitHub Action entry point (what users reference)
├── config.yml                    ← Default configuration (bundled with the action)
├── requirements.txt
├── src/
│   ├── sync_readme.py            ← Main orchestration pipeline
│   ├── llm_client.py             ← Google Gemini API wrapper
│   ├── prompt_builder.py         ← Structured prompt construction
│   └── parsers/
│       ├── base.py               ← Parser interface & shared data models
│       ├── python_parser.py      ← Python AST parser
│       └── javascript_parser.py  ← JavaScript / TypeScript parser
└── .github/workflows/
    └── readme-sync.yml           ← Workflow used by this repository itself
```

### Key Components

| Component | Description |
|-----------|-------------|
| `sync_readme.py` | Orchestrates the full pipeline: detect → parse → build prompt → generate → update |
| `llm_client.py` | Wraps the Gemini API; handles response extraction and error handling |
| `prompt_builder.py` | Builds prompts with code diffs, AST structure, and changelog-preservation rules |
| `python_parser.py` | Uses Python's `ast` module — full support for type hints, decorators, docstrings |
| `javascript_parser.py` | Regex-based extraction for JS/TS (functions, classes, imports) |

---

## 🌐 Supported Languages

| Language | Parser | What is extracted |
|----------|--------|-------------------|
| Python | AST | Functions, classes, methods, type hints, docstrings, decorators |
| JavaScript | Regex | Functions (declarations + arrow), classes, imports |
| TypeScript | Regex | Functions, classes, imports |
| JSX / TSX | Regex | Component functions, classes |

> More languages (Go, Rust, Java) are planned. Contributions are welcome!

---

## 🔒 Permissions

The workflow needs two permissions:

```yaml
permissions:
  contents: write       # Creates branches and commits the updated README
  pull-requests: write  # Opens the documentation PR
```

These are scoped to the action only and follow GitHub's minimum-permission principle. The `GITHUB_TOKEN` is automatically provided by GitHub — no extra secrets needed beyond your Gemini key.

---

## 🛠️ Local Development

Clone the repo and run the demo locally:

```bash
git clone https://github.com/bramha-hub/readme-sync.git
cd readme-sync
pip install -r requirements.txt

# See the parser and prompt builder in action
python demo.py

# Run the unit tests
pytest tests/
```

To test the full sync pipeline locally (requires a Gemini API key):

```bash
export GEMINI_API_KEY=your_key_here
python src/sync_readme.py
```

---

## 🤝 Contributing

Contributions are very welcome! Here's how to get started:

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests in `tests/`
4. Run the test suite: `pytest tests/`
5. Open a pull request

### Ideas for Contributions

- Add proper AST parsing for JavaScript/TypeScript (replace regex approach)
- Support additional languages: Go, Rust, Java, C#
- Add support for other LLM providers (OpenAI, Anthropic Claude)
- Improve changelog preservation heuristics
- Add caching for large repositories
- Write more comprehensive unit tests

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 📝 Changelog

### 2026-02-22
- feat: add `action.yml` — users now reference this repo as a GitHub Action; one workflow file is all that's needed
- feat: `sync_readme.py` now respects `CONFIG_PATH` env variable and falls back to the bundled `config.yml` when none is found in the target repository
- fix: remove `docs/API.md` from default `documentation_files` (file did not exist, causing spurious warnings)
- fix: update `.github/workflows/readme-sync.yml` with path filters to prevent workflow loops on README-only changes

### 2025-XX-XX
- feat: add `square_root` method to `Calculator` and update `quick_calculate`
- fix: increase `max_tokens` to 16384 for comprehensive README output
- fix: improve prompt instructions to better preserve existing README content
- feat: add example calculator module with operation history tracking
- fix: migrate from `google-generativeai` to the new `google-genai` SDK
- fix: replace `peter-evans/create-pull-request` with native `gh` CLI for PR creation

---

*Built with ❤️ using [Google Gemini](https://deepmind.google/technologies/gemini/) and Python AST*
