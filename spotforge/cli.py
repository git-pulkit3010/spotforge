# spotforge/cli.py

import click
import sys
import os
from pathlib import Path

from spotforge import config
from spotforge.orchestrator import generate_storyboard, edit_panel, export_storyboard

sys.path.insert(0, str(Path(__file__).parent.parent))

@click.group()
def main():
    """SpotForge: Turn a single sentence into a polished, narrated, product-fused storyboard video."""
    pass

@main.command()
@click.option('--brief', '-b', required=True, help='The one-sentence brief for the storyboard.')
@click.option('--image', '-i', type=click.Path(exists=True), required=True, help='Path to the product image file.')
@click.option('--style', '-s', type=click.Choice(list(config.PRESETS.keys())), default=config.DEFAULT_STYLE, help='Visual style preset.')
@click.option('--color', '-c', default=None, help='Brand color hex code (e.g., #FF5733).')
def generate(brief: str, image: str, style: str, color: str):
    """Generate the initial 6-panel storyboard."""
    click.echo(f"Generating storyboard for brief: '{brief}'")
    click.echo(f"Using product image: {image}")
    click.echo(f"Style: {style}")
    if color:
        click.echo(f"Brand color: {color}")

    success = generate_storyboard(brief=brief, image_path=image, style=style, brand_color=color)
    if success:
        click.echo("Storyboard generation complete!")
    else:
        click.echo("Storyboard generation failed.", err=True)
        sys.exit(1)

@main.command()
@click.argument('panel_id', type=int)
@click.argument('instruction', type=str)
def edit(panel_id: int, instruction: str):
    """Edit a specific panel using natural language."""
    if not 1 <= panel_id <= config.MAX_PANELS:
        click.echo(f"Error: Panel ID must be between 1 and {config.MAX_PANELS}.", err=True)
        sys.exit(1)

    click.echo(f"Editing panel {panel_id} with instruction: '{instruction}'")

    success = edit_panel(panel_id=panel_id, instruction=instruction)
    if success:
        click.echo(f"Panel {panel_id} updated successfully!")
    else:
        click.echo(f"Failed to update panel {panel_id}.", err=True)
        sys.exit(1)

@main.command()
@click.option('--narration', '-n', is_flag=True, help='Add optional narration (requires ElevenLabs API key).')
@click.option('--voice-id', '-v', default='default', help='ElevenLabs voice ID (if narration enabled).')
def export(narration: bool, voice_id: str):
    """Export the final storyboard as MP4 and shot list."""
    click.echo("Exporting final storyboard...")
    if narration:
        click.echo("  - Including narration (if configured).")
        click.echo(f"  - Using voice ID: {voice_id}")

    success = export_storyboard(include_narration=narration, voice_id=voice_id)
    if success:
        click.echo("Export complete! Check the 'exports' directory.")
    else:
        click.echo("Export failed.", err=True)
        sys.exit(1)

@main.command()
def init():
    """Initialize SpotForge environment (checks config, creates dirs)."""
    click.echo("Initializing SpotForge...")
    errors = config.validate_config()
    if errors:
        click.echo("Configuration Issues Found:")
        for error in errors:
            click.echo(f" - {error}", err=True)
        click.echo("Please fix the issues and try again.", err=True)
        sys.exit(1)
    else:
        click.echo("Configuration OK.")
        click.echo(f"Directories ensured: inputs, panels, exports, cache")

if __name__ == '__main__':
    main()
