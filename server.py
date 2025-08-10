#!/usr/bin/env python3
"""
Enhanced Poem Generator MCP Server for Puch AI Hackathon (AI-first version)
Now all tools try Hugging Face first with retries and model warm-up.
"""
import asyncio
import json
import os
import sys
import random
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import web
import aiohttp_cors

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PoemGeneratorMCP:
    def __init__(self):
        self.name = "poem-generator"
        self.version = "1.1.0"
        self.hf_api_url = "https://api-inference.huggingface.co/models/gpt2"
        self.session = None

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {"name": "generate_poem", "description": "🎭 Generate a custom poem based on theme, style, and length",
             "inputSchema": {"type": "object", "properties": {"theme": {"type": "string"},
             "style": {"type": "string", "enum": ["free_verse", "haiku", "limerick", "sonnet", "rhyming", "acrostic"]},
             "length": {"type": "string", "enum": ["short", "medium", "long"]},
             "mood": {"type": "string", "enum": ["happy", "sad", "inspiring", "romantic", "mysterious", "playful"]}},
             "required": ["theme"]}},
            {"name": "quick_poem", "description": "✨ Generate a quick inspirational poem with just a theme",
             "inputSchema": {"type": "object", "properties": {"theme": {"type": "string"}}, "required": ["theme"]}},
            {"name": "haiku_generator", "description": "🌸 Generate a traditional 5-7-5 haiku poem",
             "inputSchema": {"type": "object", "properties": {"subject": {"type": "string"},
             "season": {"type": "string", "enum": ["spring", "summer", "autumn", "winter", "any"]}},
             "required": ["subject"]}},
            {"name": "acrostic_poem", "description": "📝 Generate an acrostic poem using the first letters of a word",
             "inputSchema": {"type": "object", "properties": {"word": {"type": "string"}, "theme": {"type": "string"}},
             "required": ["word"]}}
        ]

    async def query_ai_api(self, prompt: str, max_retries: int = 5) -> Optional[str]:
        session = await self.get_session()
        hf_token = os.getenv('HF_API_TOKEN')
        if not hf_token:
            logger.error("❌ HF_API_TOKEN environment variable not found or empty!")
            return None
        headers = {"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"}
        payload = {"inputs": prompt, "parameters": {"max_length": 200, "temperature": 0.7,
                    "do_sample": True, "return_full_text": False, "pad_token_id": 50256}}
        for attempt in range(max_retries):
            try:
                async with session.post(self.hf_api_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=25)) as response:
                    logger.info(f"HF API status: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        text = ""
                        if isinstance(result, list) and result:
                            text = result[0].get('generated_text', '').strip()
                        elif isinstance(result, dict):
                            text = result.get('generated_text', '').strip()
                        if len(text) > 10:
                            return text
                        else:
                            logger.warning("No valid generated text found.")
                            return None
                    elif response.status == 503:
                        logger.info(f"Model loading, retrying in 4s... (attempt {attempt+1})")
                        await asyncio.sleep(4)
                    else:
                        logger.error(f"Unexpected status {response.status}")
                        return None
            except Exception as e:
                logger.warning(f"HF API attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
        return None

    async def generate_with_ai_first(self, prompt: str, fallback_func, *fallback_args):
        ai_poem = await self.query_ai_api(prompt)
        if ai_poem and len(ai_poem.strip()) > 20:
            return ai_poem, "🤖 AI Generated"
        return fallback_func(*fallback_args), "📝 Crafted with Care"

    # simplified fallback
    def create_enhanced_poem(self, theme: str, style: str = "free_verse", length: str = "short", mood: str = "inspiring") -> str:
        return f"[{style.title()} about {theme} in {mood} mood - fallback generated]"

    def create_acrostic_poem(self, word: str, theme: str = None) -> str:
        return "\n".join([f"{letter} - {theme or 'theme'}" for letter in word])

    async def handle_generate_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        theme, style, length, mood = args.get('theme', 'life'), args.get('style', 'free_verse'), args.get('length', 'short'), args.get('mood', 'inspiring')
        prompt = f"Write a beautiful {mood} {length} {style.replace('_', ' ')} poem about {theme}."
        poem, source = await self.generate_with_ai_first(prompt, self.create_enhanced_poem, theme, style, length, mood)
        return {"content": [{"type": "text", "text": f"**Your Poem: '{theme.title()}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_quick_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        theme = args.get('theme', 'inspiration')
        prompt = f"Write a short, inspiring free verse poem about {theme}."
        poem, source = await self.generate_with_ai_first(prompt, self.create_enhanced_poem, theme, 'free_verse', 'short', 'inspiring')
        return {"content": [{"type": "text", "text": f"**Quick Inspiration: '{theme.title()}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_haiku_generator(self, args: Dict[str, Any]) -> Dict[str, Any]:
        subject, season = args.get('subject', 'nature'), args.get('season', 'any')
        theme = f"{season} {subject}" if season != 'any' else subject
        prompt = f"Write a traditional 5-7-5 haiku about {theme}."
        poem, source = await self.generate_with_ai_first(prompt, self.create_enhanced_poem, theme, 'haiku', 'short', 'mysterious')
        return {"content": [{"type": "text", "text": f"**Haiku: '{subject.title()}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_acrostic_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        word, theme = args.get('word', 'POEM').upper(), args.get('theme', None)
        if len(word) > 15:
            return {"content": [{"type": "text", "text": "❌ Word too long!"}], "isError": True}
        prompt = f"Write an acrostic poem for the word '{word}' about {theme or 'life'}."
        poem, source = await self.generate_with_ai_first(prompt, self.create_acrostic_poem, word, theme)
        return {"content": [{"type": "text", "text": f"**Acrostic Poem: '{word}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "generate_poem":
            return await self.handle_generate_poem(arguments)
        elif name == "quick_poem":
            return await self.handle_quick_poem(arguments)
        elif name == "haiku_generator":
            return await self.handle_haiku_generator(arguments)
        elif name == "acrostic_poem":
            return await self.handle_acrostic_poem(arguments)
        return {"content": [{"type": "text", "text": f"❌ Unknown tool: {name}"}], "isError": True}

# HTTP handler
def setup_routes(app):
    resource = app.router.add_resource("/mcp")
    app.router.add_route("POST", "/mcp", handle_mcp_request)
    app.router.add_get("/health", lambda r: web.json_response({"status": "healthy"}))
    app.router.add_get("/", lambda r: web.Response(text="Puch AI MCP server is running."))

def cors_wrap(app):
    cors = aiohttp_cors.setup(app, defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")})
    for route in list(app.router.routes()):
        cors.add(route)

async def handle_mcp_request(request):
    server = request.app['mcp_server']
    data = await request.json()
    method, params, msg_id = data.get("method"), data.get("params", {}), data.get("id")
    if method == "initialize":
        return web.json_response({"jsonrpc": "2.0", "id": msg_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": server.name, "version": server.version}}})
    elif method == "tools/list":
        tools = await server.list_tools()
        return web.json_response({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools}})
    elif method == "tools/call":
        tool_name, arguments = params.get("name"), params.get("arguments", {})
        result = await server.handle_tool_call(tool_name, arguments)
        return web.json_response({"jsonrpc": "2.0", "id": msg_id, "result": result})
    return web.json_response({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

async def create_app():
    app = web.Application()
    app['mcp_server'] = PoemGeneratorMCP()
    setup_routes(app)
    cors_wrap(app)
    return app

async def main():
    logger.info("🌐 Starting in Web mode")
    app = await create_app()
    logger.info("🔥 Warming up Hugging Face model...")
    await app['mcp_server'].query_ai_api("Warm up poem generator model.")
    logger.info("✅ Model warmed up.")
    port = int(os.getenv('PORT', 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"🚀 Server running on port {port}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
