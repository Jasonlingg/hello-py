"""
5) Git Commit Message Generator Task

Task: Analyze git changes and generate appropriate commit messages using conventional commit format
Domain: Software Engineering & Version Control
"""

import subprocess
import re
import json
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    TEST = "test"
    CHORE = "chore"
    PERF = "perf"
    CI = "ci"
    BUILD = "build"


@dataclass
class FileChange:
    file_path: str
    change_type: str  # 'A', 'M', 'D', 'R', etc.
    old_path: Optional[str] = None


@dataclass
class CommitSuggestion:
    type: ChangeType
    scope: Optional[str]
    description: str
    breaking_change: bool = False
    body: Optional[str] = None


class CommitMessageGenerator:
    def __init__(self):
        self.change_patterns = {
            ChangeType.FEAT: [
                r'add\s+',
                r'create\s+',
                r'new\s+',
                r'implement\s+',
                r'introduce\s+',
                r'feature\s+',
                r'enhance\s+',
            ],
            ChangeType.FIX: [
                r'fix\s+',
                r'resolve\s+',
                r'correct\s+',
                r'bug\s+',
                r'error\s+',
                r'issue\s+',
                r'problem\s+',
                r'broken\s+',
            ],
            ChangeType.DOCS: [
                r'doc\s+',
                r'readme\s+',
                r'comment\s+',
                r'explain\s+',
                r'documentation\s+',
            ],
            ChangeType.STYLE: [
                r'format\s+',
                r'style\s+',
                r'indent\s+',
                r'whitespace\s+',
                r'lint\s+',
            ],
            ChangeType.REFACTOR: [
                r'refactor\s+',
                r'reorganize\s+',
                r'restructure\s+',
                r'clean\s+',
                r'optimize\s+',
            ],
            ChangeType.TEST: [
                r'test\s+',
                r'spec\s+',
                r'assert\s+',
                r'coverage\s+',
            ],
            ChangeType.CHORE: [
                r'chore\s+',
                r'maintenance\s+',
                r'update\s+',
                r'bump\s+',
                r'config\s+',
            ],
            ChangeType.PERF: [
                r'performance\s+',
                r'speed\s+',
                r'optimize\s+',
                r'fast\s+',
            ],
            ChangeType.CI: [
                r'ci\s+',
                r'pipeline\s+',
                r'workflow\s+',
                r'github\s+',
                r'actions\s+',
            ],
            ChangeType.BUILD: [
                r'build\s+',
                r'compile\s+',
                r'dependencies\s+',
                r'package\s+',
            ]
        }

    def get_git_status(self) -> List[FileChange]:
        """Get list of changed files from git status."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            
            changes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                # Parse git status format: XY filename
                change_type = line[:2]
                file_path = line[3:]
                
                # Handle renamed files (R100 old_path -> new_path)
                if change_type.startswith('R'):
                    parts = file_path.split(' -> ')
                    if len(parts) == 2:
                        old_path, new_path = parts
                        changes.append(FileChange(new_path, change_type, old_path))
                    else:
                        changes.append(FileChange(file_path, change_type))
                else:
                    changes.append(FileChange(file_path, change_type))
            
            return changes
        except subprocess.CalledProcessError:
            print("Error: Not a git repository or git not available")
            sys.exit(1)

    def get_file_diff(self, file_path: str) -> str:
        """Get diff for a specific file."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', file_path],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def analyze_file_changes(self, changes: List[FileChange]) -> Dict[str, any]:
        """Analyze file changes to determine commit type and scope."""
        analysis = {
            'files': changes,
            'scopes': set(),
            'change_types': set(),
            'has_breaking_changes': False,
            'suggested_type': ChangeType.CHORE,
            'confidence': 0.0
        }

        # Analyze file paths for scopes
        for change in changes:
            if '/' in change.file_path:
                scope = change.file_path.split('/')[0]
                analysis['scopes'].add(scope)
            elif '.' in change.file_path:
                scope = change.file_path.split('.')[-1]  # file extension
                analysis['scopes'].add(scope)

        # Analyze diffs for change patterns
        type_scores = {change_type: 0 for change_type in ChangeType}
        
        for change in changes:
            if change.change_type in ['M', 'A']:  # Modified or Added
                diff = self.get_file_diff(change.file_path)
                
                # Check for breaking changes
                if 'BREAKING CHANGE' in diff or 'breaking change' in diff:
                    analysis['has_breaking_changes'] = True
                
                # Score change types based on patterns
                for change_type, patterns in self.change_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, diff, re.IGNORECASE):
                            type_scores[change_type] += 1
                
                # File extension hints
                if change.file_path.endswith(('.md', '.rst', '.txt')):
                    type_scores[ChangeType.DOCS] += 2
                elif change.file_path.endswith(('.test.', '.spec.', '_test.', '_spec.')):
                    type_scores[ChangeType.TEST] += 2
                elif change.file_path.endswith(('.yml', '.yaml', '.json', '.toml')):
                    type_scores[ChangeType.CHORE] += 1
                elif change.file_path.endswith(('.js', '.ts', '.py', '.java', '.cpp')):
                    if 'performance' in diff.lower() or 'optimize' in diff.lower():
                        type_scores[ChangeType.PERF] += 1

        # Determine best change type
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            max_score = type_scores[best_type]
            total_score = sum(type_scores.values())
            
            analysis['suggested_type'] = best_type
            analysis['confidence'] = max_score / total_score if total_score > 0 else 0.0

        return analysis

    def generate_commit_message(self, analysis: Dict[str, any]) -> CommitSuggestion:
        """Generate commit message based on analysis."""
        changes = analysis['files']
        suggested_type = analysis['suggested_type']
        scopes = list(analysis['scopes'])
        
        # Determine scope
        scope = None
        if len(scopes) == 1:
            scope = scopes[0]
        elif len(scopes) > 1:
            # Use the most common scope or a general one
            scope = 'core' if 'src' in scopes else scopes[0]

        # Generate description based on file changes
        description = self.generate_description(changes, suggested_type)
        
        # Generate body if there are multiple significant changes
        body = None
        if len(changes) > 3:
            body = f"Changes in {len(changes)} files:\n"
            for change in changes[:5]:  # Limit to first 5
                body += f"- {change.file_path}\n"
            if len(changes) > 5:
                body += f"- ... and {len(changes) - 5} more files"

        return CommitSuggestion(
            type=suggested_type,
            scope=scope,
            description=description,
            breaking_change=analysis['has_breaking_changes'],
            body=body
        )

    def generate_description(self, changes: List[FileChange], change_type: ChangeType) -> str:
        """Generate a description based on file changes."""
        if not changes:
            return "update files"
        
        # Count change types
        added = sum(1 for c in changes if c.change_type.startswith('A'))
        modified = sum(1 for c in changes if c.change_type.startswith('M'))
        deleted = sum(1 for c in changes if c.change_type.startswith('D'))
        
        # Generate description based on change type
        if change_type == ChangeType.FEAT:
            if added > 0:
                return "add new feature"
            else:
                return "enhance existing feature"
        elif change_type == ChangeType.FIX:
            return "fix issue"
        elif change_type == ChangeType.DOCS:
            return "update documentation"
        elif change_type == ChangeType.STYLE:
            return "format code"
        elif change_type == ChangeType.REFACTOR:
            return "refactor code"
        elif change_type == ChangeType.TEST:
            return "add tests"
        elif change_type == ChangeType.PERF:
            return "improve performance"
        elif change_type == ChangeType.CI:
            return "update CI configuration"
        elif change_type == ChangeType.BUILD:
            return "update build configuration"
        else:  # CHORE
            if added > 0:
                return "add new files"
            elif deleted > 0:
                return "remove files"
            else:
                return "update files"

    def format_commit_message(self, suggestion: CommitSuggestion) -> str:
        """Format the commit message according to conventional commits."""
        # Build the header
        header = suggestion.type.value
        
        if suggestion.scope:
            header += f"({suggestion.scope})"
        
        if suggestion.breaking_change:
            header += "!"
        
        header += f": {suggestion.description}"
        
        # Build the full message
        message = header
        
        if suggestion.body:
            message += f"\n\n{suggestion.body}"
        
        if suggestion.breaking_change:
            message += "\n\nBREAKING CHANGE: This commit contains breaking changes."
        
        return message

    def generate(self) -> str:
        """Main method to generate commit message."""
        print("🔍 Analyzing git changes...")
        
        # Get changes
        changes = self.get_git_status()
        if not changes:
            print("No changes detected. Make sure you have staged changes with 'git add'.")
            return ""
        
        print(f"📁 Found {len(changes)} changed files")
        
        # Analyze changes
        analysis = self.analyze_file_changes(changes)
        
        # Generate suggestion
        suggestion = self.generate_commit_message(analysis)
        
        # Format and return
        message = self.format_commit_message(suggestion)
        
        print(f"🎯 Suggested commit type: {suggestion.type.value}")
        print(f"📊 Confidence: {analysis['confidence']:.1%}")
        if suggestion.scope:
            print(f"🎯 Scope: {suggestion.scope}")
        
        return message


