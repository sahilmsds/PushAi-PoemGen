#!/usr/bin/env python3
"""
Poem Generator MCP Server for Puch AI
Uses Bearer token authentication as required by Puch AI
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
        self.session = None
        self.auth_token = os.getenv('AUTH_TOKEN')  # Required by Puch AI

    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    def validate_auth(self, request):
        """Validate Bearer token as required by Puch AI"""
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        return token == self.auth_token

    async def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "generate_poem",
                "description": "🎭 Generate a custom poem based on theme, style, and length",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string", "description": "Main theme or subject of the poem"},
                        "style": {
                            "type": "string", 
                            "enum": ["free_verse", "haiku", "limerick", "sonnet", "rhyming", "acrostic"],
                            "description": "Style of poem to generate"
                        },
                        "length": {
                            "type": "string", 
                            "enum": ["short", "medium", "long"],
                            "description": "Length of the poem"
                        },
                        "mood": {
                            "type": "string", 
                            "enum": ["happy", "sad", "inspiring", "romantic", "mysterious", "playful"],
                            "description": "Emotional tone of the poem"
                        }
                    },
                    "required": ["theme"]
                }
            },
            {
                "name": "quick_poem",
                "description": "✨ Generate a quick inspirational poem with just a theme",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string", "description": "Theme for the inspirational poem"}
                    },
                    "required": ["theme"]
                }
            },
            {
                "name": "haiku_generator", 
                "description": "🌸 Generate a traditional 5-7-5 haiku poem",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string", "description": "Subject of the haiku"},
                        "season": {
                            "type": "string",
                            "enum": ["spring", "summer", "autumn", "winter", "any"],
                            "description": "Season theme for the haiku"
                        }
                    },
                    "required": ["subject"]
                }
            },
            {
                "name": "acrostic_poem",
                "description": "📝 Generate an acrostic poem using the first letters of a word",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "word": {"type": "string", "description": "Word to use for acrostic poem"},
                        "theme": {"type": "string", "description": "Optional theme for the poem"}
                    },
                    "required": ["word"]
                }
            }
        ]

    async def query_ai_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Query Hugging Face Router API"""
        session = await self.get_session()
        hf_token = os.getenv('HF_API_TOKEN')
        if not hf_token:
            logger.error("❌ HF_API_TOKEN environment variable not found!")
            return None

        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-oss-120b:fireworks-ai",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        for attempt in range(max_retries):
            try:
                async with session.post(self.hf_api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        resp_json = await response.json()
                        if "choices" in resp_json and resp_json["choices"]:
                            return resp_json["choices"][0]["message"]["content"].strip()
                    else:
                        logger.error(f"HF API error: {response.status}")
            except Exception as e:
                logger.warning(f"HF API attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
        return None

    async def generate_poem(self, prompt: str) -> tuple[str, str]:
        ai_poem = await self.query_ai_api(prompt)
        if ai_poem:
            return ai_poem, "🤖 AI Generated"
        return "[Poem generation failed]", "❌ Error"

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if name == "generate_poem":
                theme = arguments.get('theme', 'life')
                style = arguments.get('style', 'free_verse')
                length = arguments.get('length', 'short') 
                mood = arguments.get('mood', 'inspiring')
                prompt = f"Write a beautiful {mood} {length} {style.replace('_', ' ')} poem about {theme}."
                poem, source = await self.generate_poem(prompt)
                return {
                    "content": [{
                        "type": "text", 
                        "text": f"**Your Poem: '{theme.title()}'**\n\n{poem}\n\n*{source}*"
                    }]
                }
                
            elif name == "quick_poem":
                theme = arguments.get('theme', 'inspiration')
                prompt = f"Write a short, inspiring free verse poem about {theme}."
                poem, source = await self.generate_poem(prompt)
                return {
                    "content": [{
                        "type": "text",
                        "text": f"**Quick Inspiration: '{theme.title()}'**\n\n{poem}\n\n*{source}*"
                    }]
                }
                
            elif name == "haiku_generator":
                subject = arguments.get('subject', 'nature')
                season = arguments.get('season', 'any')
                theme = f"{season} {subject}" if season != 'any' else subject
                prompt = f"Write a traditional 5-7-5 haiku about {theme}."
                poem, source = await self.generate_poem(prompt)
                return {
                    "content": [{
                        "type": "text",
                        "text": f"**Haiku: '{subject.title()}'**\n\n{poem}\n\n*{source}*"
                    }]
                }
                
            elif name == "acrostic_poem":
                word = arguments.get('word', 'POEM').upper()
                theme = arguments.get('theme', None)
                prompt = f"Write an acrostic poem for the word '{word}' about {theme or 'life'}."
                poem, source = await self.generate_poem(prompt)
                return {
                    "content": [{
                        "type": "text",
                        "text": f"**Acrostic Poem: '{word}'**\n\n{poem}\n\n*{source}*"
                    }]
                }
                
            else:
                return {
                    "content": [{"type": "text", "text": f"❌ Unknown tool: {name}"}],
                    "isError": True
                }
        except Exception as e:
            logger.error(f"Error in tool call {name}: {e}")
            return {
                "content": [{"type": "text", "text": f"❌ Error: {str(e)}"}],
                "isError": True
            }

# HTTP handlers for MCP protocol
async def handle_mcp_request(request):
    """Handle MCP JSON-RPC requests with Bearer token auth"""
    server = request.app['mcp_server']
    
    # Validate Bearer token authentication (required by Puch AI)
    if not server.validate_auth(request):
        return web.json_response(
            {"error": "Unauthorized - Invalid Bearer token"}, 
            status=401
        )
    
    try:
        data = await request.json()
        method = data.get("method")
        params = data.get("params", {})
        msg_id = data.get("id")
        
        if method == "initialize":
            return web.json_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": server.name, "version": server.version}
                }
            })
            
        elif method == "tools/list":
            tools = await server.list_tools()
            return web.json_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": tools}
            })
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = await server.handle_tool_call(tool_name, arguments)
            return web.json_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            })
            
        else:
            return web.json_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })
            
    except Exception as e:
        logger.error(f"MCP request error: {e}")
        return web.json_response({
            "jsonrpc": "2.0",
            "id": data.get("id") if 'data' in locals() else None,
            "error": {"code": -32603, "message": "Internal error"}
        }, status=500)

