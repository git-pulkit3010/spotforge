# SpotForge 🎬✨

**Turn a single sentence into a polished, narrated storyboard video.**

SpotForge is a powerful AI-driven tool that transforms simple text descriptions into professional product storyboards with seamless transitions and optional narration. Perfect for creating marketing content, product demos, and visual storytelling.

## 🚀 Features

- **AI-Powered Generation**: Creates 6-panel storyboards from single sentence briefs
- **Product Integration**: Seamlessly incorporates your product images into scenes
- **Multiple Visual Styles**: Choose from preset styles (Minimal Studio, Warm Lifestyle, Outdoor Natural)
- **Interactive Editing**: Modify individual panels with natural language instructions
- **Video Export**: Generates MP4 videos with crossfade transitions
- **Shot List Export**: Creates detailed text descriptions of each panel

## 📋 Prerequisites

- **Python 3.9+** (recommended: Python 3.11)
- **OpenRouter API Key** - Get one free at [OpenRouter.ai](https://openrouter.ai/)
- **Internet Connection** - Required for AI image generation

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd spotforge
```

### 2. Install Dependencies
```bash
# Using pip
pip install -e .

# Or install dependencies manually
pip install click python-dotenv pillow moviepy requests tqdm
```

### 3. Set Up Environment
Create a `.env` file in the project root:
```bash
echo "OPENROUTER_API_KEY=your_api_key_here" > .env
```

**Note**: Replace `your_api_key_here` with your actual OpenRouter API key.

## 🎯 Quick Start

### Initialize SpotForge
```bash
spotforge init
```
This checks your configuration and creates necessary directories.

### Generate Your First Storyboard
```bash
spotforge generate \
  --brief "A cozy morning coffee scene with steam rising" \
  --image path/to/your/product.jpg \
  --style "Warm Lifestyle"
```

### Edit Specific Panels
```bash
# Edit panel 3 to adjust lighting
spotforge edit 3 "Make the lighting more golden and warm"

# Edit panel 5 to change the scene
spotforge edit 5 "Move the product to a kitchen counter with plants"
```

### Export Final Video
```bash
# Basic export
spotforge export

# With narration (requires ElevenLabs API setup)
spotforge export --narration --voice-id "your_voice_id"
```

## 📚 Detailed Usage

### Command Reference

#### `spotforge generate`
Creates the initial 6-panel storyboard.

**Options**:
- `--brief, -b` (required): One-sentence description of your storyboard
- `--image, -i` (required): Path to your product image (JPG, PNG, WEBP)
- `--style, -s`: Visual style preset (default: "Warm Lifestyle")
- `--color, -c`: Brand color hex code (e.g., #FF5733)

**Example**:
```bash
spotforge generate \
  --brief "Refreshing summer drink by the pool" \
  --image bottle.jpg \
  --style "Outdoor Natural" \
  --color "#00BFFF"
```

#### `spotforge edit`
Modifies specific panels using natural language.

**Usage**: `spotforge edit <panel_id> <instruction>`

**Examples**:
```bash
spotforge edit 1 "Add more natural lighting"
spotforge edit 4 "Change background to a modern kitchen"
spotforge edit 6 "Make the product more prominent"
```

#### `spotforge export`
Exports the final storyboard as MP4 video and shot list.

**Options**:
- `--narration, -n`: Include AI-generated narration
- `--voice-id, -v`: ElevenLabs voice ID (if narration enabled)

**Examples**:
```bash
# Basic export
spotforge export

# With narration
spotforge export --narration --voice-id "pNInz6obpgDQGcFmaJgB"
```

#### `spotforge init`
Initializes the SpotForge environment and checks configuration.

### Visual Style Presets

#### 🎨 **Minimal Studio**
- **Description**: Clean, simple backgrounds with strong product focus
- **Lighting**: Bright, even lighting
- **Background**: White or light grey seamless paper
- **Mood**: Professional, minimalist

#### 🏠 **Warm Lifestyle**
- **Description**: Cozy, inviting scenes that tell a story
- **Lighting**: Warm, soft lighting, possibly golden hour
- **Background**: Kitchen counter, living room, cozy blanket
- **Mood**: Comfortable, inviting, homely

#### 🌿 **Outdoor Natural**
- **Description**: Natural settings with outdoor lighting
- **Lighting**: Natural daylight
- **Background**: Park, garden, patio, trail
- **Mood**: Fresh, energetic, adventurous

## 📁 Project Structure

SpotForge creates the following directories:

```
spotforge/
├── inputs/          # Input files and references
├── panels/          # Generated panel images
├── exports/         # Final videos and shot lists
├── cache/           # Temporary files and cache
└── shot_plan.json   # Current storyboard data
```

### Output Files

- **`panels/panel_X.jpg`**: Individual storyboard panels
- **`exports/storyboard.mp4`**: Final video with transitions
- **`exports/shot_list.txt`**: Detailed description of each panel
- **`shot_plan.json`**: Complete storyboard data (goals, scenes, paths)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional (for narration)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### API Keys Setup

#### OpenRouter (Required)
1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Navigate to "API Keys" in your dashboard
4. Create a new API key
5. Add it to your `.env` file

#### ElevenLabs (Optional - for narration)
1. Visit [ElevenLabs.io](https://elevenlabs.io/)
2. Sign up and get your API key
3. Add it to your `.env` file

## 🎬 Example Workflow

### Complete Example: Coffee Product Storyboard

```bash
# 1. Initialize
spotforge init

# 2. Generate initial storyboard
spotforge generate \
  --brief "Premium coffee beans creating the perfect morning ritual" \
  --image coffee_bag.jpg \
  --style "Warm Lifestyle" \
  --color "#8B4513"

# 3. Review and edit panels
spotforge edit 2 "Add steam rising from a coffee cup"
spotforge edit 5 "Show the coffee bag on a rustic wooden table"

# 4. Export final video
spotforge export
```

### Result
- 6 beautifully crafted panels showing your coffee product
- Smooth MP4 video with crossfade transitions
- Professional shot list for reference

## 🚨 Troubleshooting

### Common Issues

#### "OPENROUTER_API_KEY not found"
**Solution**: Create a `.env` file with your API key:
```bash
echo "OPENROUTER_API_KEY=your_actual_key" > .env
```

#### "Configuration Errors"
**Solution**: Run the initialization command:
```bash
spotforge init
```

#### "Image generation failed"
**Possible causes**:
- Invalid or expired API key
- Network connectivity issues
- API rate limits reached

**Solution**: Check your API key and internet connection.

#### "Video export failed"
**Solution**: Ensure all panel images were generated successfully:
```bash
ls panels/  # Should show panel_1.jpg through panel_6.jpg
```

### Debug Mode

For detailed error information, you can run commands with Python directly:

```bash
python -m spotforge.cli generate --brief "your brief" --image product.jpg
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

```bash
# Clone and install in development mode
git clone <repo-url>
cd spotforge
pip install -e .

# Install development dependencies
pip install black flake8
```

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. Check this README for common solutions
2. Verify your API keys are correctly set
3. Ensure you have internet connectivity
4. Check the `panels/` directory for generated images
5. Review error messages for specific guidance

---

**Ready to create stunning storyboards?** 🚀

Start with: `spotforge generate --brief "Your amazing product story" --image your_product.jpg`