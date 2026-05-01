#!/usr/bin/env python3
"""
██████╗ ███████╗███╗   ██╗██████╗ ███████╗██████╗
██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗
██████╔╝█████╗  ██╔██╗ ██║██║  ██║█████╗  ██████╔╝
██╔══██╗██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
██║  ██║███████╗██║ ╚████║██████╔╝███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝

██████╗     █████╗ ███╗   ██╗ ██████╗ ██╗     ███████╗███████╗
╚════██╗   ██╔══██╗████╗  ██║██╔════╝ ██║     ██╔════╝██╔════╝
 █████╔╝   ███████║██╔██╗ ██║██║  ███╗██║     █████╗  ███████╗
 ╚═══██╗   ██╔══██║██║╚██╗██║██║   ██║██║     ██╔══╝  ╚════██║
██████╔╝   ██║  ██║██║ ╚████║╚██████╔╝███████╗███████╗███████║
╚═════╝    ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝

Render 4 Angle Views — Complete, Robust, No Missing Parts
Saves PNG renders directly to "renders/" in the GitHub workspace.
"""

import bpy
import os
import math
from mathutils import Vector

# ─── Configuration ─────────────────────────────────
# Use GitHub workspace if available, otherwise current working directory
WORKSPACE = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
OUTPUT_DIR = os.path.join(WORKSPACE, "renders")
RESOLUTION = 1080
DISTANCE = 4.5
HEIGHT_FACTOR = 0.8

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"📁 Output directory: {OUTPUT_DIR}")

# ─── 1. Render Engine Setup ─────────────────────────
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'BLENDER_EEVEE_NEXT') else 'BLENDER_EEVEE'
scene.render.resolution_x = RESOLUTION
scene.render.resolution_y = RESOLUTION
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = True
print(f"✅ Render engine: {scene.render.engine}")

# ─── 2. Find Character Mesh ─────────────────────────
# Priority order: largest mesh that isn't the default Cube, or any mesh with > 50 vertices.
char = None
meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

if meshes:
    # Try to find a mesh whose name doesn't start with 'Cube' and has many vertices
    non_cubes = [m for m in meshes if not m.name.lower().startswith('cube')]
    if non_cubes:
        # Choose the one with the most vertices (likely the character)
        char = max(non_cubes, key=lambda o: len(o.data.vertices))
    else:
        # Fallback to any mesh with > 8 vertices (skip default cube 8 verts)
        plausible = [m for m in meshes if len(m.data.vertices) > 8]
        if plausible:
            char = max(plausible, key=lambda o: len(o.data.vertices))

if char:
    print(f"✅ Character: {char.name} ({len(char.data.vertices)} vertices)")
else:
    raise RuntimeError("❌ No suitable mesh found to render. Check previous steps.")

# ─── 3. Camera Setup ─────────────────────────────────
cam = bpy.data.objects.get('Camera')
if not cam:
    bpy.ops.object.camera_add(location=(0, -DISTANCE, 2))
    cam = bpy.context.object
    cam.name = "Camera"
scene.camera = cam
print(f"📷 Camera: {cam.name}")

# ─── 4. Compute Character Center (World Bounding Box) ──
bpy.context.view_layer.update()
verts_world = [char.matrix_world @ v.co for v in char.data.vertices]
center = sum(verts_world, Vector((0, 0, 0))) / len(verts_world)
print(f"📍 Center: ({center.x:.2f}, {center.y:.2f}, {center.z:.2f})")

# ─── 5. Render Four Angles ───────────────────────────
angles = {
    "front": 0,
    "left": math.radians(90),
    "back": math.radians(180),
    "right": math.radians(-90)
}

print("\n📸 Rendering 4 angles...")
for name, angle_rad in angles.items():
    # Position camera on a circle around the character
    x = center.x + DISTANCE * math.sin(angle_rad)
    y = center.y - DISTANCE * math.cos(angle_rad)
    z = center.z + HEIGHT_FACTOR * center.z  # Keep camera slightly above center
    cam.location = (x, y, z)

    # Point camera toward the center
    direction = center - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    # Set output path and render
    filepath = os.path.join(OUTPUT_DIR, f"angle_{name}.png")
    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

    # Confirm file was created
    if os.path.exists(filepath):
        size_kb = os.path.getsize(filepath) / 1024
        print(f"   ✅ {name:6s} → {size_kb:7.1f} KB")
    else:
        print(f"   ❌ {name:6s} → FILE NOT CREATED!")

print(f"\n🎉 Renders saved to: {OUTPUT_DIR}")
print("   Contents:", os.listdir(OUTPUT_DIR))
