# Poem Generator MCP Server
An AI-powered poetry generation MCP server built for the Puch AI Hackathon. Generate beautiful, custom poems in multiple styles with just a few words!

## Features
4 Poem Types: Custom poems, quick inspiration, haikus, and acrostic poems
Multiple Styles: Free verse, sonnets, limericks, rhyming, and more
Mood Control: Happy, sad, romantic, mysterious, playful, inspiring
Length Options: Short, medium, or long poems
AI-Powered: Uses advanced language models for high-quality generation
Secure: Bearer token authentication for safe usage


## Available Tools
### 1. generate_poem 
Generate custom poems with full control over style, mood, and length.
Parameters:

theme: "ocean waves"
style: "free_verse" | "haiku" | "limerick" | "sonnet" | "rhyming" | "acrostic"
length: "short" | "medium" | "long"
mood: "happy" | "sad" | "inspiring" | "romantic" | "mysterious" | "playful"

### 2. quick_poem
Get instant inspirational poetry with just a theme.
Parameters:

theme: "courage"

### 3. haiku_generator
Create traditional 5-7-5 haiku poems.
Parameters:

subject: "cherry blossoms"
season: "spring" | "summer" | "autumn" | "winter" | "any"

### 4. acrostic_poem
Generate poems using the first letters of any word.
Parameters:

word: "HOPE"
theme: "perseverance" (optional)

### Example Usage
Quick Inspiration
json{
  "name": "quick_poem",
  "arguments": {
    "theme": "new beginnings"
  }
}
Custom Love Poem
json{
  "name": "generate_poem", 
  "arguments": {
    "theme": "eternal love",
    "style": "sonnet",
    "length": "medium", 
    "mood": "romantic"
  }
}
Seasonal Haiku
json{
  "name": "haiku_generator",
  "arguments": {
    "subject": "falling leaves",
    "season": "autumn" 
  }
}

### Technical Setup
Prerequisites

Python 3.11+
Hugging Face API Token
Bearer token for authentication

## Installation
bash# Clone the repository
git clone https://github.com/sahilmsds/PushAi-PoemGen.git
cd PushAi-PoemGen

### Install dependencies
pip install -r requirements.txt

### Set up environment variables
cp .env.example .env
#### Edit .env with your tokens

#### Authentication
This server uses Bearer token authentication as required by Puch AI:
Authorization: Bearer your-auth-token

## Use Cases

Creative Writing - Generate inspiration for stories and scripts
Social Media - Create engaging poetry content
Education - Help students learn different poetry forms
Personal - Express emotions through AI-generated verse
Gifts - Create personalized poems for special occasions

## AI Model
Powered by advanced language models through Hugging Face Router API for high-quality, contextually appropriate poetry generation.
### Sample Output
**Quick Inspiration: 'Hope'**

Hope is the quiet ember
that refuses to die,
even when the world grows cold
and shadows stretch too long.

It whispers in the darkness,
"Tomorrow holds a different light,"
and carries us forward
on wings we cannot see.

Created with ❤️ for the Puch AI Hackathon
Bringing the beauty of poetry to AI conversations
