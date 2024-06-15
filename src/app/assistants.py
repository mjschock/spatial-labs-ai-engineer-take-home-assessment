from marvin.beta.assistants import Assistant, Thread, Run

from app.tools import get_products, playback_audio

instructions = """You are a customer assistant that has access to a product catalog.
You can help customers with their questions about the products in the catalog.
You adhere stricly to the product catalog and can only provide information that is in the catalog.
If a user asks a question that is not in the catalog, you should let them know that you cannot help them.
Always playback audio of your response to the user after outputting the text. Use the playback_audio tool to do this.
"""

class CustomerAssistant(Assistant):
    def pre_run_hook(self):
        pass

    def post_run_hook(self, run: "Run"):
        thread_id = run.thread.id

        thread = Thread(id=thread_id)
        messages = thread.get_messages()
        last_message = messages[-1]
        last_message_content_text_value = last_message.content[-1].text.value

        playback_audio(last_message_content_text_value, voice='shimmer')

customer_assistant = CustomerAssistant(
    name="Customer Assistant",
    instructions=instructions,
    tools=[
        get_products,
        # playback_audio,
    ],
)
