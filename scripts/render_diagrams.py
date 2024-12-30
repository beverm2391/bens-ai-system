import re
import os
import subprocess
import tempfile
from pathlib import Path

# Add new constants at the top
DEFAULT_INPUT_DIR = Path('docs/ai-system/diagrams')
DEFAULT_OUTPUT_DIR = Path('docs/ai-system/diagrams/images')

def extract_mermaid(md_file):
    """Extract mermaid diagram content from markdown file."""
    with open(md_file, 'r') as f:
        content = f.read()
    
    # Find content between ```mermaid and ```
    pattern = r'```mermaid\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    return matches

def render_diagram(mermaid_content, output_path):
    """Render a single mermaid diagram to PNG using mermaid-cli."""
    # Create temporary file for mermaid content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as tmp:
        tmp.write(mermaid_content)
        tmp_path = tmp.name
    
    try:
        # Run mmdc command with high quality settings
        subprocess.run([
            'mmdc',
            '-i', tmp_path,
            '-o', str(output_path),
            '-b', 'transparent',  # transparent background
            '-w', '2048',  # width
            '-H', '2048',  # height
            '-s', '2'  # scale factor
        ], check=True)
    finally:
        # Clean up temp file
        os.unlink(tmp_path)

def process_file(md_file, output_dir):
    """Process a single markdown file containing mermaid diagrams."""
    diagrams = extract_mermaid(md_file)
    if not diagrams:
        print(f"No mermaid diagrams found in {md_file}")
        return
    
    # Use passed output_dir instead of hardcoded path
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Render each diagram found
    for i, diagram in enumerate(diagrams):
        output_path = output_dir / f"{Path(md_file).stem}_{i}.png"
        try:
            render_diagram(diagram, output_path)
            print(f"Rendered diagram to {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error rendering diagram: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

def main(input_dir=DEFAULT_INPUT_DIR, output_dir=DEFAULT_OUTPUT_DIR):
    # Check if mermaid-cli is installed
    try:
        subprocess.run(['mmdc', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: mermaid-cli not found. Please install it with: npm install -g @mermaid-js/mermaid-cli")
        return

    # Use parameterized input_dir
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    for md_file in input_dir.glob('*.md'):
        print(f"\nProcessing {md_file}...")
        process_file(md_file, output_dir)

if __name__ == '__main__':
    # Can be called with default values or override them
    main() 