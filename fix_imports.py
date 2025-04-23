#!/usr/bin/env python
"""
Import fixer for the Malaysian Lead Generator project.

This script recursively scans Python files in the project directory and fixes import
issues such as missing imports, unused imports, and improper import order.
It also applies consistent import styling according to PEP 8 guidelines.
"""

import os
import sys
import re
import ast
import difflib
import logging
import argparse
from typing import List, Dict, Set, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global constants
STANDARD_LIBRARY_MODULES = {
    "abc", "argparse", "asyncio", "base64", "collections", "configparser", 
    "contextlib", "copy", "csv", "datetime", "decimal", "difflib", "enum",
    "functools", "glob", "hashlib", "hmac", "importlib", "inspect", "io",
    "itertools", "json", "logging", "math", "mimetypes", "os", "pathlib",
    "pickle", "random", "re", "shutil", "signal", "socket", "sqlite3",
    "string", "subprocess", "sys", "tempfile", "threading", "time",
    "traceback", "types", "typing", "uuid", "warnings", "zipfile"
}

THIRD_PARTY_MODULES = {
    "aiohttp", "azure", "beautifulsoup4", "bs4", "cryptography", "django",
    "fastapi", "flask", "httpx", "matplotlib", "numpy", "pandas", "pydantic",
    "pytest", "requests", "selenium", "sqlalchemy", "starlette", "uvicorn"
}

PROJECT_MODULES = {
    "lead_generator"
}

# Import sorting order: standard library, third-party, local application/library
IMPORT_ORDER = [
    lambda mod: mod.split('.')[0] in STANDARD_LIBRARY_MODULES,
    lambda mod: mod.split('.')[0] in THIRD_PARTY_MODULES,
    lambda mod: mod.split('.')[0] in PROJECT_MODULES,
    lambda mod: True  # Everything else
]

class ImportFixer:
    def __init__(self, root_dir: str, dry_run: bool = False, verbose: bool = False):
        self.root_dir = os.path.abspath(root_dir)
        self.dry_run = dry_run
        self.verbose = verbose
        
    def scan_directory(self) -> List[str]:
        """Scan directory for Python files."""
        python_files = []
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(python_files)} Python files")
        return python_files
    
    def analyze_file(self, file_path: str) -> Dict:
        """
        Analyze a Python file for imports.
        
        Returns a dictionary with:
        - used_symbols: Set of used symbols
        - imports: List of Import objects
        - import_lines: Original import lines with line numbers
        - errors: List of import-related errors
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return {
                'used_symbols': set(),
                'imports': [],
                'import_lines': [],
                'errors': [f"Syntax error: {e}"]
            }
        
        # Get all imports
        imports = []
        import_lines = []
        
        line_numbers = []
        for i, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                import_lines.append((i, line))
                line_numbers.append(i)
        
        # Extract imports using AST
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        'type': 'import',
                        'name': name.name,
                        'asname': name.asname,
                        'lineno': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for name in node.names:
                    imports.append({
                        'type': 'from',
                        'module': module,
                        'name': name.name,
                        'asname': name.asname,
                        'lineno': node.lineno
                    })
        
        # Find used symbols
        used_symbols = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_symbols.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                if isinstance(node.value, ast.Name):
                    used_symbols.add(node.value.id)
        
        # Identify unused imports
        errors = []
        for imp in imports:
            symbol = imp['asname'] or imp['name']
            if imp['type'] == 'import' and symbol not in used_symbols and '.' not in imp['name']:
                errors.append(f"Unused import: {imp['name']}")
        
        return {
            'used_symbols': used_symbols,
            'imports': imports,
            'import_lines': import_lines,
            'errors': errors
        }
    
    def fix_imports(self, file_path: str) -> Tuple[bool, List[str]]:
        """Fix imports in a Python file."""
        analysis = self.analyze_file(file_path)
        if 'errors' in analysis and analysis['errors']:
            if self.verbose:
                for error in analysis['errors']:
                    logger.warning(f"{file_path}: {error}")
            
            # Organize imports
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()
            
            # Extract import lines
            import_lines = analysis['import_lines']
            if not import_lines:
                return False, []
            
            # Get line numbers and import statements
            line_nums = [line[0] for line in import_lines]
            import_stmts = [line[1] for line in import_lines]
            
            # Sort imports
            sorted_imports = self.sort_imports(import_stmts)
            
            # Replace imports in content
            if sorted_imports != import_stmts:
                # Create a new content with sorted imports
                new_content = content.copy()
                
                # Replace imports from bottom to top to avoid line number issues
                for i in range(len(line_nums) - 1, -1, -1):
                    line_num = line_nums[i] - 1  # Convert to 0-indexed
                    if i < len(sorted_imports):
                        new_content[line_num] = sorted_imports[i] + '\n'
                    else:
                        # Remove extra imports
                        new_content[line_num] = ''
                
                # Only add new imports if they're not already there
                if len(sorted_imports) > len(import_stmts):
                    for i in range(len(import_stmts), len(sorted_imports)):
                        # Add after the last import
                        last_line = line_nums[-1]
                        new_content.insert(last_line, sorted_imports[i] + '\n')
                
                # Show diff if verbose
                if self.verbose:
                    diff = difflib.unified_diff(
                        content, new_content, 
                        fromfile=f"a/{file_path}", 
                        tofile=f"b/{file_path}"
                    )
                    for line in diff:
                        print(line, end='')
                
                # Write changes if not dry run
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_content)
                    
                    return True, analysis['errors']
            
            return False, analysis['errors']
        
        return False, []
    
    def sort_imports(self, imports: List[str]) -> List[str]:
        """Sort import statements according to PEP 8."""
        # Group imports
        grouped_imports = [[] for _ in range(len(IMPORT_ORDER))]
        
        for imp in imports:
            if imp.startswith('from '):
                # Extract the module part from "from X import Y"
                module = imp.split('import')[0].replace('from', '').strip()
            else:
                # Extract the module part from "import X"
                module = imp.replace('import', '').strip().split(' as ')[0]
            
            # Find the appropriate group
            for i, group_filter in enumerate(IMPORT_ORDER):
                if group_filter(module):
                    grouped_imports[i].append(imp)
                    break
        
        # Sort each group
        for i in range(len(grouped_imports)):
            grouped_imports[i].sort()
        
        # Flatten with blank lines between groups
        result = []
        for group in grouped_imports:
            if group and result:  # Add blank line between non-empty groups
                result.append('')
            result.extend(group)
        
        return result
    
    def run(self):
        """Run the import fixer on all Python files."""
        python_files = self.scan_directory()
        fixed_files = 0
        error_files = 0
        
        for file_path in python_files:
            try:
                fixed, errors = self.fix_imports(file_path)
                if fixed:
                    fixed_files += 1
                    logger.info(f"Fixed imports in {file_path}")
                if errors:
                    error_files += 1
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                error_files += 1
        
        mode = "DRY RUN" if self.dry_run else "FIXED"
        logger.info(f"{mode}: {fixed_files} files fixed, {error_files} files with errors")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fix Python import issues in a project"
    )
    parser.add_argument(
        "--directory", "-d", 
        default=".", 
        help="Root directory to scan (default: current directory)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be fixed without making changes"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    fixer = ImportFixer(
        root_dir=args.directory,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    fixer.run() 