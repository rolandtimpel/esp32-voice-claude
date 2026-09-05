from anthropic import Anthropic
from config.logger import setup_logging
from core.utils.util import check_model_key
from core.providers.llm.base import LLMProviderBase

TAG = __name__
logger = setup_logging()


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
        self.max_tokens = int(config.get("max_tokens", 1024))
        self.temperature = float(config.get("temperature", 0.7))
        base_url = config.get("base_url") or config.get("url")

        model_key_msg = check_model_key("LLM", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)

        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
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

    def response(self, session_id, dialogue, **kwargs):
        system_prompt, messages = self._split_system_and_messages(dialogue)
        if not messages:
            messages = [{"role": "user", "content": ""}]

        request_params = {
            "model": self.model_name,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
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
