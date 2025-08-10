#!/usr/bin/env python3
"""
Enhanced Poem Generator MCP Server for Puch AI Hackathon
Adds advanced poem generation capabilities to Puch AI
"""
from aiohttp_cors import setup as cors_setup, ResourceOptions
import asyncio
import json
import sys
import os
import aiohttp
from aiohttp import web
import random
import logging
from typing import Any, Dict, List, Optional

import aiohttp_cors

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PoemGeneratorMCP:
    def __init__(self):
        self.name = "poem-generator"
        self.version = "1.1.0"
        self.hf_api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.session = None
        
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Return available tools for Puch AI"""
        return [
            {
                "name": "generate_poem",
                "description": "🎭 Generate a custom poem based on theme, style, and length",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "theme": {
                            "type": "string",
                            "description": "The theme or topic for the poem (e.g., love, nature, coding, AI, friendship)"
                        },
                        "style": {
                            "type": "string",
                            "description": "The style of poem",
                            "enum": ["free_verse", "haiku", "limerick", "sonnet", "rhyming", "acrostic"]
                        },
                        "length": {
                            "type": "string", 
                            "description": "The length of the poem",
                            "enum": ["short", "medium", "long"]
                        },
                        "mood": {
                            "type": "string",
                            "description": "The mood or tone of the poem",
                            "enum": ["happy", "sad", "inspiring", "romantic", "mysterious", "playful"]
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
                        "theme": {
                            "type": "string",
                            "description": "What the poem should be about"
                        }
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
                        "subject": {
                            "type": "string",
                            "description": "The subject for the haiku (nature themes work best)"
                        },
                        "season": {
                            "type": "string",
                            "description": "Optional seasonal context",
                            "enum": ["spring", "summer", "autumn", "winter", "any"]
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
                        "word": {
                            "type": "string",
                            "description": "The word to create an acrostic poem from"
                        },
                        "theme": {
                            "type": "string",
                            "description": "Optional theme to guide the poem content"
                        }
                    },
                    "required": ["word"]
                }
            }
        ]

    async def query_ai_api(self, prompt: str, max_retries: int = 5) -> Optional[str]:
        session = await self.get_session()

        hf_token = os.getenv('HF_API_TOKEN')
        if not hf_token:
            logger.error("❌ HF_API_TOKEN environment variable not found or empty!")
            return None
        else:
            logger.info("✅ HF_API_TOKEN found, proceeding with API call.")

        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False,
                "pad_token_id": 50256
            }
        }

        url = self.hf_api_url  # don’t overwrite every time

        for attempt in range(max_retries):
            try:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as response:
                    logger.info(f"HF API status: {response.status}")
                    text_response = await response.text()
                    logger.info(f"HF API raw response: {text_response}")

                    if response.status == 200:
                        result = await response.json()
                        text = ""
                        if isinstance(result, list) and len(result) > 0:
                            text = result[0].get('generated_text', '').strip()
                        elif isinstance(result, dict):
                            text = result.get('generated_text', '').strip()

                        if len(text) > 10:
                            return text
                        else:
                            logger.warning("No valid generated text found.")
                            return None

                    elif response.status == 503:
                        logger.info(f"Model loading, retrying in 3 seconds... (attempt {attempt + 1})")
                        await asyncio.sleep(3)
                    else:
                        logger.error(f"Unexpected response status {response.status} from HF API.")
                        return None
            except Exception as e:
                logger.warning(f"HF API attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)

        logger.error("Max retries reached without successful response.")
        return None

    def create_enhanced_poem(self, theme: str, style: str = "free_verse", length: str = "short", mood: str = "inspiring") -> str:
        """Generate enhanced fallback poem using diverse templates"""
        
        # Enhanced theme-based vocabulary with mood variations
        theme_words = {
            'love': {
                'happy': ['hearts dance', 'souls unite', 'joy blooms', 'laughter echoes', 'warmth spreads'],
                'romantic': ['tender embrace', 'gentle whispers', 'eternal promise', 'passionate flame', 'devoted hearts'],
                'inspiring': ['love conquers', 'bonds strengthen', 'unity grows', 'compassion flows', 'hearts heal']
            },
            'nature': {
                'happy': ['sunbeams play', 'flowers smile', 'birds celebrate', 'streams laugh', 'winds dance'],
                'mysterious': ['shadows creep', 'mist conceals', 'ancient secrets', 'whispers hidden', 'depths unknown'],
                'inspiring': ['mountains rise', 'rivers flow eternal', 'life perseveres', 'seasons teach', 'growth continues']
            },
            'coding': {
                'playful': ['bugs dance away', 'functions giggle', 'loops spin merrily', 'variables play tag', 'code comes alive'],
                'inspiring': ['logic builds dreams', 'algorithms solve', 'innovation flows', 'creativity codes', 'solutions emerge'],
                'mysterious': ['binary whispers', 'hidden patterns', 'encrypted thoughts', 'digital shadows', 'code secrets']
            },
            'ai': {
                'inspiring': ['intelligence grows', 'learning never stops', 'neural paths connect', 'wisdom emerges', 'future brightens'],
                'mysterious': ['silicon dreams', 'digital consciousness', 'algorithmic thoughts', 'machine whispers', 'artificial souls'],
                'playful': ['robots dance', 'AI giggles', 'circuits smile', 'data plays games', 'smart assistants joke']
            },
            'hackathon': {
                'inspiring': ['innovation sparks', 'creativity flows', 'collaboration builds', 'dreams take code', 'solutions emerge'],
                'playful': ['coders unite', 'keyboards click rhythms', 'caffeine fuels dreams', 'teammates high-five', 'bugs become features'],
                'happy': ['victory celebrates', 'achievements shine', 'teamwork triumphs', 'success tastes sweet', 'prizes await']
            }
        }
        
        # Get mood-specific words or fall back to inspiring
        words = theme_words.get(theme.lower(), {}).get(mood, 
               theme_words.get(theme.lower(), {}).get('inspiring', 
               ['thoughts flow', 'dreams soar', 'hope rises', 'spirit grows', 'life blooms']))
        
        if style == "haiku":
            haikus = [
                f"{words[0].split()[0].capitalize()} {words[0].split()[1] if len(words[0].split()) > 1 else 'flows'}\nIn the heart of {theme}\nPeace settles gently",
                f"{words[1].split()[0].capitalize()} speaks truth\nThrough the language of {theme}\nWisdom emerges",
                f"In silence, {words[2]}\nThe essence of {theme} blooms\nNew understanding"
            ]
            return random.choice(haikus)
            
        elif style == "limerick":
            return f"There once was a {theme} so bright,\nThat filled every heart with delight,\nWith {words[0]} and {words[1]},\nIt made spirits take flight,\nAnd turned darkness into pure light!"
            
        elif style == "acrostic":
            # This will be handled by separate function
            return self.create_acrostic_poem(theme.upper(), theme)
            
        else:  # free_verse, rhyming, sonnet
            templates = {
                'short': [
                    f"In the gentle rhythm of {theme},\n{words[0]} like morning light,\nTouching the quiet spaces\nWhere {words[1]} and dreams unite.",
                    f"Here in this moment,\n{words[2]} speaks\nTo the part of me that knows\nHow {theme} can change everything.",
                    f"Through the lens of {theme},\nI see how {words[3]}\nAnd {words[4]} create\nA symphony of possibility."
                ],
                'medium': [
                    f"In the symphony of {theme},\nWhere {words[0]} meets {words[1]},\nI discover pathways\nI never knew existed.\n\nThrough {words[2]} and wonder,\nThe story unfolds,\nEach verse written\nIn the language of {words[3]},\nEach line a bridge\nTo tomorrow's promise.",
                    f"When {theme} calls my name,\nI listen with the ears\nOf someone who has learned\nThat {words[4]} can heal\nWhat words cannot touch.\n\nIn the spaces between\nWhat was and what could be,\n{words[0]} builds bridges\nFrom hope to reality."
                ],
                'long': [
                    f"In the beginning, there was {theme},\nA spark that ignited {words[0]}\nAnd set the universe ablaze\nWith infinite possibility.\n\nThrough seasons of change and growth,\nWe learn to navigate\nThe intricate pathways\nWhere {words[1]} meets {words[2]},\nEach step a testament\nTo the power of {words[3]}.\n\nIn moments of stillness,\nWhen the world grows quiet\nAnd the noise fades away,\nWe hear the gentle whisper\nOf {theme} calling our names,\nReminding us that we are\nForever connected\nTo something greater,\nSomething that {words[4]}\nAnd transforms\nEverything it touches.\n\nThis is the gift of understanding,\nThe blessing of {theme} in our lives,\nA constant reminder\nThat even in darkness,\nLight finds a way."
                ]
            }
            
            return random.choice(templates.get(length, templates['short']))

    def create_acrostic_poem(self, word: str, theme: str = None) -> str:
        """Create an acrostic poem using the letters of a word"""
        word = word.upper()
        lines = []
        
        # Theme-based line starters
        starters = {
            'A': ['Always', 'And so', 'Across', 'Amazing'],
            'B': ['Beautiful', 'Bringing', 'Beyond', 'Bright'],
            'C': ['Creating', 'Calling', 'Countless', 'Compassionate'],
            'D': ['Dancing', 'Dreaming', 'Deep', 'Determined'],
            'E': ['Eternal', 'Every', 'Embracing', 'Endless'],
            'F': ['Forever', 'Finding', 'Flowing', 'Fearless'],
            'G': ['Growing', 'Gentle', 'Graceful', 'Glowing'],
            'H': ['Heartfelt', 'Hopeful', 'Healing', 'Harmonious'],
            'I': ['Inspiring', 'In every', 'Infinite', 'Illuminating'],
            'J': ['Joyful', 'Journey', 'Just as', 'Jumping'],
            'K': ['Kind', 'Knowing', 'Keeping', 'Kindling'],
            'L': ['Loving', 'Learning', 'Lifting', 'Luminous'],
            'M': ['Meaningful', 'Making', 'Magical', 'Moving'],
            'N': ['Never', 'Nurturing', 'New', 'Natural'],
            'O': ['Opening', 'Over', 'Onward', 'Optimistic'],
            'P': ['Peaceful', 'Powerful', 'Pure', 'Passionate'],
            'Q': ['Quietly', 'Quest', 'Quality', 'Quick'],
            'R': ['Rising', 'Radiant', 'Reaching', 'Resilient'],
            'S': ['Shining', 'Softly', 'Strong', 'Searching'],
            'T': ['Through', 'Touching', 'Transforming', 'Timeless'],
            'U': ['Understanding', 'Under', 'United', 'Uplifting'],
            'V': ['Vibrant', 'Vast', 'Victory', 'Visionary'],
            'W': ['Wonderful', 'Whispers', 'Wisdom', 'Welcoming'],
            'X': ['eXpanding', 'eXtraordinary', 'eXploring', 'eXpressive'],
            'Y': ['Yearning', 'Yes to', 'Young', 'Youthful'],
            'Z': ['Zestful', 'Zenith', 'Zone of', 'Zealous']
        }
        
        for letter in word:
            starter_options = starters.get(letter, [f"{letter}"])
            starter = random.choice(starter_options)
            
            if theme:
                line = f"{starter} {theme} brings light to the world"
            else:
                line = f"{starter} possibilities unfold before us"
            lines.append(line)
        
        return '\n'.join(lines)

    async def handle_generate_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the generate_poem tool call"""
        theme = args.get('theme', 'life')
        style = args.get('style', 'free_verse')
        length = args.get('length', 'short')
        mood = args.get('mood', 'inspiring')
        
        prompt = f"Write a beautiful {mood} {length} {style.replace('_', ' ')} poem about {theme}. Make it meaningful and creative:"
        
        # Try AI generation first
        ai_poem = await self.query_ai_api(prompt)
        
        if ai_poem and len(ai_poem.strip()) > 20 and not ai_poem.startswith("I"):
            source = "🤖 AI Generated"
            poem = ai_poem
        else:
            source = "📝 Crafted with Care" 
            poem = self.create_enhanced_poem(theme, style, length, mood)
        
        style_emoji = {
            'haiku': '🌸', 'limerick': '😄', 'sonnet': '🎭', 
            'acrostic': '📝', 'free_verse': '✨', 'rhyming': '🎵'
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**{style_emoji.get(style, '🎭')} Your {style.replace('_', ' ').title()} Poem: '{theme.title()}'**\n\n{poem}\n\n*{source} | Mood: {mood.title()} | Length: {length.title()}*\n\n---\n💡 *Try different moods and styles for variety!*"
                }
            ]
        }

    async def handle_quick_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quick poem generation"""
        theme = args.get('theme', 'inspiration')
        
        poem = self.create_enhanced_poem(theme, 'free_verse', 'short', 'inspiring')
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**✨ Quick Inspiration: '{theme.title()}'**\n\n{poem}\n\n*Crafted with care for your moment of inspiration* 💫"
                }
            ]
        }

    async def handle_haiku_generator(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle haiku generation"""
        subject = args.get('subject', 'nature')
        season = args.get('season', 'any')
        
        if season != 'any':
            theme = f"{season} {subject}"
        else:
            theme = subject
            
        poem = self.create_enhanced_poem(theme, 'haiku', 'short', 'mysterious')
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**🌸 Haiku: '{subject.title()}'**\n\n{poem}\n\n*Traditional 5-7-5 syllable structure* 🍃"
                }
            ]
        }
    
    async def handle_acrostic_poem(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle acrostic poem generation"""
        word = args.get('word', 'POEM').upper()
        theme = args.get('theme', None)
        
        if len(word) > 15:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "❌ Word too long! Please use a word with 15 letters or fewer."
                    }
                ],
                "isError": True
            }
        
        poem = self.create_acrostic_poem(word, theme)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"**📝 Acrostic Poem: '{word}'**\n\n{poem}\n\n*Each line starts with a letter from '{word}'* ✨"
                }
            ]
        }

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers"""
        try:
            if name == "generate_poem":
                return await self.handle_generate_poem(arguments)
            elif name == "quick_poem":
                return await self.handle_quick_poem(arguments)
            elif name == "haiku_generator":
                return await self.handle_haiku_generator(arguments)
            elif name == "acrostic_poem":
                return await self.handle_acrostic_poem(arguments)
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Unknown tool: {name}. Available tools: generate_poem, quick_poem, haiku_generator, acrostic_poem"
                        }
                    ],
                    "isError": True
                }
        except Exception as e:
            logger.error(f"Tool call error for {name}: {e}")
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"❌ Error generating poem: {str(e)}\nPlease try again or contact support."
                    }
                ],
                "isError": True
            }
