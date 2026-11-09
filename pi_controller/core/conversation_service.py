
from pi_controller.clients.ai_engine import AIEngineClient
from pi_controller.core.conversation_store import ConversationStore
from pi_controller.core.models import ChatMessageRole
from shared.contracts import ChatRequest, ChatResponse


class ConversationService:
    def __init__(self, conversation_store: ConversationStore, ai_engine_client: AIEngineClient):
        self.conversation_store = conversation_store
        self.ai_engine_client = ai_engine_client

    async def chat(self, request: ChatRequest) -> ChatResponse:
        # Save the user's message to the conversation store
        self.conversation_store.add_message(
            session_id=request.session_id,
            role=ChatMessageRole.USER,
            content=request.messages[0].content,
            timestamp=request.timestamp
        )

        # Get the conversation history for the session
        messages = self.conversation_store.get_messages(session_id=request.session_id, limit=20)
        messages.extend(request.messages)

        # Prepare the request for the AI engine
        ai_request = ChatRequest(
            session_id=request.session_id,
            messages=messages,
            timestamp=request.timestamp
        )

        # Send the request to the AI engine and get the response
        ai_response = await self.ai_engine_client.chat(ai_request)

        # Save the AI's response to the conversation store
        self.conversation_store.add_message(
            session_id=request.session_id,
            role=ChatMessageRole.ASSISTANT,
            content=ai_response.response,
            timestamp=ai_response.timestamp
        )

        return ai_response