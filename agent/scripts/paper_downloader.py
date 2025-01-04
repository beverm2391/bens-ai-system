import os
import re
import requests
from pathlib import Path
from tqdm import tqdm
import time

OUTPUT_DIR = Path("data/agent-papers")

# The content we know works
SAMPLE_CONTENT = """
DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines  Paper• 2310.03714
ReST meets ReAct: Self-Improvement for Multi-Step Reasoning LLM Agent  Paper• 2312.10003
AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework  Paper• 2308.08155
GAIA: a benchmark for General AI Assistants  Paper• 2311.12983
Self-Discover: Large Language Models Self-Compose Reasoning Structures  Paper• 2402.03620
OS-Copilot: Towards Generalist Computer Agents with Self-Improvement  Paper• 2402.07456
Self-Refine: Iterative Refinement with Self-Feedback  Paper• 2303.17651
Reflexion: Language Agents with Verbal Reinforcement Learning  Paper• 2303.11366
Gorilla: Large Language Model Connected with Massive APIs  Paper• 2305.15334
MM-REACT: Prompting ChatGPT for Multimodal Reasoning and Action  Paper• 2303.11381
HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in HuggingFace  Paper• 2303.17580
Communicative Agents for Software Development  Paper• 2307.07924
More Agents Is All You Need  Paper• 2402.05120
ReAct: Synergizing Reasoning and Acting in Language Models  Paper• 2210.03629
Executable Code Actions Elicit Better LLM Agents  Paper• 2402.01030
SWE-bench: Can Language Models Resolve Real-World GitHub Issues?  Paper• 2310.06770
DynaSaur: Large Language Agents Beyond Predefined Actions  Paper• 2411.01747
ShowUI: One Vision-Language-Action Model for GUI Visual Agent  Paper• 2411.17465
Aguvis: Unified Pure Vision Agents for Autonomous GUI Interaction  Paper• 2412.04454
If LLM Is the Wizard, Then Code Is the Wand: A Survey on How Code Empowers Large Language Models to Serve as Intelligent Agents  Paper• 2401.00812
"""

def extract_arxiv_ids(content):
    pattern = r"Paper•\s*(\d{4}\.\d{5})"
    return re.findall(pattern, content)

def download_paper(arxiv_id, output_dir):
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    output_path = output_dir / f"{arxiv_id}.pdf"
    
    if output_path.exists():
        print(f"Skipping {arxiv_id} - already exists")
        return output_path
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=arxiv_id) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
    
    # Be nice to arXiv
    time.sleep(1)
    return output_path

def main():
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Extracting arXiv IDs...")
    arxiv_ids = extract_arxiv_ids(SAMPLE_CONTENT)
    print(f"Found {len(arxiv_ids)} papers")
    
    for arxiv_id in arxiv_ids:
        try:
            print(f"\nDownloading {arxiv_id}")
            download_paper(arxiv_id, OUTPUT_DIR)
        except Exception as e:
            print(f"Error downloading {arxiv_id}: {e}")
            continue

if __name__ == "__main__":
    main() 