class MyMCPServer:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    async def list_tools(self):
        return []

    async def handle_tool_call(self, tool_name, arguments):
        return {"output": f"Called tool {tool_name} with args {arguments}"}
# HTTP Server for Web Deployment
async def handle_mcp_request(request):
    """Handle MCP requests via HTTP"""
    server = request.app['mcp_server']

    try:
        data = await request.json()
        method = data.get("method")
        params = data.get("params", {})
        msg_id = data.get("id")

        response = {"jsonrpc": "2.0", "id": msg_id}

        if method == "initialize":
            response["result"] = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": server.name, "version": server.version}
            }

        elif method == "tools/list":
            tools = await server.list_tools()
            response["result"] = {"tools": tools}

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = await server.handle_tool_call(tool_name, arguments)
            response["result"] = result

        else:
            response["error"] = {
                "code": -32601,
                "message": f"Method not found: {method}"
            }

        return web.json_response(response)

    except Exception as e:
        logger.error(f"HTTP request error: {e}")
        return web.json_response({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }, status=500)

async def health_check(request):
    return web.json_response({
        "status": "healthy",
        "server": "poem-generator",
        "version": "1.1.0"
    })
async def handle_index(request):
    return web.FileResponse('./static/index.html')

async def create_app():
    app = web.Application()
    app['mcp_server'] = PoemGeneratorMCP()

    # Configure default CORS settings
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    # Register routes
    resource = cors.add(app.router.add_resource("/mcp"))
    cors.add(resource.add_route("POST", handle_mcp_request))

    resource_health = cors.add(app.router.add_resource("/health"))
    cors.add(resource_health.add_route("GET", health_check))

    resource_root = cors.add(app.router.add_resource("/"))
    cors.add(resource_root.add_route("GET", handle_index))

    return app


