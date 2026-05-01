#!/usr/bin/env python3
"""
رندر ۴ زاویه مختلف از کاراکتر
زاویه‌ها: جلو، چپ، عقب، راست
"""

import bpy
import os
import math

# تنظیمات خروجی
output_dir = os.path.join(os.path.dirname(bpy.data.filepath), "renders")
os.makedirs(output_dir, exist_ok=True)

bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.cycles.use_denoising = True

# پیدا کردن کاراکتر (برای فوکوس دوربین)
char = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and ('Anime_Girl' in obj.name or 'AnimeGirl' in obj.name or 'Body' in obj.name):
        char = obj
        break

# دوربین از قبل هست (Cinematic_Camera)
cam = bpy.data.objects.get('Cinematic_Camera')
if not cam:
    cam = bpy.data.objects.get('Camera')

# موقعیت مرکز کاراکتر
center = char.location if char else (0, 0, 1.2)

# ۴ زاویه
angles = {
    "front": 0,
    "left": math.radians(90),
    "back": math.radians(180),
    "right": math.radians(-90)
}

distance = 4.0
height = 1.6

for name, angle in angles.items():
    x = center.x + distance * math.sin(angle)
    y = center.y - distance * math.cos(angle)
    z = center.z + height
    
    cam.location = (x, y, z)
    
    # نگاه به مرکز
    direction = (center.x - x, center.y - y, center.z - z)
    
    filepath = os.path.join(output_dir, f"angle_{name}.png")
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    print(f"✅ Rendered: angle_{name}.png")

print("🎉 All 4 angles rendered!")
