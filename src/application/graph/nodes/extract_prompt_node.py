from src.application.graph.message_extractor import extract_prompt_from


def extract_prompt(state):
    user_prompt = extract_prompt_from(state)

    print("🔍 Prompt extracted...")

    return {"user_prompt": user_prompt}