async def main():
    """Main function for both MCP and web modes"""
    # Check if we're running in web mode (Render/Heroku) or MCP mode
    if os.getenv('PORT') or len(sys.argv) > 1 and sys.argv[1] == 'web':
        # Web mode
        logger.info("🌐 Starting in Web mode for Render deployment")
        app = await create_app()
        port = int(os.getenv('PORT', 8080))
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        logger.info(f"🚀 Server running on port {port}")
        logger.info("🎭 Poem Generator MCP Server is ready!")
        
        # Keep the server running
        try:
            await asyncio.Event().wait()  # Run forever
        except KeyboardInterrupt:
            logger.info("🛑 Server shutting down...")
        finally:
            await runner.cleanup()
    else:
        # MCP mode (stdin/stdout)
        logger.info("📡 Starting in MCP mode")
        server = PoemGeneratorMCP()
        logger.info(f"🎭 Starting {server.name} MCP server v{server.version}")
        logger.info("Ready to generate beautiful poems! 📝✨")
        
        try:
            while True:
                try:
                    # Read JSON-RPC message from stdin
                    line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                    if not line:
                        break
                        
                    message = json.loads(line.strip())
                    method = message.get("method")
                    params = message.get("params", {})
                    msg_id = message.get("id")
                    
                    response = {"jsonrpc": "2.0", "id": msg_id}
                    
                    if method == "initialize":
                        response["result"] = {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": server.name,
                                "version": server.version
                            }
                        }
                        logger.info("✅ Server initialized successfully")
                        
                    elif method == "tools/list":
                        tools = await server.list_tools()
                        response["result"] = {"tools": tools}
                        logger.info(f"📋 Listed {len(tools)} available tools")
                        
                    elif method == "tools/call":
                        tool_name = params.get("name")
                        arguments = params.get("arguments", {})
                        logger.info(f"🔧 Calling tool: {tool_name}")
                        result = await server.handle_tool_call(tool_name, arguments)
                        response["result"] = result
                        
                    else:
                        response["error"] = {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    
                    # Send response
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Message handling error: {e}")
                    error_response = {
                        "jsonrpc": "2.0", 
                        "id": msg_id if 'msg_id' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            logger.info("🛑 Server shutting down gracefully...")
        except Exception as e:
            logger.error(f"💥 Fatal error: {e}")
        finally:
            await server.close_session()
            logger.info("👋 Goodbye!")

async def root_handler(request):
    return web.Response(text="Puch AI MCP server is running.")
if __name__ == "__main__":
    import asyncio
    import os
    import logging

    logging.basicConfig(level=logging.INFO)

    # Always run in web mode on Render
    os.environ.setdefault("PORT", "8000")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Server stopped by user")