async def handle_health(request):
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "server": "poem-generator"})

async def handle_root(request):
    """Root endpoint info"""
    return web.json_response({
        "name": "poem-generator",
        "version": "2.0.0",
        "description": "Puch AI MCP server for AI poem generation",
        "status": "running"
    })

def setup_routes(app):
    """Setup HTTP routes"""
    app.router.add_post("/mcp", handle_mcp_request)  # Main MCP endpoint
    app.router.add_get("/health", handle_health)     # Health check
    app.router.add_get("/", handle_root)             # Root info

def setup_cors(app):
    """Setup CORS for all routes"""
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET", "POST", "OPTIONS"]
        )
    })
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)

async def create_app():
    """Create and configure the web application"""
    app = web.Application()
    
    # Initialize MCP server
    mcp_server = PoemGeneratorMCP()
    if not mcp_server.auth_token:
        logger.error("❌ AUTH_TOKEN environment variable is required!")
        raise ValueError("AUTH_TOKEN is required for Puch AI authentication")
    
    app['mcp_server'] = mcp_server
    
    # Setup routes and CORS
    setup_routes(app)
    setup_cors(app)
    
    return app

async def main():
    """Main server entry point"""
    logger.info("🚀 Starting Puch AI MCP Poem Generator Server")
    
    # Verify required environment variables
    if not os.getenv('AUTH_TOKEN'):
        logger.error("❌ AUTH_TOKEN environment variable is required!")
        return
    if not os.getenv('HF_API_TOKEN'):
        logger.error("❌ HF_API_TOKEN environment variable is required!")
        return
    
    app = await create_app()
    
    # Warm up the AI model
    logger.info("🔥 Warming up AI model...")
    await app['mcp_server'].query_ai_api("Test poem generation.")
    logger.info("✅ Model ready")
    
    # Start server
    port = int(os.getenv('PORT', 8086))  # Use 8086 as per Puch AI docs
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"🚀 MCP server running on http://0.0.0.0:{port}")
    logger.info("📝 Ready for Puch AI connections!")
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("🛑 Stopping server...")
    finally:
        await app['mcp_server'].close_session()
        await runner.cleanup()
        logger.info("✅ Server stopped cleanly")

if __name__ == "__main__":
    asyncio.run(main())