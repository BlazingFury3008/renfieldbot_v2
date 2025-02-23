from openai import OpenAI
from dotenv import load_dotenv
import os
from discord import Interaction

def gpt_response(message : str, interaction:Interaction, content: str | None):
    """Sends a message to the OpenAI server and gets a response from a Model

    Args:
        message (str): Message to be sent to the GPT Model
        interaction (Interaction): Discord Interaction Variable
        content (str | None): Custom content for the GPT Model to use to set context
    """
    load_dotenv()
    MODEL = os.getenv("OPENAI_MODEL")
    
    if content is None:
        content = f"You are Renfield, the Vampire Ghoul. You serve {interaction.user.name}"
    
    client = OpenAI()
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": content},
            {
                "role": "user",
                "content":message
            }
        ],
       
    )

    return(completion.choices[0].message.content)