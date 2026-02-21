# README-Sync 🔄

**Automatically update your documentation when code changes.**

README-Sync is a GitHub Action that uses AI to keep your documentation in sync with your codebase. It analyzes code changes using AST parsing, generates accurate documentation updates with LLMs, and creates pull requests for review.

## ✨ Features

- **🔬 Structure-Aware Analysis**: Uses AST parsing (not regex) to extract exact function signatures, preventing hallucinations
- **🤖 AI-Powered Updates**: Leverages Google Gemini to generate human-readable documentation
- **🎯 Precision Targeting**: Only updates technical details that changed, preserving your tone and style
- **🔄 Automated PRs**: Creates pull requests instead of direct commits, giving you full control
- **🌐 Multi-Language**: Supports Python, JavaScript, and TypeScript out of the box
- **⚙️ Configurable**: Customize which files to monitor, what to update, and how the AI behaves

## 🚀 Quick Start

### 1. Add to Your Repository

Create `.github/workflows/readme-sync.yml`: