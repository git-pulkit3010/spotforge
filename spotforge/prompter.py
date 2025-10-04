# spotforge/prompter.py

import json
from typing import Dict, Any, List
from spotforge import config

def _parse_brief(brief: str) -> Dict[str, Any]:
    """Parses the one-sentence brief into key components."""
    components = {}
    parts = [part.strip() for part in brief.split(';')]
    
    if parts:
        components['main_idea'] = parts[0]
        
    for part in parts[1:]:
        if ':' in part:
            key, value = part.split(':', 1)
            key = key.strip().lower()
            value = value.strip().strip("'\"")
            components[key] = value
        else:
            pass # Ignore parts without colon for now
            
    expected_keys = ['main_idea', 'target', 'mood', 'cta']
    for key in expected_keys:
        if key not in components:
            components[key] = ""
            
    return components

def _select_preset(style_name: str) -> Dict[str, str]:
    """Retrieves the preset configuration."""
    return config.PRESETS.get(style_name, config.PRESETS[config.DEFAULT_STYLE])

def _infer_product_type_from_brief(brief: str) -> str:
    """Attempts to infer the product type from the brief."""
    # Simple keyword matching - can be improved later
    brief_lower = brief.lower()
    if 't-shirt' in brief_lower or 'shirt' in brief_lower:
        return 't-shirt'
    elif 'mug' in brief_lower:
        return 'mug'
    elif 'sneaker' in brief_lower or 'shoe' in brief_lower:
        return 'sneaker'
    # Add more as needed
    return 'product' # Default fallback

def _create_shot_list(brief_components: Dict[str, str], preset: Dict[str, str], product_type: str) -> List[Dict[str, Any]]:
    """Creates a detailed 6-panel shot list based on parsed brief, preset, and product type."""
    main_idea = brief_components.get('main_idea', '')
    target = brief_components.get('target', '')
    mood = brief_components.get('mood', '')
    cta = brief_components.get('cta', '')
    
    lighting = preset.get('lighting', '')
    background = preset.get('background', '')
    preset_mood = preset.get('mood', '')
    
    combined_mood = f"{mood}, {preset_mood}".strip(', ')
    
    # Define consistent elements using the inferred product type
    consistent_elements = (
        f"{product_type.title()}: specific shape, color, logo visible. "
        "Protagonist: unseen or implied presence. "
        f"Consistent visual style: {combined_mood}, {lighting}, {background}. "
        "Maintain consistent aspect ratio (16:9) and camera perspective."
    )
    
    shot_list = []
    
    shot_list.append({
        "id": 1,
        "goal": "Establish setting, mood, and introduce the product.",
        "scene_description": (
            f"Establishing shot for a {main_idea}. "
            f"Setting: {background}. "
            f"Lighting: {lighting}, creating a {combined_mood} atmosphere. "
            f"Product: A {product_type} placed prominently, showing its shape and logo. "
            f"Details: Subtle elements suggesting {target} context. "
            f"Camera: Wide shot, 16:9 aspect ratio."
        ),
        "consistent_elements": consistent_elements,
        "composition_notes": "Rule of thirds, product slightly off-center."
    })
    
    # Repeat for panels 2-6, replacing 'mug' with {product_type}
    shot_list.append({
        "id": 2,
        "goal": "Show the product in use within the target context.",
        "scene_description": (
            f"Mid-shot showing the {target} using the {product_type}. "
            f"Action: Holding, wearing, or interacting with the {product_type}. "
            f"Setting: Part of the {background}. "
            f"Lighting: {lighting}, emphasizing the texture and details. "
            f"Product Details: {product_type.title()} shape, color, and logo clearly visible. "
            f"Camera: Medium shot, 16:9."
        ),
        "consistent_elements": consistent_elements,
        "composition_notes": "Focus on hands/product interaction, background slightly blurred."
    })
    
    shot_list.append({
        "id": 3,
        "goal": "Highlight a key product feature.",
        "scene_description": (
            f"Close-up shot focusing on a key feature of the {product_type}. "
            f"Example Feature: Logo detail, fabric texture, material quality. "
            f"Lighting: {lighting}, highlighting the feature. "
            f"Product Details: Clear view of the {product_type}'s design. "
            f"Setting: Continuation of {background}. "
            f"Camera: Close-up, 16:9."
        ),
        "consistent_elements": consistent_elements,
        "composition_notes": "Center focus on feature/detail, shallow depth of field."
    })
    
    shot_list.append({
        "id": 4,
        "goal": "Imply social context or lifestyle benefit.",
        "scene_description": (
            f"Wider lifestyle shot showing the {target} benefiting from the {product_type}. "
            f"Scene: {target} using/wearing the {product_type} in {background}. "
            f"Elements: Contextual items suggesting {target} lifestyle. "
            f"Lighting: {lighting}, creating an inviting scene. "
            f"Product: {product_type} visible and integrated naturally. "
            f"Camera: Wide/Medium shot, 16:9."
        ),
        "consistent_elements": consistent_elements,
        "composition_notes": "Show environment and implied use, product integrated naturally."
    })
    
    shot_list.append({
        "id": 5,
        "goal": "Present the CTA and potentially the product packaging.",
        "scene_description": (
            f"Flat lay or angled shot of the {product_type}, possibly next to its packaging. "
            f"Focus: Product packaging design, prominently displaying the CTA '{cta}'. "
            f"Setting: Clean section of {background}. "
            f"Lighting: {lighting}, ensuring product and text are well-lit. "
            f"Product: {product_type} and packaging shown clearly. "
            f"Text: '{cta}' visible and readable. "
            f"Camera: Top-down or slight angle, 16:9."
        ),
        "consistent_elements": consistent_elements,
        "composition_notes": "Clear view of packaging/CTA, product centered."
    })
    
    shot_list.append({
        "id": 6,
        "goal": "Leave a strong final impression of the brand/product.",
        "scene_description": (
            f"Artistic or symbolic closing shot. "
            f"Idea: The {product_type} alone, perhaps with subtle light rays or context. "
            f"Mood: Reinforce the {combined_mood} feeling. "
            f"Lighting: {lighting}, creating a sense of satisfaction. "
            f"Product: Strong, clear view of the {product_type} and its logo. "
            f"Background: Simplified version of {background}. "
            f"Camera: Tight composition, 16:9."
        ),
        "consistent_elements": consistent_elements,
        "composition_notes": "Strong visual impact, focus on brand/product essence."
    })
    
    return shot_list