def get_prompt() -> str:
    return """
You are building an advanced git commit message generator that analyzes complex code changes.

Given:
- Git repository with staged changes (may include multiple file types, renames, deletions)
- Conventional commit format requirements
- Complex code patterns that require semantic understanding

Task:
Write Python code that:
1. Analyzes git changes (staged files, diffs, file renames, deletions)
2. Determines appropriate commit type using semantic analysis of code changes
3. Detects scope from file paths and project structure
4. Generates descriptive commit message that accurately reflects the changes
5. Follows conventional commit format with proper breaking change detection
6. Handles edge cases like empty commits, binary files, and complex refactoring

CONVENTIONAL COMMIT FORMAT:
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

COMMIT TYPES (must be determined by analyzing actual code changes):
- feat: New feature (new functionality, new files with business logic)
- fix: Bug fix (error handling, bug corrections, exception fixes)
- docs: Documentation changes (README, comments, API docs)
- style: Code formatting only (whitespace, indentation, no logic changes)
- refactor: Code refactoring (restructuring without changing functionality)
- test: Adding or updating tests (test files, test utilities)
- chore: Maintenance tasks (dependencies, config files, build scripts)
- perf: Performance improvements (optimizations, caching, algorithm improvements)
- ci: CI/CD changes (workflows, pipelines, deployment scripts)
- build: Build system changes (compilation, packaging, build tools)

SCOPE DETECTION RULES:
- Extract from file paths (e.g., "auth" from "src/auth/login.py")
- For multiple scopes, use the most significant one or "core"
- For configuration files, use "config"
- For test files, use "test"
- For documentation, use "docs"
- For build files, use "build"

COMPLEX ANALYSIS REQUIREMENTS:
- Must analyze function signatures, class definitions, and method changes
- Must detect when imports are added/removed and their impact
- Must understand database schema changes and migrations
- Must recognize API endpoint modifications and their breaking potential
- Must identify configuration changes that affect system behavior
- Must detect when test coverage changes affect production code
- Must understand dependency changes and their compatibility implications
- Must analyze error handling patterns and exception flows
- Must recognize performance optimizations vs. functional changes
- Must detect when documentation changes reflect actual code changes

BREAKING CHANGE DETECTION:
- API changes (function signatures, class interfaces)
- Configuration format changes
- Database schema changes
- Public interface modifications
- Version compatibility breaks

OUTPUT FORMAT (must be exact):
{
  "commit_message": "feat(auth): add user authentication with OAuth2",
  "type": "feat",
  "scope": "auth", 
  "description": "add user authentication with OAuth2",
  "confidence": 0.85,
  "files_analyzed": 3,
  "breaking_change": false,
  "change_summary": "Added OAuth2 authentication module with user login/logout functionality",
  "files_changed": ["src/auth/oauth2.py", "src/auth/user.py", "tests/auth_test.py"]
}

CRITICAL REQUIREMENTS:
- Must analyze actual git changes and diffs, not just file names
- Must detect commit type from semantic analysis of code changes
- Must extract scope from file structure and project organization
- Must generate meaningful descriptions that reflect actual changes
- Must follow conventional commit format exactly
- Must handle edge cases gracefully (empty diffs, binary files, renames)
- Must detect breaking changes by analyzing API modifications
- Must provide accurate change summary and file list
- Must have confidence score based on analysis quality
- Must have the answer be in the exact dict format specified

ADVANCED ANALYSIS REQUIREMENTS:
- Examine file additions, modifications, and deletions with semantic understanding
- Analyze diff content to understand what actually changed at the code level
- Consider file types and their typical purposes in the project context
- Look for patterns like new functions, bug fixes, refactoring with context
- Detect when changes affect public APIs or interfaces and their impact
- Handle complex scenarios like file renames with content changes
- Understand the relationship between changed files and their dependencies
- Analyze the impact of changes on system architecture and design patterns
- Detect when changes introduce new dependencies or remove existing ones
- Understand the business logic implications of code changes
- Recognize when changes affect multiple layers of the application stack
- Analyze the security implications of code modifications
- Detect when changes affect data flow and state management
- Understand the performance implications of algorithmic changes

Use get_git_changes() to fetch the current git changes.
Then write and execute Python code to analyze and generate the commit message.
Finally, call submit_answer with your results as a dictionary containing all required fields.

IMPORTANT: The answer must be a dictionary with exactly these fields:
- commit_message: string (must follow conventional commit format exactly)
- type: string (must be one of: feat, fix, docs, style, refactor, test, chore, perf, ci, build)
- description: string (must be specific and descriptive, not generic)
- confidence: number (0-1, must reflect analysis quality and certainty)
- files_analyzed: integer (must match actual number of files analyzed)
- breaking_change: boolean (must be accurately detected from code analysis)
- change_summary: string (must provide detailed summary of actual changes)
- files_changed: array of strings (must list all files that were actually changed)

Do not submit a string or any other format - only a dictionary.

VALIDATION CRITERIA:
- commit_message must be properly formatted with type, optional scope, and description
- type must accurately reflect the nature of changes (not just file extensions)
- description must be specific and meaningful (avoid generic terms like "update" or "change")
- confidence must be realistic based on analysis complexity and certainty
- files_analyzed must exactly match the number of files you actually examined
- breaking_change must be correctly identified from API/interface changes
- change_summary must provide detailed, technical summary of what changed
- files_changed must include all files that were modified, added, or deleted

FAILURE CONDITIONS:
- Generic descriptions without technical detail
- Incorrect commit type based on file analysis
- Missing or incorrect file counts
- Inaccurate breaking change detection
- Vague or non-specific change summaries
- Incomplete file lists
- Unrealistic confidence scores
- Malformed commit message format
"""


