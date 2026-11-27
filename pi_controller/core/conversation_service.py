
from typing import List

from pi_controller.clients.ai_engine import AIEngineClient
from pi_controller.core.command_router import CommandRouter
from pi_controller.core.conversation_store import ConversationStore
from pi_controller.tools.registry import ToolRegistry
from shared.contracts import AIEngineChatRequest, AssistantChatRequest, ChatMessage, ChatMessageRole, ChatMessageSchema, ChatResponse
import logging
import json
logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(
            self,
            conversation_store: ConversationStore,
            ai_engine_client: AIEngineClient,
            command_router: CommandRouter,
            tool_registry: ToolRegistry
        ):
        self.conversation_store = conversation_store
        self.ai_engine_client = ai_engine_client
        self.command_router = command_router
        self.tool_registry = tool_registry

    async def _call_llm(
        self, 
        messages: list[ChatMessage], 
        request: AssistantChatRequest
    ) -> ChatResponse:
        # Description of all tools
        tools = self.tool_registry.describe_tools()

        MAX_TOOL_ROUNDS = 4
        MAX_TOOL_CALLS = 8
        total_tool_calls = 0
        for round_num in range(MAX_TOOL_ROUNDS + 1):
            ai_response = await self.ai_engine_client.chat(
                AIEngineChatRequest(
                    session_id=request.session_id,
                    messages=messages,
                    tools=tools,
                )
            )

            # No tool calls requested by the model
            if not ai_response.tool_calls:
                response_text = (ai_response.response or "").strip()
                logger.info(f"LLM requested no tool calls. Response: {response_text}")

                
                if not response_text:
                    raise RuntimeError("AI Engine returned an empty response.")

                self.conversation_store.add_message(
                    session_id=request.session_id,
                    role=ChatMessageRole.ASSISTANT,
                    content=response_text,
                    timestamp=ai_response.timestamp.isoformat(),
                )

                return ChatResponse(
                    session_id=request.session_id,
                    response=response_text,
                    timestamp=ai_response.timestamp,
                )          

            logger.info(f"LLM Requested some tool calls: {ai_response.tool_calls}")     
            if round_num == MAX_TOOL_ROUNDS:
                raise RuntimeError("Maximum tool-calling rounds exceeded.")

            # Preserve the assistant's tool-call message for the next LLM request.
            messages.append(
                ChatMessage(
                    role=ChatMessageRole.ASSISTANT,
                    content=ai_response.response or "",
                    thinking=ai_response.thinking,
                    tool_calls=ai_response.tool_calls,
                )
            )

            # Execute requested tools on Pi Core.
            for tool_call in ai_response.tool_calls:
                name = tool_call.function.name
                arguments = tool_call.function.arguments

                if total_tool_calls >= MAX_TOOL_CALLS:
                    logger.info(f"LLM requested more than the no. of tool calls available. Total at: {total_tool_calls}. Requested: {ai_response.tool_calls}")
                    result = {"error": "Maximum tool-call limit reached."}
                else:
                    total_tool_calls += 1

                    try:
                        result = await self.tool_registry.execute(
                            name,
                            arguments,
                        )
                        logger.info(f"Successfully executed tool call: {name}. Total: {total_tool_calls}. Result: {result}")
                    except Exception as exc:
                        logger.exception("Tool execution failed: %s", name)
                        result = {
                            "error": f"Tool execution failed: {type(exc).__name__}"
                        }

                messages.append(
                    ChatMessage(
                        role=ChatMessageRole.TOOL,
                        content=json.dumps(result, ensure_ascii=False),
                        tool_name=name,
                    )
                )
        raise RuntimeError(f"Unable to complete tool-calling interaction. LLM never returned a non-tool call response within allowed: {MAX_TOOL_CALLS}")

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
        messages: List[ChatMessageSchema] = self.conversation_store.get_messages(
            session_id=request.session_id,
            limit=20
        )

        request_messages = [
            ChatMessage(
                role=message.role,
                content=message.content
            )
            for message in messages
        ]

        # Send the request to the AI engine and get the response
        try:
            ai_response = await self._call_llm(
                messages=request_messages, 
                request=request
            )
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