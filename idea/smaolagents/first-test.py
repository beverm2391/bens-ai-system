from smolagents import CodeAgent, HfApiModel, LiteLLMModel
from huggingface_hub import login, list_models
from transformers import tool
from dotenv import load_dotenv
import os
from huggingface_hub import list_models


load_dotenv()

token = os.getenv("HF_ACCESS_TOKEN")
if not token:
    raise ValueError("HF_ACCESS_TOKEN is not set")


def get_model(
    name: str,
):
    map_ = {
        "sonnet": "anthropic/claude-3-5-sonnet-20240620",
        "haiku": "anthropic/claude-3-haiku-20240307",
    }
    model_id = map_.get(name, None)
    if not model_id:
        raise ValueError(f"Model {name} not found")
    return model_id


@tool
def model_download_tool(task: str) -> str:
    """
    This is a tool that returns the most downloaded model of a given task on the Hugging Face Hub.
    It returns the name of the checkpoint.

    Args:
        task: The task for which
    """
    most_downloaded_model = next(iter(list_models(filter=task, sort="downloads", direction=-1)))
    return most_downloaded_model.id

def main():
    login(token)

    model_id = get_model("sonnet")

    model = LiteLLMModel(model_id=model_id)
    agent = CodeAgent(
        tools=[model_download_tool],
        model=model,
        add_base_tools=True,  # includes DuckDuckGoSearchTool, PythonInterpreterTool, and Transcriber
        additional_authorized_imports=["requests", "bs4"],
    )

    agent.run(
        "Can you give me the name of the model that has the most downloads in the 'text-to-video' task on the Hugging Face Hub?"
    )


if __name__ == "__main__":
    main()
