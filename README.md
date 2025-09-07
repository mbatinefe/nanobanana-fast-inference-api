# Nanobanana Fast Inference API

For me to use on weekend (free api offering from google)

A Python script for generating gothic fantasy illustrations using Google's Gemini 2.5 Flash image generation model.

## Features

- Batch processes prompts from `prompts.txt`
- Generates images with gothic fantasy, dark academia aesthetic
- Automatically saves generated images to `images/` directory
- Uses numbered prompts for organized output

## Setup

1. Install dependencies: `uv sync`
2. Copy `.example.env` to `.env` and add your `GEMINI_API_KEY`
3. Add your prompts to `prompts.txt` (format: `1- Your prompt here`)
4. Run: `python main.py`

## Output

Generated images are saved as `images/{number}.png` based on the prompt numbering.