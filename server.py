#!/usr/bin/env python3
"""
Poem Generator MCP Server using Hugging Face Router API
Now uses meta-llama/llama-3-8b-instruct for all poem generation.
"""
import asyncio
import json
import os
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import aiohttp
from aiohttp import web
import aiohttp_cors

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PoemGeneratorMCP:
    def __init__(self):
        self.name = "poem-generator"
        self.version = "2.0.0"
        self.hf_api_url = "https://router.huggingface.co/v1/chat/completions"
        self.model_name = "openai/gpt-oss-120b:fireworks-ai"
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

    async def query_ai_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Query Hugging Face Router API with Fireworks GPT-OSS-120B."""
        session = await self.get_session()
        hf_token = os.getenv('HF_API_TOKEN')
        if not hf_token:
            logger.error("❌ HF_API_TOKEN environment variable not found or empty!")
            return None

        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-oss-120b:fireworks-ai",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        for attempt in range(max_retries):
            try:
                async with session.post(self.hf_api_url, json=payload, headers=headers) as response:
                    logger.info(f"HF API status: {response.status}")
                    resp_json = await response.json()
                    logger.debug(f"HF API full response: {json.dumps(resp_json, indent=2)}")

                    if response.status == 200 and "choices" in resp_json:
                        text = resp_json["choices"][0]["message"]["content"].strip()
                        if text:
                            return text
                        else:
                            logger.warning("HF API returned empty text.")
                            return None
                    else:
                        logger.error(f"HF API error: {resp_json}")
                        return None

            except Exception as e:
                logger.warning(f"HF API attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)

        return None


    async def generate_poem(self, prompt: str) -> str:
        ai_poem = await self.query_ai_api(prompt)
        if ai_poem:
            return ai_poem, "🤖 AI Generated"
        return "[Poem generation failed]", "❌ Error"

    async def handle_generate_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        theme, style, length, mood = args.get('theme', 'life'), args.get('style', 'free_verse'), args.get('length', 'short'), args.get('mood', 'inspiring')
        prompt = f"Write a beautiful {mood} {length} {style.replace('_', ' ')} poem about {theme}."
        poem, source = await self.generate_poem(prompt)
        return {"content": [{"type": "text", "text": f"**Your Poem: '{theme.title()}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_quick_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        theme = args.get('theme', 'inspiration')
        prompt = f"Write a short, inspiring free verse poem about {theme}."
        poem, source = await self.generate_poem(prompt)
        return {"content": [{"type": "text", "text": f"**Quick Inspiration: '{theme.title()}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_haiku_generator(self, args: Dict[str, Any]) -> Dict[str, Any]:
        subject, season = args.get('subject', 'nature'), args.get('season', 'any')
        theme = f"{season} {subject}" if season != 'any' else subject
        prompt = f"Write a traditional 5-7-5 haiku about {theme}."
        poem, source = await self.generate_poem(prompt)
        return {"content": [{"type": "text", "text": f"**Haiku: '{subject.title()}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_acrostic_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        word, theme = args.get('word', 'POEM').upper(), args.get('theme', None)
        prompt = f"Write an acrostic poem for the word '{word}' about {theme or 'life'}."
        poem, source = await self.generate_poem(prompt)
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

# HTTP handlers
def setup_routes(app):
    resource = app.router.add_resource("/mcp")
    app.router.add_route("POST", "/mcp", handle_mcp_request)
    app.router.add_get("/health", lambda r: web.json_response({"status": "healthy"}))
    app.router.add_get("/", lambda r: web.Response(text="Puch AI MCP server is running."))

def cors_wrap(app):
    cors = aiohttp_cors.setup(app, defaults={"*": aiohttp_cors.ResourceOptions(
        allow_credentials=True, expose_headers="*", allow_headers="*"
    )})
    for route in list(app.router.routes()):
        cors.add(route)

async def handle_mcp_request(request):
    server = request.app['mcp_server']
    data = await request.json()
    method, params, msg_id = data.get("method"), data.get("params", {}), data.get("id")
    if method == "initialize":
        return web.json_response({"jsonrpc": "2.0", "id": msg_id, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": server.name, "version": server.version}
        }})
    elif method == "tools/list":
        tools = await server.list_tools()
        return web.json_response({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools}})
    elif method == "tools/call":
        tool_name, arguments = params.get("name"), params.get("arguments", {})
        result = await server.handle_tool_call(tool_name, arguments)
        return web.json_response({"jsonrpc": "2.0", "id": msg_id, "result": result})
    return web.json_response({"jsonrpc": "2.0", "id": msg_id,
                              "error": {"code": -32601, "message": f"Method not found: {method}"}})

async def create_app():
    app = web.Application()
    app['mcp_server'] = PoemGeneratorMCP()
    setup_routes(app)
    cors_wrap(app)
    return app

async def main():
    logger.info("🌐 Starting in Web mode")
    app = await create_app()
    logger.info("🔥 Warming up Hugging Face GPT-OSS-120B model...")
    await app['mcp_server'].query_ai_api("Warm up poem generator model.")
    logger.info("✅ Model warmed up.")

    port = int(os.getenv('PORT', 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"🚀 Server running on port {port}")

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("🛑 Stopping server...")
    finally:
        await app['mcp_server'].close_session()  # ✅ ensures no unclosed session
        await runner.cleanup()
        logger.info("✅ Server stopped cleanly.")

if __name__ == "__main__":
    asyncio.run(main())
