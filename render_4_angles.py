#!/usr/bin/env python3
"""
██████╗ ███████╗███╗   ██╗██████╗ ███████╗██████╗
██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗
██████╔╝█████╗  ██╔██╗ ██║██║  ██║█████╗  ██████╔╝
██╔══██╗██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
██║  ██║███████╗██║ ╚████║██████╔╝███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝

███████╗     █████╗ ███╗   ██╗ ██████╗ ██╗     ███████╗███████╗
██╔════╝    ██╔══██╗████╗  ██║██╔════╝ ██║     ██╔════╝██╔════╝
█████╗      ███████║██╔██╗ ██║██║  ███╗██║     █████╗  ███████╗
██╔══╝      ██╔══██║██║╚██╗██║██║   ██║██║     ██╔══╝  ╚════██║
██║         ██║  ██║██║ ╚████║╚██████╔╝███████╗███████╗███████║
╚═╝         ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝

Render 4 Angle Views — Front, Left, Back, Right
Compatible with GitHub Actions (CPU-only, no GPU required)
"""

import bpy
import os
import math
from mathutils import Vector

# ═══════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════

OUTPUT_DIR = os.path.join(os.getcwd(), "renders")
RESOLUTION_X = 1080
RESOLUTION_Y = 1080
SAMPLES = 32
RENDER_ENGINE = 'CYCLES'  # or 'BLENDER_EEVEE_NEXT'

ANGLES = {
    "front": 0,
    "left": math.radians(90),
    "back": math.radians(180),
    "right": math.radians(-90)
}

CAMERA_DISTANCE = 4.5
CAMERA_HEIGHT_FACTOR = 0.8


# ═══════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════

def print_banner():
    """Print startup banner."""
    print("=" * 55)
    print("  📸 RENDER 4 ANGLES — Anime Girl Character  ")
    print("=" * 55)


def setup_render_settings():
    """Configure render engine and output settings."""
    scene = bpy.context.scene

    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True

    if RENDER_ENGINE == 'CYCLES':
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = SAMPLES
        scene.cycles.use_denoising = True
        scene.cycles.device = 'CPU'
        print(f"✅ Render engine: CYCLES | Samples: {SAMPLES} | Device: CPU")
    else:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
        scene.eevee.taa_render_samples = SAMPLES
        print(f"✅ Render engine: EEVEE | Samples: {SAMPLES}")


def find_character():
    """Find the main character mesh in scene."""
    possible_names = [
        'Anime_Girl', 'AnimeGirl', 'Body',
        'MBlab', 'Character', 'Mpfb', 'Base'
    ]

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for name in possible_names:
                if name.lower() in obj.name.lower():
                    print(f"✅ Character found: {obj.name}")
                    return obj

    # Fallback: pick the mesh with the most vertices
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    if mesh_objects:
        chosen = max(mesh_objects, key=lambda o: len(o.data.vertices))
        print(f"⚠️  Character auto-detected: {chosen.name}")
        return chosen

    print("❌ No mesh found in scene!")
    return None


def get_character_center(char):
    """Calculate bounding box center of a mesh."""
    bpy.context.view_layer.update()
    vertices_world = [char.matrix_world @ v.co for v in char.data.vertices]
    center = sum(vertices_world, Vector((0, 0, 0))) / len(vertices_world)
    print(f"   Center: ({center.x:.2f}, {center.y:.2f}, {center.z:.2f})")
    return center


def find_or_create_camera():
    """Find existing camera or create a new one."""
    cam = bpy.data.objects.get('Cinematic_Camera')
    if not cam:
        cam = bpy.data.objects.get('Camera')

    if not cam:
        bpy.ops.object.camera_add(location=(0, -CAMERA_DISTANCE, 2))
        cam = bpy.context.object
        cam.name = "Cinematic_Camera"
        print("📷 New camera created: Cinematic_Camera")
    else:
        print(f"📷 Using existing camera: {cam.name}")

    bpy.context.scene.camera = cam
    return cam


def focus_camera_on_point(cam, target):
    """Point camera towards a target position."""
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def render_single_angle(cam, center, angle_rad, angle_name):
    """Render one angle and save to disk."""
    x = center.x + CAMERA_DISTANCE * math.sin(angle_rad)
    y = center.y - CAMERA_DISTANCE * math.cos(angle_rad)
    z = center.z * CAMERA_HEIGHT_FACTOR + center.z

    cam.location = (x, y, z)
    focus_camera_on_point(cam, center)

    filepath = os.path.join(OUTPUT_DIR, f"angle_{angle_name}.png")
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

    # Report file size
    if os.path.exists(filepath):
        size_kb = os.path.getsize(filepath) / 1024
        print(f"   ✅ {angle_name:6s} → {size_kb:7.1f} KB")


def render_all_angles(cam, center):
    """Loop through all 4 angles and render each."""
    print("\n📸 Rendering 4 angles...\n")

    for angle_name, angle_rad in ANGLES.items():
        render_single_angle(cam, center, angle_rad, angle_name)

    print(f"\n🎉 All renders saved to: {OUTPUT_DIR}\n")


def print_summary():
    """Print final summary of generated files."""
    print("=" * 55)
    print("  📁 OUTPUT FILES  ")
    print("=" * 55)

    for angle_name in ANGLES:
        filepath = os.path.join(OUTPUT_DIR, f"angle_{angle_name}.png")
        if os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  • angle_{angle_name}.png  ({size_kb:.1f} KB)")
        else:
            print(f"  • angle_{angle_name}.png  ❌ MISSING!")

    print("=" * 55)


# ═══════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════

def main():
    print_banner()

    # 1. Ensure output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 Output: {OUTPUT_DIR}")

    # 2. Setup
    setup_render_settings()

    # 3. Find character
    char = find_character()
    if not char:
        raise RuntimeError("Cannot render: no character found!")

    # 4. Get center
    center = get_character_center(char)

    # 5. Setup camera
    cam = find_or_create_camera()

    # 6. Render all angles
    render_all_angles(cam, center)

    # 7. Summary
    print_summary()

    print("✨ Done! 4-angle render complete.\n")


if __name__ == "__main__":
    main()
