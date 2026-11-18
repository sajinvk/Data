import os
from types import SimpleNamespace
from typing import Any

import boto3


class Claude:
    def __init__(self, model: str):
        # Bedrock Converse API. Credentials come from AWS_PROFILE or the default AWS chain.
        region = os.getenv("AWS_REGION", "ap-southeast-2")
        session = boto3.Session(
            profile_name=os.getenv("AWS_PROFILE") or None,
            region_name=region,
        )
        self.client = session.client("bedrock-runtime", region_name=region)
        self.model = model

    @staticmethod
    def _get(block: Any, key: str, default=None):
        if isinstance(block, dict):
            return block.get(key, default)
        return getattr(block, key, default)

    def add_user_message(self, messages: list, message):
        user_message = {
            "role": "user",
            "content": getattr(message, "content", message),
        }
        messages.append(user_message)

    def add_assistant_message(self, messages: list, message):
        assistant_message = {
            "role": "assistant",
            "content": getattr(message, "content", message),
        }
        messages.append(assistant_message)

    def text_from_message(self, message) -> str:
        return "\n".join(
            [block.text for block in message.content if block.type == "text"]
        )

    def _to_converse_content(self, content) -> list[dict]:
        """Converts app message content (str or Anthropic-style blocks) to Converse content blocks."""
        if isinstance(content, str):
            return [{"text": content}]

        blocks: list[dict] = []
        for block in content:
            block_type = self._get(block, "type")
            if block_type == "text":
                text = self._get(block, "text")
                if text:
                    blocks.append({"text": text})
            elif block_type == "tool_use":
                blocks.append(
                    {
                        "toolUse": {
                            "toolUseId": self._get(block, "id"),
                            "name": self._get(block, "name"),
                            "input": self._get(block, "input") or {},
                        }
                    }
                )
            elif block_type == "tool_result":
                blocks.append(
                    {
                        "toolResult": {
                            "toolUseId": self._get(block, "tool_use_id"),
                            "content": [
                                {"text": str(self._get(block, "content", ""))}
                            ],
                            "status": "error"
                            if self._get(block, "is_error")
                            else "success",
                        }
                    }
                )
        return blocks

    @staticmethod
    def _to_converse_tools(tools: list[dict]) -> dict:
        return {
            "tools": [
                {
                    "toolSpec": {
                        "name": tool["name"],
                        "description": tool.get("description") or "",
                        "inputSchema": {
                            "json": tool.get("input_schema")
                            or {"type": "object", "properties": {}}
                        },
                    }
                }
                for tool in tools
            ]
        }

    def _from_converse(self, response: dict) -> SimpleNamespace:
        """Maps a Converse response to an object with the .content / .stop_reason shape the app uses."""
        blocks = []
        for block in response["output"]["message"].get("content", []):
            if "text" in block:
                blocks.append(SimpleNamespace(type="text", text=block["text"]))
            elif "toolUse" in block:
                tool_use = block["toolUse"]
                blocks.append(
                    SimpleNamespace(
                        type="tool_use",
                        id=tool_use["toolUseId"],
                        name=tool_use["name"],
                        input=tool_use.get("input", {}),
                    )
                )
        return SimpleNamespace(
            role="assistant",
            content=blocks,
            stop_reason=response.get("stopReason"),
        )

    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=[],
        tools=None,
        thinking=False,
        thinking_budget=1024,
    ):
        inference_config: dict[str, Any] = {
            "temperature": temperature,
            "maxTokens": 8000,
        }
        if stop_sequences:
            inference_config["stopSequences"] = list(stop_sequences)

        params: dict[str, Any] = {
            "modelId": self.model,
            "messages": [
                {
                    "role": message["role"],
                    "content": self._to_converse_content(message["content"]),
                }
                for message in messages
            ],
            "inferenceConfig": inference_config,
        }

        if system:
            params["system"] = [{"text": system}]

        if tools:
            params["toolConfig"] = self._to_converse_tools(tools)

        if thinking:
            params["additionalModelRequestFields"] = {
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": thinking_budget,
                }
            }

        response = self.client.converse(**params)
        return self._from_converse(response)
