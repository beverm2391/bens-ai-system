#!/usr/bin/env python3
"""
Script for updating dir.md with current project structure.
"""
import os
import re
from typing import Dict, List, Optional

def get_comments(content: str) -> Dict[str, str]:
    """Extract existing comments from dir.md."""
    comments = {}
    lines = content.split('\n')
    for line in lines:
        if '#' in line:
            path = line.split('#')[0].strip()
            comment = line.split('#')[1].strip()
            if path.endswith('/') or path in ['dir.md']:
                comments[path] = comment
    return comments

def should_ignore(path: str) -> bool:
    """Check if path should be ignored."""
    ignore_patterns = [
        r'\.git',
        r'\.pytest_cache',
        r'__pycache__',
        r'\.pyc$',
        r'\.pyo$',
        r'\.pyd$',
        r'\.DS_Store',
        r'\.env',
        r'venv',
    ]
    return any(re.search(pattern, path) for pattern in ignore_patterns)

def generate_tree(
    start_path: str = ".",
    level: int = 0,
    comments: Optional[Dict[str, str]] = None
) -> List[str]:
    """Generate tree structure with comments."""
    if comments is None:
        comments = {}
        
    prefix = "│   " * level
    output = []
    
    try:
        entries = sorted(os.listdir(start_path))
    except PermissionError:
        return output
        
    for i, entry in enumerate(entries):
        if should_ignore(entry):
            continue
            
        path = os.path.join(start_path, entry)
        rel_path = os.path.relpath(path, ".")
        is_last = i == len(entries) - 1
        
        # Format entry
        if is_last:
            branch = "└── "
        else:
            branch = "├── "
            
        # Add comment if exists
        entry_key = f"{entry}/" if os.path.isdir(path) else entry
        comment = comments.get(entry_key, "")
        comment_str = f" # {comment}" if comment else ""
            
        output.append(f"{prefix}{branch}{entry}{comment_str}")
        
        if os.path.isdir(path):
            subtree = generate_tree(path, level + 1, comments)
            output.extend(subtree)
            
    return output

def update_dir_md():
    """Update dir.md with current structure."""
    dir_md_path = "dir.md"
    
    # Read existing file to preserve comments
    try:
        with open(dir_md_path, 'r') as f:
            existing_content = f.read()
        comments = get_comments(existing_content)
    except FileNotFoundError:
        comments = {}
    
    # Generate new tree
    tree_lines = generate_tree(comments=comments)
    
    # Format output
    output = "# Directory Structure\n\n```\n.\n"
    output += "\n".join(tree_lines)
    output += "\n```"
    
    # Write updated content
    with open(dir_md_path, 'w') as f:
        f.write(output)
    
    print(f"Updated {dir_md_path}")

if __name__ == "__main__":
    update_dir_md() 