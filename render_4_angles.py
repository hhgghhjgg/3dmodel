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

Render 4 Angle Views — Ultra Robust (EEVEE, no denoiser)
Saves to "renders/" inside the repository.
"""

import bpy
import os
import math
from mathutils import Vector

# ─── Settings ───
OUTPUT_DIR = os.path.join(os.getcwd(), "renders")
RESOLUTION = 1080
DISTANCE = 4.5
HEIGHT_FACTOR = 0.8

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── 1. Render Engine (EEVEE Next – always works on CPU) ───
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = RESOLUTION
scene.render.resolution_y = RESOLUTION
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = True
print("✅ EEVEE Next engine ready")

# ─── 2. Find the real character (ignore default Cube) ───
char = None
# First, try to find a mesh with >100 vertices that isn't a Cube
for obj in bpy.data.objects:
    if obj.type == 'MESH' and len(obj.data.vertices) > 100:
        if 'cube' not in obj.name.lower():
            char = obj
            print(f"✅ Character: {obj.name} ({len(obj.data.vertices)} vertices)")
            break

if not char:
    # Fallback: any mesh that isn't a Cube
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and 'cube' not in obj.name.lower():
            char = obj
            print(f"⚠️ Fallback character: {obj.name} ({len(obj.data.vertices)} vertices)")
            break

if not char:
    raise RuntimeError("❌ No character mesh found! Aborting render.")

# ─── 3. Find or create camera ───
cam = bpy.data.objects.get('Camera')
if not cam:
    bpy.ops.object.camera_add(location=(0, -DISTANCE, 2))
    cam = bpy.context.object
    cam.name = "Camera"
scene.camera = cam
print(f"📷 Camera ready: {cam.name}")

# ─── 4. Calculate character center (bounding box) ───
bpy.context.view_layer.update()
verts_world = [char.matrix_world @ v.co for v in char.data.vertices]
center = sum(verts_world, Vector((0, 0, 0))) / len(verts_world)
print(f"📍 Character center: ({center.x:.2f}, {center.y:.2f}, {center.z:.2f})")

# ─── 5. Render 4 angles ───
angles = {
    "front": 0,
    "left": math.radians(90),
    "back": math.radians(180),
    "right": math.radians(-90)
}

print("\n📸 Rendering 4 angles...")
for name, angle in angles.items():
    # Camera position
    x = center.x + DISTANCE * math.sin(angle)
    y = center.y - DISTANCE * math.cos(angle)
    z = center.z + HEIGHT_FACTOR * center.z
    cam.location = (x, y, z)

    # Look at center
    direction = center - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    # Render
    filepath = os.path.join(OUTPUT_DIR, f"angle_{name}.png")
    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

    size_kb = os.path.getsize(filepath) / 1024 if os.path.exists(filepath) else 0
    print(f"   ✅ {name:6s} → {size_kb:.1f} KB")

print(f"\n🎉 All 4 renders saved to: {OUTPUT_DIR}")
