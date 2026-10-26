#!/usr/bin/env python3
"""app_presets.py — ready-to-paste output templates per DCC.

Each preset is a dict you can drop into the corresponding app's output config.
The placeholders (e.g. {show}, {shot}, {rev}) are filled by the app's native
token substitution — check the app's docs for the exact syntax.

The naming pattern follows the ETC@USC / MovieLabs TR-VFX-IS v1.0 spec:

    <showid>_<vfx-sequence>_<vfx-shot>_<image-type>_<vendor-code>_<revision-code>
    {_<identifying-description>}.<frame-number>.<file-extension>

Apps covered:
  - Nuke Write node
  - Photoshop Export Layers to Files / Save for Web (Legacy)
  - Blender File Output (Compositor) and Output Properties (Render)
  - DaVinci Resolve render name
  - After Effects render queue
  - Houdini COP / Render Output
"""

PRESETS = {
    "nuke_write_matte": {
        "app": "Nuke",
        "node": "Write",
        "file_knob": "file",
        "template": "{show}_{seq}_{shot}_matt01_{vendor}_v{rev:03d}_{description}.####.exr",
        "notes": [
            "Set the `file type` knob to the literal extension, not a protocol prefix (exr/).",
            "Set `colorspace` to match your pipeline (typically linear / sRGB).",
            "Enable 'read file' to verify the render after the fact.",
        ],
        "example_filled": "un-ff25_sb_0100_matt01_dd_v001_mp-v023.1001.exr",
    },

    "nuke_write_comp": {
        "app": "Nuke",
        "node": "Write",
        "file_knob": "file",
        "template": "{show}_{seq}_{shot}_comp_{vendor}_v{rev:03d}.####.exr",
        "notes": [
            "Use image type 'comp' for intermediate composites, 'FINAL' for the delivered comp.",
        ],
        "example_filled": "un-ff25_sb_0100_comp_dd_v020.1001.exr",
    },

    "photoshop_export_layers": {
        "app": "Photoshop",
        "menu": "File > Export > Layers to Files",
        "file_name_pattern": "{prefix}_{layername}",
        "recommended_prefix": "{show}_{seq}_{shot}_matt_{vendor}_v{rev:03d}",
        "notes": [
            "Rename each layer in the PSD to its matte type: 'hard', 'soft', 'garbage', 'key'.",
            "Layer names must contain only [a-zA-Z0-9-] (no spaces, no underscores).",
            "The prefix field concatenates with the layer name; underscores are added automatically.",
        ],
        "example_layer_names": [
            "hard-premult",
            "soft-premult",
            "garbage",
            "key",
            "core",
            "edge",
        ],
        "example_output_filenames": [
            "un-ff25_sb_0100_matt_dd_v001_hard-premult.png",
            "un-ff25_sb_0100_matt_dd_v001_soft-premult.png",
            "un-ff25_sb_0100_matt_dd_v001_garbage.png",
        ],
    },

    "photoshop_save_for_web": {
        "app": "Photoshop",
        "menu": "File > Export > Save for Web (Legacy)",
        "preset": "PNG-24",
        "transparency": True,
        "matte_color": "None",  # CRITICAL — preserves straight alpha
        "notes": [
            "MATTE: NONE is required for VFX mattes. Any other colour premultiplies the alpha.",
            "Use this only for review PNGs. Source mattes should be PSD or EXR.",
        ],
    },

    "blender_file_output_node": {
        "app": "Blender",
        "node": "File Output (Compositor)",
        "path_template": "//{show}_{seq}_{shot}_matt01_{vendor}_v{rev:03d}_{description}.####.exr",
        "file_format": "OpenEXR Multilayer",
        "color_depth": "32-bit Float",
        "compression": "ZIP",
        "notes": [
            "Use '//' at the start for a path relative to the .blend file.",
            "For Cryptomatte layers, also enable Cryptomatte in View Layer > Passes.",
            "EXR layer names use dot-separation ('ViewLayer.CryptoAsset00'); the filename uses underscores.",
        ],
    },

    "blender_render_output": {
        "app": "Blender",
        "tab": "Output Properties",
        "file_path_template": "//{show}_{seq}_{shot}_comp_{vendor}_v{rev:03d}.####.exr",
        "file_format": "OpenEXR",
        "color_depth": "32-bit Float",
        "color_management_view_transform": "Standard",
        "notes": [
            "Use // for relative paths (saved next to the .blend file).",
            "Use absolute paths when sharing scripts across machines.",
        ],
    },

    "resolve_render_name": {
        "app": "DaVinci Resolve",
        "page": "Deliver",
        "field": "Custom name (in render settings)",
        "token_template": "{Show}_{Seq}_{Shot}_{Type}_{Vendor}_v{Rev}.{Frame}.{Ext}",
        "available_tokens": [
            "$TimelineName", "$RenderTime", "$Resolution", "$FPS",
            "$RenderPass", "$ClipName",
        ],
        "notes": [
            "Resolve stores projects in a Project Library (database), not loose files.",
            "This naming convention applies to RENDERED image sequences, not the .drp/.dra project files.",
            "For Power Window mattes, set Type = 'matt' and Description = 'pw-<n>'.",
        ],
    },

    "after_effects_render": {
        "app": "After Effects",
        "section": "Output Module > Name Template",
        "template": "{comp}_matt01_{vendor}_v{rev:03d}_{description}.[{####}].png",
        "notes": [
            "[####] = 4-digit frame padding (use [#####] for 5-digit).",
            "For Roto Brush mattes, use PNG with Matte: None in the Output Module.",
            "For premultiplied output, leave the alpha interpretation as 'Straight'.",
        ],
    },

    "houdini_cop_output": {
        "app": "Houdini",
        "node": "COP / Render Output",
        "template": "{show}_{seq}_{shot}_comp_{vendor}_v{rev:03d}.$F4.exr",
        "notes": [
            "$F4 = 4-digit frame padding ($F5 for 5).",
            "Set the COP to write OpenEXR with ZIP compression for matte review.",
        ],
    },
}


def list_presets() -> list:
    """Return the list of preset names."""
    return list(PRESETS.keys())


def get_preset(name: str) -> dict:
    """Return a preset by name. Raises KeyError if missing."""
    return PRESETS[name]


if __name__ == "__main__":
    # CLI: list presets or print one
    import argparse
    import json

    p = argparse.ArgumentParser(description="Print VFX naming presets for DCC apps.")
    p.add_argument("preset", nargs="?", help="Preset name to print (omit to list)")
    args = p.parse_args()

    if not args.preset:
        print("Available presets:")
        for n in list_presets():
            print(f"  {n}")
    else:
        try:
            print(json.dumps(get_preset(args.preset), indent=2))
        except KeyError:
            print(f"unknown preset: {args.preset}", file=sys.stderr)
            print(f"available: {', '.join(list_presets())}", file=sys.stderr)
            sys.exit(1)