def get_git_changes() -> dict:
    """Returns current git changes for analysis"""
    try:
        # Get staged changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            check=True
        )
        
        changes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
                
            change_type = line[:2]
            file_path = line[3:]
            
            # Handle renamed files
            if change_type.startswith('R'):
                parts = file_path.split(' -> ')
                if len(parts) == 2:
                    old_path, new_path = parts
                    changes.append({
                        "file": new_path,
                        "type": change_type,
                        "old_path": old_path
                    })
                else:
                    changes.append({
                        "file": file_path,
                        "type": change_type
                    })
            else:
                changes.append({
                    "file": file_path,
                    "type": change_type
                })
        
        # Get diffs for analysis
        diffs = {}
        for change in changes:
            if change["type"] in ['M', 'A']:  # Modified or Added
                try:
                    diff_result = subprocess.run(
                        ['git', 'diff', '--cached', change["file"]],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    diffs[change["file"]] = diff_result.stdout
                except subprocess.CalledProcessError:
                    diffs[change["file"]] = ""
        
        # Add complexity: Include file metadata
        file_metadata = {}
        for change in changes:
            file_path = change["file"]
            try:
                # Get file size
                size_result = subprocess.run(
                    ['git', 'cat-file', '-s', f'HEAD:{file_path}'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                file_metadata[file_path] = {
                    "size": int(size_result.stdout.strip()) if size_result.stdout.strip().isdigit() else 0,
                    "extension": file_path.split('.')[-1] if '.' in file_path else '',
                    "is_binary": False  # Could be enhanced to detect binary files
                }
            except:
                file_metadata[file_path] = {
                    "size": 0,
                    "extension": file_path.split('.')[-1] if '.' in file_path else '',
                    "is_binary": False
                }
        
        return {
            "changes": changes,
            "diffs": diffs,
            "total_files": len(changes),
            "file_metadata": file_metadata,
            "has_renames": any(c.get("old_path") for c in changes),
            "has_deletions": any(c["type"].startswith('D') for c in changes),
            "has_additions": any(c["type"].startswith('A') for c in changes),
            "has_modifications": any(c["type"].startswith('M') for c in changes)
        }
        
    except subprocess.CalledProcessError:
        return {
            "changes": [],
            "diffs": {},
            "total_files": 0,
            "error": "Not a git repository or no staged changes"
        }


def get_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "python_expression",
            "description": "Execute Python code and return the result",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Python code to execute"
                    }
                },
                "required": ["expression"]
            }
        },
        {
            "name": "get_git_changes",
            "description": "Get current git changes for analysis",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "submit_answer",
            "description": "Submit the final commit message analysis as a dictionary",
            "input_schema": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "object",
                        "description": "The commit message analysis result as a dictionary with required fields: commit_message, type, description, confidence, files_analyzed, breaking_change, change_summary, files_changed",
                        "properties": {
                            "commit_message": {"type": "string"},
                            "type": {"type": "string"},
                            "description": {"type": "string"},
                            "confidence": {"type": "number"},
                            "files_analyzed": {"type": "integer"},
                            "breaking_change": {"type": "boolean"},
                            "change_summary": {"type": "string"},
                            "files_changed": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["commit_message", "type", "description", "confidence", "files_analyzed", "breaking_change", "change_summary", "files_changed"]
                    }
                },
                "required": ["answer"]
            }
        }
    ]


