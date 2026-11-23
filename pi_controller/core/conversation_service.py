
from typing import List

from pi_controller.clients.ai_engine import AIEngineClient
from pi_controller.core.command_router import CommandRouter
from pi_controller.core.conversation_store import ConversationStore
from shared.contracts import AIEngineChatRequest, AssistantChatRequest, ChatMessage, ChatMessageRole, ChatMessageSchema, ChatResponse
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(
            self,
            conversation_store: ConversationStore,
            ai_engine_client: AIEngineClient,
            command_router: CommandRouter
        ):
        self.conversation_store = conversation_store
        self.ai_engine_client = ai_engine_client
        self.command_router = command_router

    async def chat(self, request: AssistantChatRequest) -> ChatResponse:
        # Save the user's message to the conversation store
        self.conversation_store.add_message(
            session_id=request.session_id,
            role=ChatMessageRole.USER,
            content=request.message,
        )

        if self.command_router:
            handler_response = self.command_router.handle(request.message)
            logger.info(f"Command router response: {handler_response}")
            if handler_response is not None:
                # If the command router handled the message, return a response indicating that
                response = ChatResponse(
                    session_id=request.session_id,
                    response=handler_response,
                )

                self.conversation_store.add_message(
                    session_id=request.session_id,
                    role=ChatMessageRole.ASSISTANT,
                    content=response.response,
                    timestamp=response.timestamp.isoformat(),
                )
                return response
        else:
            logger.info("Command router is not initialized. Skipping command handling.")

        # Get the conversation history for the session
        messages: List[ChatMessageSchema] = self.conversation_store.get_messages(session_id=request.session_id, limit=20)

        request_messages = [
            ChatMessage(
                role=message.role,
                content=message.content
            )
            for message in messages
        ]

        # print(f"Conversation history for session {request.session_id}:")
        # for msg in request_messages:
        #     print(f"{msg.role}: {msg.content}")

        # Prepare the request for the AI engine
        ai_request = AIEngineChatRequest(
            session_id=request.session_id,
            messages=request_messages,
        )

        # Send the request to the AI engine and get the response
        try:
            ai_response = await self.ai_engine_client.chat(ai_request)
        except Exception as e:
            logger.error(f"Error in generating response from LLM: {e}")
            raise e

        if not ai_response.response or not ai_response.response.strip():
            logger.error("AI Engine returned an empty response.")
            raise RuntimeError("AI Engine returned an empty response.")

        # Save the AI's response to the conversation store
        self.conversation_store.add_message(
            session_id=request.session_id,
            role=ChatMessageRole.ASSISTANT,
            content=ai_response.response,
            timestamp=ai_response.timestamp.isoformat()
        )

        return ai_response