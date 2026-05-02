import bpy
import os
import math
from mathutils import Vector

# =============================================================================
# 1. تنظیمات پایه رندر
# =============================================================================
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

# =============================================================================
# 2. ایجاد پوشه خروجی
# =============================================================================
output_dir = os.path.join(os.path.dirname(bpy.data.filepath), "renders")
if not output_dir or output_dir == "":
    output_dir = os.path.join(os.path.abspath("//"), "renders")
output_dir = os.path.abspath(output_dir)
os.makedirs(output_dir, exist_ok=True)

# =============================================================================
# 3. پیدا کردن دوربین
# =============================================================================
camera = bpy.data.objects.get('Main_Camera')
if not camera:
    camera = bpy.context.scene.camera
if not camera:
    # ایجاد دوربین جدید اگر وجود نداشت
    bpy.ops.object.camera_add(location=(0, -5, 1.2))
    camera = bpy.context.active_object
    camera.name = "Main_Camera"
    bpy.context.scene.camera = camera

# =============================================================================
# 4. پیدا کردن مش اصلی (بدون Outline)
# =============================================================================
def find_main_mesh():
    candidates = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and 'outline' not in obj.name.lower():
            candidates.append((obj, len(obj.data.vertices)))
    
    if not candidates:
        return None
    
    # بزرگترین مش غیر Outline
    return max(candidates, key=lambda x: x[1])[0]

body = find_main_mesh()

if body:
    # محاسبه مرکز
    bbox = [body.matrix_world @ Vector(c) for c in body.bound_box]
    center = Vector((
        (min(v.x for v in bbox) + max(v.x for v in bbox)) / 2,
        (min(v.y for v in bbox) + max(v.y for v in bbox)) / 2,
        (min(v.z for v in bbox) + max(v.z for v in bbox)) / 2
    ))
    # فاصله بر اساس بزرگترین بعد
    max_dim = max(
        max(v.x for v in bbox) - min(v.x for v in bbox),
        max(v.y for v in bbox) - min(v.y for v in bbox),
        max(v.z for v in bbox) - min(v.z for v in bbox)
    )
    distance = max_dim * 2.0
else:
    center = Vector((0, 0, 1))
    distance = 3.0

# =============================================================================
# 5. رندر از چهار زاویه
# =============================================================================
angles = [0, 90, 180, 270]
names = [
    "angle_front.png",
    "angle_left.png",
    "angle_back.png",
    "angle_right.png"
]

for angle, name in zip(angles, names):
    rad = math.radians(angle)
    
    # موقعیت دوربین
    cam_x = center.x + distance * math.sin(rad)
    cam_y = center.y - distance * math.cos(rad)
    cam_z = center.z
    
    camera.location = (cam_x, cam_y, cam_z)
    
    # تنظیم جهت دوربین
    direction = center - camera.location
    camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    # مسیر ذخیره
    filepath = os.path.join(output_dir, name)
    scene.render.filepath = filepath
    
    # رندر
    print(f"🎨 رندر {name} ...")
    bpy.ops.render.render(write_still=True)
    print(f"✅ ذخیره شد: {filepath}")

print("🚀 همه رندرها با موفقیت انجام شدند.")
