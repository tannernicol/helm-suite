#!/usr/bin/env python3
"""Ollama MCP Server -- Local LLM inference for your tools.

Exposes your local Ollama instance to LLM clients via MCP. Use this to
offload tasks (summarization, code review, etc.) to local models and
save cloud API tokens.

Usage:
    python3 server.py

Requires:
    pip install mcp httpx

Configure OLLAMA_URL if Ollama is not on localhost.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Add lib to path for shared logging
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
try:
    from logger import log_call
except ImportError:

    def log_call(*args, **kwargs):
        pass


# ---- Configuration ----------------------------------------------------------
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# Models available on your system. Update this after pulling models.
# Format: "model_name": "description of what it's good at"
MODELS: dict[str, str] = {
    "qwen2.5-coder:7b": "Fast code helper, debugging, code generation",
    "qwen2.5:7b": "General reasoning, analysis, writing",
    # Add more as you pull them:
    # "qwen2.5-coder:32b": "Advanced code analysis and review",
    # "qwen2.5:32b": "Advanced reasoning and writing",
}

# ---- Server -----------------------------------------------------------------
server = Server("ollama-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    model_list = ", ".join(MODELS.keys())
    return [
        Tool(
            name="ollama_generate",
            description=(
                f"Generate text using a local LLM via Ollama. "
                f"Available models: {model_list}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Model to use",
                        "enum": list(MODELS.keys()),
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The prompt for the local LLM",
                    },
                    "system": {
                        "type": "string",
                        "description": "System prompt (optional)",
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature 0-1 (default 0.7)",
                        "default": 0.7,
                    },
                },
                "required": ["model", "prompt"],
            },
        ),
        Tool(
            name="ollama_code_review",
            description=(
                "Have a local LLM review code for bugs, security issues, "
                "and improvements."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to review",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                    },
                    "focus": {
                        "type": "string",
                        "description": "Focus area: security, bugs, performance, all",
                        "default": "all",
                    },
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="ollama_summarize",
            description="Have a local LLM summarize text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to summarize",
                    },
                    "style": {
                        "type": "string",
                        "description": "Style: brief, detailed, bullets",
                        "default": "brief",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="ollama_models",
            description="List available Ollama models on this machine.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


async def _generate(
    model: str, prompt: str, system: str | None = None, temperature: float = 0.7
) -> str:
    """Call Ollama generate API."""
    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "")


def _pick_code_model() -> str:
    """Pick the best available code model."""
    preferences = ["qwen2.5-coder:32b", "qwen2.5-coder:14b", "qwen2.5-coder:7b"]
    for model in preferences:
        if model in MODELS:
            return model
    return next(iter(MODELS))


def _pick_general_model() -> str:
    """Pick the best available general model."""
    preferences = ["qwen2.5:32b", "qwen2.5:14b", "qwen2.5:7b"]
    for model in preferences:
        if model in MODELS:
            return model
    return next(iter(MODELS))


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    log_call("ollama", name, arguments)
    try:
        if name == "ollama_generate":
            model = arguments.get("model", "")
            prompt = arguments.get("prompt", "")
            system = arguments.get("system")
            temperature = arguments.get("temperature", 0.7)

            if model not in MODELS:
                return [
                    TextContent(
                        type="text",
                        text=f"Error: Unknown model '{model}'. Available: {list(MODELS.keys())}",
                    )
                ]

            result = await _generate(model, prompt, system, temperature)
            return [TextContent(type="text", text=result)]

        elif name == "ollama_code_review":
            code = arguments.get("code", "")
            language = arguments.get("language", "unknown")
            focus = arguments.get("focus", "all")

            focus_prompts = {
                "security": "Focus on security vulnerabilities, injection risks, and unsafe practices.",
                "bugs": "Focus on potential bugs, edge cases, and logic errors.",
                "performance": "Focus on performance issues and optimization opportunities.",
                "all": "Review for security, bugs, and performance issues.",
            }

            system = (
                f"You are an expert code reviewer. "
                f"{focus_prompts.get(focus, focus_prompts['all'])} "
                f"Be concise and actionable. List issues with line references."
            )
            prompt = f"Review this {language} code:\n\n```{language}\n{code}\n```"

            result = await _generate(_pick_code_model(), prompt, system, 0.3)
            return [TextContent(type="text", text=result)]

        elif name == "ollama_summarize":
            text = arguments.get("text", "")
            style = arguments.get("style", "brief")

            style_prompts = {
                "brief": "Provide a 2-3 sentence summary.",
                "detailed": "Provide a comprehensive summary covering all key points.",
                "bullets": "Summarize as bullet points.",
            }

            system = (
                f"You are a summarization expert. "
                f"{style_prompts.get(style, style_prompts['brief'])}"
            )
            prompt = f"Summarize the following:\n\n{text}"

            result = await _generate(_pick_general_model(), prompt, system, 0.5)
            return [TextContent(type="text", text=result)]

        elif name == "ollama_models":
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{OLLAMA_URL}/api/tags")
                response.raise_for_status()
                models = response.json().get("models", [])

            model_list = [
                {"name": m["name"], "size": f"{m.get('size', 0) / 1e9:.1f}GB"}
                for m in models
            ]
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"models": model_list}, indent=2),
                )
            ]

    except httpx.ConnectError:
        return [
            TextContent(
                type="text",
                text=f"Error: Cannot connect to Ollama at {OLLAMA_URL}. Is it running?",
            )
        ]
    except httpx.HTTPStatusError as e:
        return [
            TextContent(type="text", text=f"HTTP Error: {e.response.status_code}")
        ]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
