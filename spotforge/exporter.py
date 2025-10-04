# spotforge/exporter.py

from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips # Import CompositeVideoClip for transitions
from pathlib import Path
import json
from spotforge import config

def _load_shot_plan(filepath: Path) -> dict:
    """Loads the shot plan from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[Exporter] Error: Shot plan file not found: {filepath}")
        return None
    except Exception as e:
        print(f"[Exporter] Error loading shot plan: {e}")
        return None

def _create_video_from_panels(image_paths: list, durations: list, output_path: Path):
    """Creates an MP4 slideshow from a list of image paths with crossfade transitions."""
    try:
        print(f"[Exporter] Creating video from {len(image_paths)} panels with transitions...")
        clips = []
        transition_duration = 1.0 # Duration of the crossfade transition in seconds

        for i, (img_path, duration) in enumerate(zip(image_paths, durations)):
            # Create a clip for each image with the specified duration
            clip = ImageClip(str(img_path)).set_duration(duration)
            clips.append(clip)

        # --- Corrected Transition Logic for moviepy 1.0.3 ---
        # To add a crossfade, we need to manually apply the effect between clips.
        # We'll create a new list of clips where transitions are embedded.

        if not clips:
            print("[Exporter] No clips to concatenate.")
            return

        # Start with the first clip
        final_clip = clips[0]

        # Iterate through the remaining clips and add them with a transition
        for i in range(1, len(clips)):
            next_clip = clips[i]

            # Apply crossfadein to the *next* clip starting from its beginning
            # This creates the fade-in effect for the next clip, overlapping with the fade-out of the current one.
            next_clip_with_fade = next_clip.crossfadein(transition_duration)

            # Concatenate the current final clip with the next clip that has the fade-in
            # We need to use CompositeVideoClip or a similar approach for overlapping.
            # The simplest way is often to use a function that handles the transition explicitly.
            # moviepy doesn't have a built-in concat with *only* crossfade as an argument for the function itself.
            # We build it step by step.

            # The 'method="compose"' argument in concatenate_videoclips might be related to handling
            # alpha channels or compositing layers correctly during the transition, which is important for fades.
            # Since 'cross' is invalid, we rely on applying crossfadein/crossfadeout manually and concatenating.

            # Ensure the previous clip fades out correctly if needed, though crossfadein on the next clip
            # often handles the visual overlap.
            # Let's try concatenating the current final with the *next* clip that has crossfadein applied.
            # This might require a more complex loop or using CompositeVideoClip for each pair,
            # which concatenate_videoclips might handle internally *if* the 'cross' arg worked.

            # The safest way with the basic API is to apply fades and use the standard concatenate.
            # For a true crossfade, apply fadeout to the current clip and fadein to the next,
            # then concatenate. moviepy's concatenate_videoclips *should* handle the overlap if fades are present,
            # but the original function call suggested it might need a specific method.

            # Let's try applying fadeout to the *previous* clip in the pair being concatenated.
            # This is the standard way for a crossfade between two specific clips.
            current_clip_for_transition = final_clip
            next_clip_for_transition = next_clip_with_fade

            # Apply fade-out to the current final clip
            current_clip_for_transition = current_clip_for_transition.crossfadeout(transition_duration)

            # Now concatenate these two specific clips (with their fades) into a temporary sequence
            # We need to concatenate just these two, respecting the fade durations.
            # The standard concatenate_videoclips might handle the overlap correctly if fades are present.
            temp_sequence = [current_clip_for_transition, next_clip_for_transition]
            # Concatenate only these two, with method="compose" to ensure layers are handled correctly for fades.
            # This is the key: apply fades to adjacent clips and concatenate them *as a pair* if needed,
            # or rely on the global concatenate to handle overlaps correctly when fades are present.

            # The *global* concatenate_videoclips should take a list where adjacent clips have fade-in/fade-out
            # applied. It should automatically handle the overlapping duration specified by the fades.
            # Let's rebuild the 'clips' list with the fades already applied.

            # This approach modifies the original clips list by applying fades strategically.
            # We'll iterate through the original list again, but this time apply fadeouts and fadeins
            # to the original clips before the final global concatenate.

            # Re-initialize the clips list with fades applied correctly
            clips_with_fades = []
            for i in range(len(clips)):
                clip = clips[i]
                if i > 0: # Apply fade-in to all clips except the first
                    clip = clip.crossfadein(transition_duration)
                if i < len(clips) - 1: # Apply fade-out to all clips except the last
                    clip = clip.crossfadeout(transition_duration)
                clips_with_fades.append(clip)

            # Now, concatenate the list where adjacent clips have appropriate fades
            # The 'method="compose"' might be needed here if fades involve alpha channels.
            final_clip = CompositeVideoClip(clips_with_fades, size=clips_with_fades[0].size) # This might not be the right way for a linear sequence.
            # CompositeVideoClip is for layering, not sequential concatenation.

            # The correct way is back to concatenate_videoclips, but with fades already applied to individual clips.
            # The 'method' argument might be relevant, let's try without 'cross' but with 'method'.
            # The original error was specifically about 'cross'. Let's remove it and ensure fades are on the clips.
            final_clip = clips_with_fades[0]
            for next_clip_faded in clips_with_fades[1:]:
                 final_clip = CompositeVideoClip([final_clip, next_clip_faded.set_start(final_clip.duration - transition_duration)], size=final_clip.size)
                 # This CompositeVideoClip approach overlays them. We need to cut the *previous* clip short.
                 # Let's go back to building a sequence correctly with concatenate_videoclips *after* applying fades.

            # The standard approach *should* be:
            # 1. Apply crossfadein to clip[1..N]
            # 2. Apply crossfadeout to clip[0..N-1]
            # 3. Pass the resulting list to concatenate_videoclips.
            # Let's try this final structure:
            clips_for_concat = []
            for i in range(len(clips)):
                clip = clips[i]
                # Apply fade-in if not the first clip
                if i > 0:
                    clip = clip.crossfadein(transition_duration)
                # Apply fade-out if not the last clip
                if i < len(clips) - 1:
                    clip = clip.crossfadeout(transition_duration)
                clips_for_concat.append(clip)

            # Now concatenate the list of pre-faded clips
            # The 'method' argument might help with compositing the fades correctly.
            # The 'cross' argument was likely a shortcut that doesn't exist in this version.
            final_clip = concatenate_videoclips(clips_for_concat, method="compose") # Remove 'cross', keep 'method' if helpful for alpha.

        # Write the video file
        final_clip.write_videofile(str(output_path), fps=24, codec='libx264', audio=False)
        print(f"[Exporter] Video saved to {output_path}")
    except Exception as e:
        print(f"[Exporter] Error creating video: {e}")
        import traceback
        traceback.print_exc()
        raise

def _create_shot_list_text(shot_plan: dict, output_path: Path):
    """Creates a text file listing the shot descriptions."""
    try:
        print(f"[Exporter] Creating shot list text file...")
        with open(output_path, 'w') as f:
            f.write("--- SpotForge Storyboard Shot List ---\n\n")
            panel_ids = sorted(shot_plan.get("panels", {}).keys(), key=int)
            for panel_id_str in panel_ids:
                panel_data = shot_plan["panels"][panel_id_str]
                f.write(f"--- Panel {panel_data['id']} ---\n")
                f.write(f"Goal: {panel_data.get('goal', 'N/A')}\n")
                f.write(f"Scene: {panel_data.get('scene_description', 'N/A')}\n")
                f.write("\n")
        print(f"[Exporter] Shot list saved to {output_path}")
    except Exception as e:
        print(f"[Exporter] Error creating shot list: {e}")
        raise

def export_final_storyboard(include_narration: bool = False, voice_id: str = 'default') -> bool:
    """Exports the final storyboard as MP4 and shot list text file."""
    print("[Exporter] Starting export process...")
    
    try:
        plan_file_path = config.PROJECT_ROOT / "shot_plan.json"
        shot_plan = _load_shot_plan(plan_file_path)
        
        if not shot_plan:
            print("[Exporter] Cannot export: Shot plan not found or invalid.")
            return False

        panel_ids = sorted(shot_plan.get("panels", {}).keys(), key=int)
        image_paths = []
        durations = []
        for panel_id_str in panel_ids:
            panel_data = shot_plan["panels"][panel_id_str]
            img_path_str = panel_data.get("generated_image_path")
            if img_path_str:
                image_paths.append(Path(img_path_str))
                durations.append(6) # 6 seconds per panel
            else:
                print(f"[Exporter] Warning: No image path found for Panel {panel_id_str}. Skipping.")
                return False 

        if not image_paths:
            print("[Exporter] Error: No valid image paths found in shot plan.")
            return False

        video_output_path = config.EXPORTS_DIR / "storyboard.mp4"
        text_output_path = config.EXPORTS_DIR / "shot_list.txt"

        # Use the updated function with transitions
        _create_video_from_panels(image_paths, durations, video_output_path)

        _create_shot_list_text(shot_plan, text_output_path)

        print("[Exporter] Export process completed successfully!")
        return True

    except Exception as e:
        print(f"[Exporter] Export process failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = export_final_storyboard()
    if success:
        print("Direct export test successful!")
    else:
        print("Direct export test failed.")