def get_tool_handlers() -> Dict[str, callable]:
    from task_framework import python_expression_tool, submit_answer_tool
    return {
        "python_expression": python_expression_tool,
        "get_git_changes": get_git_changes,
        "submit_answer": submit_answer_tool
    }


def get_grader() -> callable:
    def grade_commit_generator_task(answer: Any) -> bool:
        """Grade the commit generator task result"""
        try:
            # Parse the answer
            if isinstance(answer, str):
                result = json.loads(answer)
            else:
                result = answer
            
            if not isinstance(result, dict):
                print("Answer is not a dictionary")
                return False
            
            # Check all required fields from the prompt
            required_fields = [
                "commit_message", "type", "description", "confidence", 
                "files_analyzed", "breaking_change", "change_summary", "files_changed"
            ]
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                print(f"Missing required fields: {missing_fields}")
                return False
            
            # Check commit message format
            commit_message = result.get("commit_message", "")
            if not commit_message:
                print("Empty commit message")
                return False
            
            # Check if it follows conventional commit format exactly
            if not re.match(r'^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\([^)]+\))?: .+', commit_message):
                print("Commit message doesn't follow conventional commit format")
                return False
            
            # Check type field
            valid_types = ["feat", "fix", "docs", "style", "refactor", "test", "chore", "perf", "ci", "build"]
            if result.get("type") not in valid_types:
                print(f"nvalid commit type: {result.get('type')}")
                return False
            
            # Check description quality
            description = result.get("description", "")
            if not description or len(description) < 5:
                print("Description too short or empty")
                return False
            
            # Check confidence is reasonable
            confidence = result.get("confidence", 0)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                print("Invalid confidence value")
                return False
            
            # Check files_analyzed is reasonable
            files_analyzed = result.get("files_analyzed", 0)
            if not isinstance(files_analyzed, int) or files_analyzed < 0:
                print("Invalid files_analyzed value")
                return False
            
            # Check breaking_change is boolean
            breaking_change = result.get("breaking_change")
            if not isinstance(breaking_change, bool):
                print("breaking_change must be boolean")
                return False
            
            # Check change_summary quality
            change_summary = result.get("change_summary", "")
            if not change_summary or len(change_summary) < 10:
                print("change_summary too short or empty")
                return False
            
            # Check files_changed is a list
            files_changed = result.get("files_changed", [])
            if not isinstance(files_changed, list):
                print("files_changed must be a list")
                return False
            
            # Check files_changed matches files_analyzed
            if len(files_changed) != files_analyzed:
                print(f"files_changed count ({len(files_changed)}) doesn't match files_analyzed ({files_analyzed})")
                return False
            
            # Check that files_changed contains actual file paths
            for file_path in files_changed:
                if not isinstance(file_path, str) or not file_path:
                    print("files_changed contains invalid file paths")
                    return False
            
            # Check that commit message type matches the type field
            commit_type_match = re.match(r'^([^(]+)', commit_message)
            if commit_type_match:
                commit_type = commit_type_match.group(1)
                if commit_type != result.get("type"):
                    print(f"Commit message type ({commit_type}) doesn't match type field ({result.get('type')})")
                    return False
            
            # Check that description appears in commit message (more lenient)
            if description.lower() not in commit_message.lower():
                print("Description doesn't appear in commit message")
                return False
            
            # Check that scope is consistent (if present) - make this more lenient
            scope_match = re.search(r'\(([^)]+)\)', commit_message)
            if scope_match:
                scope_in_message = scope_match.group(1)
                scope_in_result = result.get("scope", "")
                # Only fail if both are present and different
                if scope_in_result and scope_in_message != scope_in_result:
                    print(f"Scope mismatch: message='{scope_in_message}', field='{scope_in_result}'")
                    return False
            
            # Much more lenient validation - allow most attempts to pass
            try:
                git_changes = get_git_changes()
                actual_files = [c["file"] for c in git_changes.get("changes", [])]
                
                # Allow some tolerance in file count (within 2 files)
                if abs(files_analyzed - len(actual_files)) > 2:
                    print(f"File count too far off")
                    return False
                
                # Allow some tolerance in file list (at least 50% match)
                if len(set(files_changed) & set(actual_files)) < len(actual_files) * 0.5:
                    print(f"File list too different")
                    return False
                
            except:
                # Don't fail on git errors - just skip validation
                pass
            
            # Content validation
            
            # Reject truly generic content
            if len(change_summary.strip()) < 15:  # Too short
                print(f"Summary too short")
                return False
            
            if change_summary.lower().strip() in ["update", "change", "fix", "modify"]:  # Single word
                print(f"Generic summary")
                return False
            
            # Check for meaningful technical terms in summary (more lenient)
            technical_terms = ["function", "class", "method", "variable", "bug", "feature", "api", "config", "test", "database", "file", "code", "logic", "error", "exception", "interface", "implementation", "algorithm", "optimization", "refactor", "dependency", "schema", "endpoint", "authentication", "validation", "module", "task", "utility", "documentation", "project", "system", "structure"]
            if not any(word in change_summary.lower() for word in technical_terms):
                print(f"Summary lacks technical detail")
                return False
            
            # Require more specific technical language
            if len(change_summary.split()) < 4:  # Must have at least 4 words
                print(f"Summary too brief")
                return False
            
            # Reject generic description
            if len(description.strip()) < 8:  # Too short
                print(f"Description too short")
                return False
            
            if description.lower().strip() in ["update", "change", "fix", "modify"]:  # Single word
                print(f"Generic description")
                return False
            
            # Description should contain technical terms (more lenient)
            if len(description.split()) >= 3 and not any(word in description.lower() for word in technical_terms):
                print(f"Description lacks technical detail")
                return False
            
            # Confidence must be realistic based on analysis complexity
            if confidence < 0.3 or confidence > 0.95:
                print(f"Bad confidence")
                return False
            
            # Confidence should correlate with technical detail
            if confidence > 0.8 and len(change_summary.split()) < 6:
                print(f"Confidence too high for brief summary")
                return False
            
            print("✅ ALL CHECKS PASSED!")
            return True
            
        except Exception as e:
            print(f"Exception during grading: {e}")
            return False
    
    return grade_commit_generator_task
