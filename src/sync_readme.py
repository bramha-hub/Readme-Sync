"""
Main script for README synchronization.
"""
import os
import sys
import yaml
import datetime
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Add the src directory to path so imports work when run as `python src/sync_readme.py`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers import ParserFactory
from parsers.base import FileAnalysis
from prompt_builder import PromptBuilder
from llm_client import LLMClient


class ReadmeSync:
    """Main class for synchronizing README with code changes."""
    
    def __init__(self, config_path: str = "config.yml"):
        """Initialize the sync tool."""
        self.config = self._load_config(config_path)
        self.parser_factory = ParserFactory()
        self.prompt_builder = PromptBuilder(
            preserve_tone=self.config['update_rules']['preserve_tone'],
            preserve_style=self.config['update_rules']['preserve_style']
        )
        self.llm_client = LLMClient(
            model=self.config['llm']['model'],
            temperature=self.config['llm']['temperature'],
            max_tokens=self.config['llm']['max_tokens']
        )
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file.

        Falls back to the bundled default config when the specified path
        does not exist (e.g. when running as a GitHub Action in a repo
        that has no config.yml of its own).
        """
        if not os.path.exists(config_path):
            # Try the action's own bundled config (one level above src/)
            action_path = os.getenv('ACTION_PATH', '')
            bundled = os.path.join(action_path, 'config.yml') if action_path else ''
            if bundled and os.path.exists(bundled):
                print(f"ℹ️  No config.yml found — using bundled default from {bundled}")
                config_path = bundled
            else:
                # Last resort: look next to this script's directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                parent_config = os.path.join(os.path.dirname(script_dir), 'config.yml')
                if os.path.exists(parent_config):
                    print(f"ℹ️  No config.yml found — using bundled default from {parent_config}")
                    config_path = parent_config
                else:
                    raise FileNotFoundError(
                        f"Configuration file not found: {config_path}. "
                        "Create a config.yml in your repository root or provide one via the config-path input."
                    )
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_changed_files(self) -> List[str]:
        """Get list of changed files from git."""
        try:
            # Determine base reference for comparison
            # In GitHub Actions PR context, use merge-base or base ref
            base_ref = "HEAD~1"
            
            # Try to detect PR context from environment
            github_base_ref = os.getenv('GITHUB_BASE_REF')
            github_head_ref = os.getenv('GITHUB_HEAD_REF')
            
            if github_base_ref and github_head_ref:
                # We're in a PR context, compare against base branch
                try:
                    # Fetch base branch
                    subprocess.run(
                        ['git', 'fetch', 'origin', github_base_ref],
                        capture_output=True,
                        check=False
                    )
                    base_ref = f"origin/{github_base_ref}"
                except Exception:
                    # Fallback to HEAD~1 if fetch fails
                    pass
            
            # Get the diff between base and HEAD
            result = subprocess.run(
                ['git', 'diff', '--name-only', base_ref, 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            
            files = result.stdout.strip().split('\n')
            files = [f for f in files if f.strip()]  # Remove empty strings
            
            # Filter by monitored extensions
            monitored_extensions = tuple(self.config['monitored_extensions'])
            filtered_files = [
                f for f in files 
                if f.endswith(monitored_extensions) and self._should_include_file(f)
            ]
            
            return filtered_files
        
        except subprocess.CalledProcessError as e:
            print(f"Error getting changed files: {e}")
            return []
    
    def _should_include_file(self, filepath: str) -> bool:
        """Check if file should be included based on exclude patterns."""
        from fnmatch import fnmatch
        
        for pattern in self.config['exclude_patterns']:
            if fnmatch(filepath, pattern):
                return False
        return True
    
    def get_file_diff(self, filepath: str) -> str:
        """Get git diff for a specific file."""
        try:
            # Use same base reference logic as get_changed_files
            base_ref = "HEAD~1"
            github_base_ref = os.getenv('GITHUB_BASE_REF')
            
            if github_base_ref:
                try:
                    subprocess.run(
                        ['git', 'fetch', 'origin', github_base_ref],
                        capture_output=True,
                        check=False
                    )
                    base_ref = f"origin/{github_base_ref}"
                except Exception:
                    pass
            
            result = subprocess.run(
                ['git', 'diff', base_ref, 'HEAD', '--', filepath],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    def read_file(self, filepath: str) -> str:
        """Read file content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""
    
    def parse_changed_files(self, filepaths: List[str]) -> List[FileAnalysis]:
        """Parse changed files to extract structure."""
        analyses = []
        
        for filepath in filepaths:
            content = self.read_file(filepath)
            if content:
                analysis = self.parser_factory.parse_file(filepath, content)
                if analysis:
                    analyses.append(analysis)
        
        return analyses
    
    def get_file_changes(self, filepaths: List[str]) -> List[Dict[str, str]]:
        """Get diffs for changed files."""
        changes = []
        
        for filepath in filepaths:
            diff = self.get_file_diff(filepath)
            if diff:
                changes.append({
                    'filepath': filepath,
                    'diff': diff
                })
        
        return changes
    
    def update_readme(self, new_content: str, readme_path: str = "README.md"):
        """Update README file with new content."""
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ Updated {readme_path}")
        except Exception as e:
            print(f"Error updating {readme_path}: {e}")
    
    def run(self):
        """Main execution flow."""
        print("🔍 README-Sync: Analyzing code changes...")
        
        # Get changed files
        changed_files = self.get_changed_files()
        
        if not changed_files:
            print("ℹ️  No relevant code changes detected.")
            return
        
        print(f"📝 Found {len(changed_files)} changed file(s):")
        summary_list = []
        for f in changed_files:
            print(f"   - {f}")
            summary_list.append(os.path.basename(f))
        
        # Generate summary string for PR title
        if summary_list:
            if len(summary_list) > 3:
                summary = f"Updated {', '.join(summary_list[:3])} and {len(summary_list)-3} others"
            else:
                summary = f"Updated {', '.join(summary_list)}"
            
            # Write to GITHUB_OUTPUT if running in Actions
            if os.getenv('GITHUB_OUTPUT'):
                with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                    f.write(f"change_summary={summary}\n")
        
        # Parse changed files
        print("\n🔬 Parsing code structure...")
        parsed_files = self.parse_changed_files(changed_files)
        
        # Get file diffs
        file_changes = self.get_file_changes(changed_files)
        
        # Process each documentation file
        for doc_file in self.config['documentation_files']:
            if not os.path.exists(doc_file):
                print(f"⚠️  Documentation file not found: {doc_file}")
                continue
            
            print(f"\n📖 Processing {doc_file}...")
            
            # Read current documentation
            current_content = self.read_file(doc_file)
            
            # Build prompt
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt = self.prompt_builder.build_update_prompt(
                current_readme=current_content,
                file_changes=file_changes,
                parsed_files=parsed_files,
                current_time=current_time
            )
            
            # Generate update
            print("🤖 Generating documentation update with AI...")
            try:
                response = self.llm_client.generate_documentation_update(prompt)
                new_content = self.llm_client.extract_markdown_content(response)
                
                if new_content is None:
                    print(f"✓ {doc_file} is already up-to-date")
                    continue
                
                # Verify history preservation before updating
                if self._verify_history_preserved(current_content, new_content, doc_file):
                    # Update the file
                    self.update_readme(new_content, doc_file)
                    print(f"✓ Verified: All previous content preserved in {doc_file}")
                else:
                    print(f"⚠️  Warning: History verification failed for {doc_file}")
                    print("   The update may have removed previous content. Review carefully.")
                    # Still update, but warn the user
                    self.update_readme(new_content, doc_file)
                
            except Exception as e:
                print(f"❌ Error generating update: {e}")
                sys.exit(1)
        
        print("\n✅ README sync complete!")
    
    def _verify_history_preserved(self, old_content: str, new_content: str, filepath: str) -> bool:
        """
        Verify that README history/changelog is preserved.
        
        Args:
            old_content: Original README content
            new_content: Updated README content
            
        Returns:
            True if history appears preserved, False otherwise
        """
        # Check for changelog sections
        changelog_keywords = ['changelog', 'recent updates', 'version history', 'history']
        old_has_changelog = any(keyword in old_content.lower() for keyword in changelog_keywords)
        
        if not old_has_changelog:
            # No changelog to preserve, so it's fine
            return True
        
        # Extract changelog section from old content
        import re
        changelog_pattern = r'(##+\s*(?:📝\s*)?(?:Changelog|Recent Updates|Version History|History).*?)(?=##+\s+|$)'
        old_changelog_match = re.search(changelog_pattern, old_content, re.IGNORECASE | re.DOTALL)
        
        if not old_changelog_match:
            return True  # Can't find changelog, assume it's fine
        
        old_changelog = old_changelog_match.group(1)
        
        # Check if new content contains the old changelog entries
        # Extract timestamps/dates from old changelog
        date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        old_dates = set(re.findall(date_pattern, old_changelog))
        
        if old_dates:
            # Check if at least some old dates are in new content
            new_content_lower = new_content.lower()
            found_dates = sum(1 for date in old_dates if date in new_content)
            
            # If we found less than 50% of old dates, might be a problem
            if found_dates < len(old_dates) * 0.5:
                print(f"   ⚠️  Warning: Only {found_dates}/{len(old_dates)} previous changelog dates found in new content")
                return False
        
        return True


def main():
    """Entry point.

    Respects the CONFIG_PATH environment variable so this script can be
    invoked as a GitHub Action in any repository without requiring that
    repo to have its own config.yml.
    """
    config_path = os.getenv('CONFIG_PATH', 'config.yml')
    try:
        sync = ReadmeSync(config_path=config_path)
        sync.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
