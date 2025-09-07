import re
from google import genai
from google.genai import types
import mimetypes
import base64
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# Ensure output directory exists
os.makedirs('images', exist_ok=True)

master_prompt = """

-in the style of a gothic fantasy illustration, dark academia aesthetic, moody and atmospheric, painterly, intricate ornate details, dramatic chiaroscuro lighting, somber color palette of deep browns and muted crimson, mysterious, historical fantasy **a wide-format image, depicting a vast and panoramic scene, horizontal composition**

"""


def save_binary_file(file_name, data):
    try:
        with open(file_name, "wb") as f:
            f.write(data)
        print(f"File saved to: {file_name}")
    except Exception as e:
        print(f"Error saving file {file_name}: {e}")

def crop_center_to_16x9(input_path, output_path=None):
    try:
        image = Image.open(input_path)
        width, height = image.size
        target_ratio = 16 / 9

        if width / height > target_ratio:
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            crop_box = (left, 0, left + new_width, height)
        else:
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            crop_box = (0, top, width, top + new_height)

        cropped = image.crop(crop_box)
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_16x9{ext}"
        cropped.save(output_path)
        print(f"Saved 16:9 crop to: {output_path}")
    except Exception as e:
        print(f"Error cropping to 16:9 for {input_path}: {e}")

def generate(prompt, file_number):
    try:
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        model = "gemini-2.5-flash-image-preview"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=[
                "IMAGE",
                "TEXT",
            ],
        )

        file_index = 0
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue
            if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data
                file_extension = mimetypes.guess_extension(inline_data.mime_type) or '.png'
                file_name = f"images/{file_number}{file_extension}"
                file_index += 1
                save_binary_file(file_name, data_buffer)
                crop_center_to_16x9(file_name)
            #else:
                #print(chunk.text)
    except Exception as e:
        print(f"Error generating content for prompt {file_number}: {e}")


# Lets open prompts.txt and read the file
try:
    with open('prompts.txt', 'r') as file:
        prompts = file.readlines()
except FileNotFoundError:
    print("Error: prompts.txt file not found!")
    exit(1)
except Exception as e:
    print(f"Error reading prompts.txt: {e}")
    exit(1)

# For each line in the file, add the helper prompt to the end of the line
# But first, lets get first 1 or 2 digit numbers also "-" from beginning of the line
# Then add the helper prompt to the end of the line
for prompt in prompts:
    # Skip empty lines
    if not prompt.strip():
        continue
        
    # Only find in first 5 characters
    numbers = re.findall(r'\d+', prompt[:5])
    file_number = "0"  # Default filename if no number found
    
    if numbers:
        file_number = numbers[0]
        # Remove the number and "-", we will use for filename later
        prompt = prompt.replace(f"{numbers[0]}-", "", 1).strip()
    
    # Add the master prompt to the cleaned prompt
    full_prompt = prompt + master_prompt

    full_prompt = f"""
    {full_prompt}
    """
    print(f"Processing prompt {file_number}:")
    print(full_prompt)

    generate(full_prompt, file_number)

