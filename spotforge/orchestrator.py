# spotforge/orchestrator.py

import json
from pathlib import Path
from spotforge import config
from spotforge.prompter import create_initial_plan, create_edit_prompt_for_panel
from spotforge.generator import generate_panel
from spotforge.exporter import export_final_storyboard

SHOT_PLAN_FILENAME = "shot_plan.json"

def _save_shot_plan(plan: dict, filepath: Path):
    """Saves the shot plan to a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(plan, f, indent=4)
        print(f"[Orchestrator] Shot plan saved to {filepath}")
    except Exception as e:
        print(f"[Orchestrator] Error saving shot plan: {e}")

def _load_shot_plan(filepath: Path) -> dict:
    """Loads the shot plan from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[Orchestrator] Shot plan file not found: {filepath}")
        return None
    except Exception as e:
        print(f"[Orchestrator] Error loading shot plan: {e}")
        return None

def generate_storyboard(brief: str, image_path: str, style: str, brand_color: str = None) -> bool:
    """Orchestrates the full storyboard generation process."""
    print(f"[Orchestrator] Received request to generate storyboard.")
    print(f"  Brief: {brief}")
    print(f"  Product Image: {image_path}")
    print(f"  Style: {style}")
    print(f"  Color: {brand_color}")
    
    try:
        print("[Orchestrator] Stage 1: Planning...")
        shot_plan = create_initial_plan(brief, style)
        
        shot_plan["product_image_path"] = image_path
        
        plan_file_path = config.PROJECT_ROOT / SHOT_PLAN_FILENAME
        _save_shot_plan(shot_plan, plan_file_path)
        
        print("[Orchestrator] Stage 2: Generating panels...")
        shot_plan = _load_shot_plan(plan_file_path)
        
        if not shot_plan:
            print("[Orchestrator] Failed to load shot plan for generation.")
            return False
            
        product_image_path = shot_plan.get("product_image_path")
        if not product_image_path or not Path(product_image_path).exists():
             print(f"[Orchestrator] Warning: Product image path '{product_image_path}' is invalid or missing. Proceeding without fusion.")
             product_image_path = None

        panel_ids = sorted(shot_plan.get("panels", {}).keys(), key=int)
        for panel_id_str in panel_ids:
            panel_id = int(panel_id_str)
            panel_data = shot_plan["panels"][panel_id_str]
            
            print(f"[Orchestrator] --- Generating Panel {panel_id} ---")
            image_path_obj = generate_panel(panel_data, product_image_path=product_image_path)
            
            shot_plan["panels"][panel_id_str]["generated_image_path"] = str(image_path_obj)
            
            _save_shot_plan(shot_plan, plan_file_path)
            
        print("[Orchestrator] All panels generated successfully!")
        print("[Orchestrator] Full storyboard generation complete!")
        return True
        
    except Exception as e:
        print(f"[Orchestrator] Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def edit_panel(panel_id: int, instruction: str) -> bool:
    """Orchestrates the editing of a specific panel."""
    print(f"[Orchestrator] Received request to edit panel {panel_id}.")
    print(f"  Instruction: {instruction}")
    
    try:
        plan_file_path = config.PROJECT_ROOT / SHOT_PLAN_FILENAME
        shot_plan = _load_shot_plan(plan_file_path)
        
        if not shot_plan:
            print("[Orchestrator] Cannot edit: Shot plan not found.")
            return False

        panel_id_str = str(panel_id)
        if panel_id_str not in shot_plan.get("panels", {}):
            print(f"[Orchestrator] Error: Panel ID {panel_id} not found in shot plan.")
            return False

        current_panel_data = shot_plan["panels"][panel_id_str]
        print(f"[Orchestrator] Editing Panel {panel_id}: {current_panel_data.get('goal', 'No goal found')}")

        consistent_elements = current_panel_data.get("consistent_elements", "")
        original_scene_desc = current_panel_data.get("scene_description", "")
        original_full_prompt_for_editing = f"Scene Description:\n{original_scene_desc}\n\nConsistent Elements:\n{consistent_elements}"

        print("[Orchestrator] Creating edited prompt...")
        edited_prompt = create_edit_prompt_for_panel(
            current_panel_prompt=original_full_prompt_for_editing,
            edit_instruction=instruction,
            consistent_elements=consistent_elements
        )
        print(f"[Orchestrator] Edited prompt created.")

        # Get the global product image path for fusion during edit
        product_image_path = shot_plan.get("product_image_path")

        edited_panel_data = {
            "id": panel_id,
            "scene_description": edited_prompt,
            "consistent_elements": consistent_elements,
            "goal": current_panel_data.get("goal", ""),
        }
        
        print(f"[Orchestrator] Calling generator for edited Panel {panel_id}...")
        new_image_path = generate_panel(edited_panel_data, product_image_path=product_image_path) # Pass product_image_path here too
        
        shot_plan["panels"][panel_id_str]["generated_image_path"] = str(new_image_path)
        if "edit_history" not in shot_plan["panels"][panel_id_str]:
            shot_plan["panels"][panel_id_str]["edit_history"] = []
        shot_plan["panels"][panel_id_str]["edit_history"].append(instruction)
        
        _save_shot_plan(shot_plan, plan_file_path)
        
        print(f"[Orchestrator] Panel {panel_id} updated successfully!")
        return True
        
    except Exception as e:
        print(f"[Orchestrator] Error during panel edit: {e}")
        import traceback
        traceback.print_exc()
        return False

def export_storyboard(include_narration: bool = False, voice_id: str = 'default') -> bool:
    """Orchestrates the export process."""
    print(f"[Orchestrator] Received request to export storyboard.")
    print(f"  Include Narration: {include_narration}")
    print(f"  Voice ID: {voice_id}")
    
    success = export_final_storyboard(include_narration=include_narration, voice_id=voice_id)
    
    if success:
        print("[Orchestrator] Export orchestrated successfully!")
    else:
        print("[Orchestrator] Export orchestration failed.")
        
    return success
