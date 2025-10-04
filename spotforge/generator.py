# spotforge/generator.py

import requests
import base64
import io
import re
from pathlib import Path
from PIL import Image
from spotforge import config
import time

def _construct_prompt(panel_data: dict) -> str:
    """Constructs the final prompt string for the API call from panel data."""
    scene_desc = panel_data.get("scene_description", "")
    consistent_elements = panel_data.get("consistent_elements", "")
    
    # Combine scene description and consistent elements into a single prompt
    final_prompt = (
        f"Generate a high-quality, realistic image in 16:9 aspect ratio based on the following description:\n\n"
        f"Scene Description:\n{scene_desc}\n\n"
        f"Consistent Elements (Maintain these strictly):\n{consistent_elements}\n\n"
        f"CRITICAL INSTRUCTION FOR FUSION: The user will provide a real image of their product. "
        f"Seamlessly integrate this specific product into the scene described above. "
        f"Match the lighting, perspective, and context naturally. "
        f"The product's logo, shape, color, and material properties must be accurately represented as per the provided image. "
        f"Do not generate a generic product; use the provided one.\n\n"
        f"Please create a detailed, professional image that captures this scene perfectly, adhering to all instructions above."
    )
    return final_prompt

def _encode_image_to_base64(image_path: str) -> str:
    """Encodes an image file to a base64 string."""
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        return encoded_image
    except Exception as e:
        print(f"[Generator] Error encoding image {image_path}: {e}")
        raise

def _extract_image_from_response(response_data: dict) -> bytes:
    """Extracts image data from OpenRouter API response."""
    try:
        # Check if response has the expected structure with images
        if 'choices' in response_data and len(response_data['choices']) > 0:
            choice = response_data['choices'][0]
            
            # Method 1: Check for images array in message
            if 'message' in choice and 'images' in choice['message']:
                images = choice['message']['images']
                if images and len(images) > 0:
                    image_url = images[0].get('image_url', {}).get('url', '')
                    if 'base64,' in image_url:
                        b64_data = image_url.split('base64,', 1)[1]
                        return base64.b64decode(b64_data)
            
            # Method 2: Check for content that might contain base64 image
            if 'message' in choice and 'content' in choice['message']:
                content = choice['message']['content']
                # Look for base64 image pattern in content
                base64_pattern = r'data:image/\w+;base64,([A-Za-z0-9+/=]+)'
                matches = re.findall(base64_pattern, content)
                if matches:
                    return base64.b64decode(matches[0])
                
                # If content is directly base64 encoded image data
                if len(content) > 1000:  # Heuristic: base64 images are large
                    try:
                        # Try to decode as base64 directly
                        return base64.b64decode(content)
                    except:
                        pass
            
            # Method 3: Check for alternative response structure
            if 'images' in response_data:
                images = response_data['images']
                if images and len(images) > 0:
                    image_data = images[0].get('data', '')
                    if image_data:
                        return base64.b64decode(image_data)
        
        print(f"[Generator] Could not extract image from response structure: {response_data.keys()}")
        return None
        
    except Exception as e:
        print(f"[Generator] Error extracting image from response: {e}")
        return None

def _call_openrouter_api(prompt: str, product_image_path: str = None, retries: int = 3, delay: int = 5) -> bytes:
    """Calls the OpenRouter API to generate an image."""
    
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "SpotForge",
    }

    # System prompt for image generation guidance
    system_prompt = (
        "You are an expert at generating high-quality, realistic images based on detailed text descriptions. "
        "Your output must be a single, detailed image. "
        "When a user provides a product image, you must seamlessly blend it into the described scene, "
        "matching lighting, perspective, and context accurately. "
        "Ensure the product's specific details (logo, color, shape) are preserved. "
        "Return ONLY the generated image as base64 data, no additional text."
    )

    # Prepare the payload
    payload = {
        "model": config.OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7,
    }

    # Add the image to the payload if provided
    if product_image_path and Path(product_image_path).exists():
        print(f"[Generator] Adding product image for fusion: {product_image_path}")
        try:
            encoded_image = _encode_image_to_base64(product_image_path)
            # Modify the user message content to include the image
            payload["messages"][1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            })
            print("[Generator] Product image data (base64) added to request.")
        except Exception as img_err:
            print(f"[Generator] Warning: Failed to load/encode product image {product_image_path}: {img_err}. Proceeding without fusion for this call.")
    else:
        if product_image_path:
            print(f"[Generator] Warning: Product image path '{product_image_path}' not found. Proceeding without fusion.")

    for attempt in range(retries + 1):
        try:
            print(f"[Generator] Calling OpenRouter API (Attempt {attempt + 1}/{retries + 1})...")
            response = requests.post(config.OPENROUTER_BASE_URL, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[Generator] API call successful, extracting image data...")
                
                # Extract image from response
                image_bytes = _extract_image_from_response(response_data)
                
                if image_bytes:
                    print(f"[Generator] Successfully extracted image data ({len(image_bytes)} bytes)")
                    return image_bytes
                else:
                    print(f"[Generator] Could not extract image from response. Response structure: {list(response_data.keys())}")
                    if 'choices' in response_data:
                        choice = response_data['choices'][0]
                        print(f"[Generator] Choice keys: {choice.keys() if isinstance(choice, dict) else 'N/A'}")
                        if 'message' in choice:
                            print(f"[Generator] Message keys: {choice['message'].keys()}")
                    
                    # Save debug info
                    debug_file = config.CACHE_DIR / f"api_response_debug_{int(time.time())}.json"
                    with open(debug_file, 'w') as f:
                        import json
                        # Remove large base64 data for readability
                        debug_data = response_data.copy()
                        if 'choices' in debug_data:
                            for choice in debug_data['choices']:
                                if 'message' in choice and 'content' in choice['message']:
                                    content = choice['message']['content']
                                    if len(content) > 500:
                                        choice['message']['content'] = content[:500] + "...[truncated]"
                        json.dump(debug_data, f, indent=2)
                    print(f"[Generator] Saved debug response to: {debug_file}")
                    
                    raise Exception("Could not extract image data from API response")
                    
            else:
                print(f"[Generator] API call failed with status {response.status_code}: {response.text[:500]}")
                raise Exception(f"API call failed with status {response.status_code}")

        except Exception as e:
            print(f"[Generator] API call failed: {e}")
            if attempt < retries:
                print(f"[Generator] Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise  # Re-raise the last exception if all retries failed

def _save_image(image_data: bytes, filepath: Path):
    """Saves image bytes to a file."""
    try:
        image = Image.open(io.BytesIO(image_data))
        image.save(filepath, 'PNG')
        print(f"[Generator] Image saved to {filepath}")
    except Exception as e:
        print(f"[Generator] Error saving image {filepath}: {e}")
        raise

def generate_panel(panel_data: dict, product_image_path: str = None) -> Path:
    """Generates a single panel image based on its data."""
    panel_id = panel_data["id"]
    print(f"[Generator] Generating Panel {panel_id}...")
    
    prompt = _construct_prompt(panel_data)
    
    image_bytes = _call_openrouter_api(prompt, product_image_path=product_image_path)
    
    filename = f"panel_{panel_id}.png"
    image_path = config.PANELS_DIR / filename
    
    _save_image(image_bytes, image_path)
    
    print(f"[Generator] Panel {panel_id} generated successfully.")
    return image_path