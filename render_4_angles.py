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
Robust version: handles missing denoiser, missing character.
"""

import bpy
import os
import math
from mathutils import Vector

# ═══════════════════════════════════════════
# PARAMETERS (can be changed)
# ═══════════════════════════════════════════
OUTPUT_DIR = os.path.join(os.getcwd(), "renders")
RESOLUTION_X = 1080
RESOLUTION_Y = 1080
SAMPLES = 32
CAMERA_DISTANCE = 4.5
CAMERA_HEIGHT_FACTOR = 0.8

# ═══════════════════════════════════════════
# 1. SETUP RENDER ENGINE (FALLBACK ON DENOISER ERROR)
# ═══════════════════════════════════════════
def setup_render():
    scene = bpy.context.scene
    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True

    # ابتدا Cycles رو امتحان کن
    try:
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = SAMPLES
        scene.cycles.device = 'CPU'
        # اگر denoiser در دسترس نیست، بدون denoiser ادامه بده
        if hasattr(scene.cycles, 'use_denoising'):
            scene.cycles.use_denoising = False  # قطع کن تا خطا نگیره
        print("✅ Render engine: CYCLES (CPU, no denoiser)")
    except Exception as e:
        print(f"⚠️ Cycles failed ({e}), switch to Eevee")
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
        scene.eevee.taa_render_samples = 16
        print("✅ Render engine: EEVEE (fallback)")

# ═══════════════════════════════════════════
# 2. FIND CHARACTER MESH (PRIORITIZE NAME)
# ═══════════════════════════════════════════
def find_character():
    # اسامی احتمالی را به ترتیب اولویت چک کن
    target_names = [
        'Anime_Girl_Character',   # اسمی که در mpfb2_base.py ست کردیم
        'AnimeGirl_Body',
        'AnimeGirl',
        'Body',
        'Mpfb',
        'Base'
    ]
    for name in target_names:
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and name.lower() in obj.name.lower():
                # مطمئن شو فقط یه مکعب پیش‌فرض نیست (تعداد رأس > 8)
                if len(obj.data.vertices) > 100:
                    print(f"✅ Character found: {obj.name} ({len(obj.data.vertices)} vertices)")
                    return obj

    # اگر هیچ کدام پیدا نشد، بزرگترین مش غیردوربین و غیر نوری را بردار
    mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH' and len(o.data.vertices) > 50]
    if mesh_objs:
        best = max(mesh_objs, key=lambda o: len(o.data.vertices))
        print(f"⚠️  Fallback character: {best.name} ({len(best.data.vertices)} vertices)")
        return best

    print("❌ No suitable character mesh found!")
    return None

# ═══════════════════════════════════════════
# 3. CAMERA SETUP / FIND
# ═══════════════════════════════════════════
def find_or_create_camera():
    cam = bpy.data.objects.get('Cinematic_Camera')
    if not cam:
        cam = bpy.data.objects.get('Camera')
    if not cam:
        bpy.ops.object.camera_add(location=(0, -CAMERA_DISTANCE, 2))
        cam = bpy.context.object
        cam.name = "Cinematic_Camera"
        print("📷 New camera created")
    else:
        print(f"📷 Using camera: {cam.name}")
    bpy.context.scene.camera = cam
    return cam

# ═══════════════════════════════════════════
# 4. CALCULATE BOUNDING BOX CENTER
# ═══════════════════════════════════════════
def get_character_center(char_obj):
    bpy.context.view_layer.update()
    verts = [char_obj.matrix_world @ v.co for v in char_obj.data.vertices]
    center = sum(verts, Vector((0,0,0))) / len(verts)
    print(f"   Center: ({center.x:.3f}, {center.y:.3f}, {center.z:.3f})")
    return center

# ═══════════════════════════════════════════
# 5. RENDER ONE ANGLE
# ═══════════════════════════════════════════
def render_angle(cam, target, angle_rad, filepath):
    x = target.x + CAMERA_DISTANCE * math.sin(angle_rad)
    y = target.y - CAMERA_DISTANCE * math.cos(angle_rad)
    z = target.z * CAMERA_HEIGHT_FACTOR + target.z
    cam.location = (x, y, z)
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    size_kb = os.path.getsize(filepath) / 1024 if os.path.exists(filepath) else 0
    print(f"   ✅ {os.path.basename(filepath)} ({size_kb:.1f} KB)")

# ═══════════════════════════════════════════
# 6. MAIN
# ═══════════════════════════════════════════
def main():
    print("=" * 55)
    print("  📸 RENDER 4 ANGLES — Robust Edition  ")
    print("=" * 55)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 Output: {OUTPUT_DIR}")

    setup_render()

    char = find_character()
    if not char:
        raise RuntimeError("No character to render! Check previous steps.")
    center = get_character_center(char)

    cam = find_or_create_camera()

    angles = {
        "front": 0,
        "left": math.radians(90),
        "back": math.radians(180),
        "right": math.radians(-90)
    }

    print("\n📸 Rendering...")
    for name, angle in angles.items():
        filepath = os.path.join(OUTPUT_DIR, f"angle_{name}.png")
        render_angle(cam, center, angle, filepath)

    print("\n🎉 All 4 renders complete!")
    for name in angles:
        f = os.path.join(OUTPUT_DIR, f"angle_{name}.png")
        if os.path.exists(f):
            print(f"   • angle_{name}.png ({os.path.getsize(f)/1024:.1f} KB)")
    print("=" * 55)

if __name__ == "__main__":
    main()