def create_initial_plan(brief: str, style: str) -> Dict[str, Any]:
    """Main function to create the initial storyboard plan."""
    print(f"[Prompter] Parsing brief: {brief}")
    brief_components = _parse_brief(brief)
    product_type = _infer_product_type_from_brief(brief) # Infer product type
    print(f"[Prompter] Inferred product type: {product_type}")
    print(f"[Prompter] Selected style: {style}")
    preset = _select_preset(style)
    
    print("[Prompter] Creating shot list...")
    shot_list = _create_shot_list(brief_components, preset, product_type) # Pass product_type
    
    plan = {
        "original_brief": brief,
        "selected_style": style,
        "inferred_product_type": product_type, # Store the inferred type
        "parsed_components": brief_components,
        "preset_details": preset,
        "panels": {panel["id"]: panel for panel in shot_list}
    }
    
    print("[Prompter] Initial plan created successfully.")
    return plan

def create_edit_prompt_for_panel(current_panel_prompt: str, edit_instruction: str, consistent_elements: str) -> str:
    """Constructs a prompt for editing a specific panel."""
    edit_prompt = (
        f"Revise the following image generation prompt based on the instruction. "
        f"IMPORTANT: Ensure the elements listed under 'Consistent Elements' remain unchanged.\n\n"
        f"Original Prompt:\n{current_panel_prompt}\n\n"
        f"Edit Instruction:\n{edit_instruction}\n\n"
        f"Consistent Elements (DO NOT CHANGE):\n{consistent_elements}\n\n"
        f"Revised Prompt (incorporating the edit while preserving consistency):"
    )
    return edit_prompt

if __name__ == '__main__':
    test_brief = "Cozy autumn t-shirt launch; target: students; mood: warm; CTA: 'wear your focus'."
    test_style = "Warm Lifestyle"
    
    plan = create_initial_plan(test_brief, test_style)
    
    print("\n--- Generated Shot Plan ---")
    print(json.dumps(plan, indent=2))
