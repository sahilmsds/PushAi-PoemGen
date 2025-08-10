#!/usr/bin/env python3
"""
Enhanced Poem Generator MCP Server - WITH BETTER DEBUGGING
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
        self.version = "1.2.0"
        self.hf_api_url = "https://api-inference.huggingface.co/models/gpt2"
        self.session = None
        self.hf_working = False

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
             "required": ["word"]}},
            {"name": "debug_status", "description": "🔧 Check server status and AI integration",
             "inputSchema": {"type": "object", "properties": {}, "required": []}}
        ]

    async def query_ai_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Query Hugging Face API with enhanced debugging"""
        session = await self.get_session()
        hf_token = os.getenv('HF_API_TOKEN')
        
        # DEBUG: Check token
        if not hf_token:
            logger.error("❌ NO HF_API_TOKEN FOUND!")
            logger.error("   Add HF_API_TOKEN in Render environment variables")
            logger.error("   Get token from: https://huggingface.co/settings/tokens")
            return None
        
        logger.info(f"✅ HF_API_TOKEN found (length: {len(hf_token)})")
        
        headers = {"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 150,
                "temperature": 0.8,
                "do_sample": True,
                "return_full_text": False,
                "pad_token_id": 50256
            }
        }
        
        logger.info(f"🚀 Calling HF API with prompt: '{prompt[:50]}...'")
        
        for attempt in range(max_retries):
            try:
                async with session.post(
                    self.hf_api_url, 
                    json=payload, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    logger.info(f"📡 HF API Response: Status {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ HF API Success: {type(result)}")
                        
                        text = ""
                        if isinstance(result, list) and result:
                            text = result[0].get('generated_text', '').strip()
                        elif isinstance(result, dict):
                            text = result.get('generated_text', '').strip()
                        
                        if len(text) > 10:
                            logger.info(f"🎉 AI Generated text: '{text[:100]}...'")
                            self.hf_working = True
                            return text
                        else:
                            logger.warning(f"⚠️  Generated text too short: '{text}'")
                            
                    elif response.status == 503:
                        logger.warning(f"⏳ Model loading, attempt {attempt+1}/{max_retries}")
                        await asyncio.sleep(5)
                        continue
                        
                    elif response.status == 401:
                        logger.error("🔐 Authentication failed - check HF_API_TOKEN")
                        return None
                        
                    elif response.status == 429:
                        logger.error("🚦 Rate limited - too many requests")
                        await asyncio.sleep(10)
                        continue
                        
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Unexpected status {response.status}: {error_text}")
                        
            except asyncio.TimeoutError:
                logger.error(f"⏱️  Timeout on attempt {attempt+1}")
            except Exception as e:
                logger.error(f"💥 HF API error (attempt {attempt+1}): {str(e)}")
                
        logger.error("❌ All HF API attempts failed - using fallback")
        return None

    def create_enhanced_poem(self, theme: str, style: str = "free_verse", length: str = "short", mood: str = "inspiring") -> str:
        """Enhanced fallback poem generation"""
        logger.info(f"📝 Creating fallback poem: {theme}, {style}, {length}, {mood}")
        
        # Theme-based templates
        templates = {
            'hackathon': {
                'short': f"Code flows like poetry,\nIdeas spark in the night,\n{theme} brings us together,\nBuilding dreams with digital light.",
                'medium': f"In the realm of {theme},\nWhere keyboards click like rain,\nDevelopers unite with vision,\nTransforming ideas into gain.\n\nThrough coffee-fueled nights,\nAnd debugging sessions long,\nWe craft the future together,\nOur code becomes our song.",
            },
            'ai': {
                'short': f"Silicon dreams awaken,\nNeural networks learn and grow,\n{theme} shapes tomorrow,\nIn ways we're just starting to know.",
                'medium': f"In circuits deep and algorithms bright,\n{theme} emerges from the digital night,\nLearning, adapting, growing strong,\nSinging humanity's technological song.\n\nFrom data streams to knowledge vast,\nThe future's here, arriving fast,\nWhere human creativity meets machine,\nThe most amazing things are seen."
            }
        }
        
        # Get theme-specific template or create generic
        theme_templates = templates.get(theme.lower(), {})
        template = theme_templates.get(length, f"In the world of {theme},\nWhere {mood} feelings flow,\nWe find our inspiration,\nAnd watch our spirits grow.")
        
        return template

    async def handle_debug_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Debug endpoint to check server status"""
        hf_token = os.getenv('HF_API_TOKEN')
        
        status = {
            "server_version": self.version,
            "hf_token_present": bool(hf_token),
            "hf_token_length": len(hf_token) if hf_token else 0,
            "hf_api_working": self.hf_working,
            "environment_vars": list(os.environ.keys()),
        }
        
        # Test HF API
        test_result = await self.query_ai_api("Test poem about debugging.")
        status["hf_test_success"] = bool(test_result)
        status["hf_test_result"] = test_result[:100] if test_result else "No result"
        
        debug_text = f"""
**🔧 Server Debug Status**

**Environment:**
- HF Token Present: {'✅' if status['hf_token_present'] else '❌'}
- HF Token Length: {status['hf_token_length']}
- HF API Working: {'✅' if status['hf_api_working'] else '❌'}

**API Test:**
- Test Success: {'✅' if status['hf_test_success'] else '❌'}
- Test Result: {status['hf_test_result']}

**Fix Issues:**
{'✅ All systems working!' if status['hf_token_present'] and status['hf_test_success'] else '❌ Issues detected:'}
{'' if status['hf_token_present'] else '- Add HF_API_TOKEN environment variable'}
{'' if status['hf_test_success'] else '- HF API not responding (check logs)'}
        """
        
        return {"content": [{"type": "text", "text": debug_text.strip()}]}

    async def generate_with_ai_first(self, prompt: str, fallback_func, *fallback_args):
        """Try AI first, fallback to templates"""
        logger.info(f"🎭 Generating poem: AI first, then fallback")
        
        ai_poem = await self.query_ai_api(prompt)
        if ai_poem and len(ai_poem.strip()) > 20:
            logger.info("🤖 Using AI generated poem")
            return ai_poem, "🤖 AI Generated"
        
        logger.info("📝 Using fallback poem")
        return fallback_func(*fallback_args), "📝 Crafted with Care"

    async def handle_generate_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        theme = args.get('theme', 'life')
        style = args.get('style', 'free_verse')
        length = args.get('length', 'short')
        mood = args.get('mood', 'inspiring')
        
        prompt = f"Write a beautiful {mood} {length} {style.replace('_', ' ')} poem about {theme}. Make it creative and meaningful:"
        poem, source = await self.generate_with_ai_first(prompt, self.create_enhanced_poem, theme, style, length, mood)
        
        return {"content": [{"type": "text", "text": f"**🎭 Your {style.title()} Poem: '{theme.title()}'**\n\n{poem}\n\n*{source} | Style: {style} | Mood: {mood}*"}]}

    async def handle_quick_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        theme = args.get('theme', 'inspiration')
        prompt = f"Write a short, inspiring free verse poem about {theme}. Make it uplifting:"
        poem, source = await self.generate_with_ai_first(prompt, self.create_enhanced_poem, theme, 'free_verse', 'short', 'inspiring')
        return {"content": [{"type": "text", "text": f"**✨ Quick Inspiration: '{theme.title()}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_haiku_generator(self, args: Dict[str, Any]) -> Dict[str, Any]:
        subject = args.get('subject', 'nature')
        season = args.get('season', 'any')
        theme = f"{season} {subject}" if season != 'any' else subject
        prompt = f"Write a traditional 5-7-5 syllable haiku about {theme}:"
        poem, source = await self.generate_with_ai_first(prompt, self.create_enhanced_poem, theme, 'haiku', 'short', 'mysterious')
        return {"content": [{"type": "text", "text": f"**🌸 Haiku: '{subject.title()}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_acrostic_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        word = args.get('word', 'POEM').upper()
        theme = args.get('theme', None)
        if len(word) > 15:
            return {"content": [{"type": "text", "text": "❌ Word too long! Use 15 letters or fewer."}], "isError": True}
        
        prompt = f"Write an acrostic poem using the word '{word}' where each line starts with the corresponding letter. Theme: {theme or 'life'}:"
        
        def fallback_acrostic():
            return "\n".join([f"{letter}mazing things happen when we try" for letter in word])
        
        poem, source = await self.generate_with_ai_first(prompt, fallback_acrostic)
        return {"content": [{"type": "text", "text": f"**📝 Acrostic Poem: '{word}'**\n\n{poem}\n\n*{source}*"}]}

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"🔧 Tool called: {name} with args: {arguments}")
        
        if name == "generate_poem":
            return await self.handle_generate_poem(arguments)
        elif name == "quick_poem":
            return await self.handle_quick_poem(arguments)
        elif name == "haiku_generator":
            return await self.handle_haiku_generator(arguments)
        elif name == "acrostic_poem":
            return await self.handle_acrostic_poem(arguments)
        elif name == "debug_status":
            return await self.handle_debug_status(arguments)
        
        return {"content": [{"type": "text", "text": f"❌ Unknown tool: {name}"}], "isError": True}

# Rest of your HTTP handling code stays the same...
def setup_routes(app):
    app.router.add_route("POST", "/mcp", handle_mcp_request)
    app.router.add_get("/health", lambda r: web.json_response({"status": "healthy", "hf_working": r.app['mcp_server'].hf_working}))
    app.router.add_get("/", lambda r: web.Response(text="Puch AI MCP server is running. Check /health for status."))

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
    logger.info("🌐 Starting Enhanced Poem Generator MCP Server")
    app = await create_app()
    
    # Test HF integration on startup
    logger.info("🔥 Testing Hugging Face integration...")
    test_result = await app['mcp_server'].query_ai_api("Test startup poem about hackathon.")
    if test_result:
        logger.info("✅ Hugging Face API working!")
    else:
        logger.warning("⚠️  Hugging Face API not working - will use fallbacks")
    
    port = int(os.getenv('PORT', 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"🚀 Server running on port {port}")
    logger.info("🎭 Ready to generate poems!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())