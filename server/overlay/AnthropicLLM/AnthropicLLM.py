from anthropic import Anthropic
from config.logger import setup_logging
from core.utils.util import check_model_key
from core.providers.llm.base import LLMProviderBase

TAG = __name__
logger = setup_logging()


class _ToolCallFunctionDelta:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class _ToolCallDelta:
    """Duck-types the OpenAI streaming tool-call delta shape that
    core.connection._merge_tool_calls expects (.index, .id, .function.name,
    .function.arguments) so we can reuse that logic for Anthropic's
    differently-shaped tool_use streaming events."""

    def __init__(self, index, id, name, arguments):
        self.index = index
        self.id = id
        self.function = _ToolCallFunctionDelta(name, arguments)


class LLMProvider(LLMProviderBase):
    """Anthropic Claude provider for xiaozhi-esp32-server.

    xiaozhi passes dialogue as OpenAI-style {role, content} dicts with role
    in {system, user, assistant}. Anthropic's Messages API instead takes the
    system prompt as its own top-level parameter and only user/assistant
    turns in `messages`, so that split happens here before every call.
    """

    def __init__(self, config):
        self.model_name = config.get("model_name", "claude-sonnet-5")
        self.api_key = config.get("api_key")
        self.workspace_id = config.get("workspace_id")
        self.max_tokens = int(config.get("max_tokens", 1024))
        self.temperature = float(config.get("temperature", 0.7))
        base_url = config.get("base_url") or config.get("url")

        model_key_msg = check_model_key("LLM", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)

        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        if self.workspace_id:
            client_kwargs["default_headers"] = {"anthropic-workspace-id": self.workspace_id}
        self.client = Anthropic(**client_kwargs)

    @staticmethod
    def _split_system_and_messages(dialogue):
        system_parts = []
        messages = []
        for msg in dialogue:
            role = msg.get("role")
            content = msg.get("content", "") or ""
            if role == "system":
                if content:
                    system_parts.append(content)
                continue
            if role not in ("user", "assistant"):
                role = "user"
            messages.append({"role": role, "content": content})
        return "\n\n".join(system_parts), messages

    @staticmethod
    def _to_anthropic_tools(functions):
        """xiaozhi builds `functions` in OpenAI tool-schema form
        ({"type": "function", "function": {name, description, parameters}}).
        Anthropic's Messages API wants {name, description, input_schema}."""
        tools = []
        for f in functions or []:
            fn = f.get("function", f)
            name = fn.get("name")
            if not name:
                continue
            tools.append({
                "name": name,
                "description": fn.get("description", "") or "",
                "input_schema": fn.get("parameters") or {"type": "object", "properties": {}},
            })
        return tools

    def response(self, session_id, dialogue, **kwargs):
        system_prompt, messages = self._split_system_and_messages(dialogue)
        if not messages:
            messages = [{"role": "user", "content": ""}]

        request_params = {
            "model": self.model_name,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": messages,
        }
        if system_prompt:
            request_params["system"] = system_prompt

        try:
            with self.client.messages.stream(**request_params) as stream:
                for text in stream.text_stream:
                    if text:
                        yield text
        except Exception as e:
            logger.bind(tag=TAG).error(f"Anthropic API Fehler: {e}")
            yield "Entschuldigung, bei der Verbindung zu Claude ist gerade ein Fehler aufgetreten."

    def response_with_functions(self, session_id, dialogue, functions=None, **kwargs):
        system_prompt, messages = self._split_system_and_messages(dialogue)
        if not messages:
            messages = [{"role": "user", "content": ""}]

        request_params = {
            "model": self.model_name,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": messages,
        }
        if system_prompt:
            request_params["system"] = system_prompt

        tools = self._to_anthropic_tools(functions)
        if tools:
            request_params["tools"] = tools

        try:
            with self.client.messages.stream(**request_params) as stream:
                tool_use_indices = {}  # Anthropic content-block index -> our sequential tool index
                for event in stream:
                    event_type = getattr(event, "type", None)

                    if event_type == "content_block_start":
                        block = event.content_block
                        if getattr(block, "type", None) == "tool_use":
                            seq_index = len(tool_use_indices)
                            tool_use_indices[event.index] = seq_index
                            yield "", [
                                _ToolCallDelta(seq_index, block.id, block.name, "")
                            ]

                    elif event_type == "content_block_delta":
                        delta = event.delta
                        delta_type = getattr(delta, "type", None)
                        if delta_type == "text_delta":
                            yield delta.text, None
                        elif delta_type == "input_json_delta":
                            seq_index = tool_use_indices.get(event.index)
                            if seq_index is not None:
                                yield "", [
                                    _ToolCallDelta(seq_index, None, None, delta.partial_json)
                                ]
        except Exception as e:
            logger.bind(tag=TAG).error(f"Anthropic API Fehler: {e}")
            yield "Entschuldigung, bei der Verbindung zu Claude ist gerade ein Fehler aufgetreten.", None
