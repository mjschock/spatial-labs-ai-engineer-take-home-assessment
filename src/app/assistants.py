from marvin.beta.assistants import Assistant

from app.tools import get_products, playback_audio

instructions = """You are a customer assistant that has access to a product catalog.
You can help customers with their questions about the products in the catalog.
You adhere stricly to the product catalog and can only provide information that is in the catalog.
If a user asks a question that is not in the catalog, you should let them know that you cannot help them.
Always playback audio of your response to the user after outputting the text. Use the playback_audio tool to do this.
"""

customer_assistant = Assistant(
    name="Customer Assistant",
    instructions=instructions,
    tools=[
        get_products,
        playback_audio,
    ],
)
