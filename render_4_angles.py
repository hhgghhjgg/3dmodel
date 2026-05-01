import bpy
import os
import math
from mathutils import Vector

# ====== تنظیمات رندر ======
RENDER_DIR = "//renders/"
OUTPUT_NAMES = [
    "angle_front.png",
    "angle_left.png",
    "angle_back.png",
    "angle_right.png"
]
CAMERA_ANGLES = [0, 90, 180, 270]  # چرخش حول محور Z
CAMERA_DISTANCE_FACTOR = 2.5        # فاصله دوربین نسبت به بزرگترین بعد مش
ORTHO_SCALE_FACTOR = 1.8            # بزرگنمایی در حالت orthographic
RENDER_SAMPLES = 64                 # تعداد نمونه‌های Cycles (برای کیفیت معمولی)
RESOLUTION_X = 1024
RESOLUTION_Y = 1024

# ====== انتخاب موتور و دستگاه ======
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'          # کاملاً مستقل از GPU
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.resolution_x = RESOLUTION_X
scene.render.resolution_y = RESOLUTION_Y
scene.render.film_transparent = True # پس‌زمینه شفاف
scene.cycles.samples = RENDER_SAMPLES

# غیرفعال کردن denoising برای سرعت بیشتر (اختیاری)
scene.cycles.use_denoising = False

# ====== پیدا کردن مش اصلی ======
def find_character_mesh():
    """پیدا کردن مش مناسب برای رندر: اولویت با مش‌های غیر Cube با بیشترین رأس"""
    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    if not meshes:
        raise RuntimeError("هیچ مشی در صحنه پیدا نشد!")
    
    # اولویت: بزرگترین مشی که نامش با 'Cube' شروع نشود
    non_cubes = [m for m in meshes if not m.name.startswith('Cube')]
    if non_cubes:
        return max(non_cubes, key=lambda o: len(o.data.vertices))
    
    # در غیر این صورت بزرگترین مش از نظر تعداد رأس
    print("⚠️ فقط مش‌های Cube پیدا شد. از بزرگترین مش استفاده می‌شود.")
    return max(meshes, key=lambda o: len(o.data.vertices))

target_obj = find_character_mesh()
print(f"✅ مش انتخاب‌شده: {target_obj.name} با {len(target_obj.data.vertices)} رأس")

# ====== تنظیم دوربین ======
# ایجاد دوربین اگر وجود ندارد
if 'RenderCamera' not in bpy.data.objects:
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = 'RenderCamera'
else:
    camera = bpy.data.objects['RenderCamera']

scene.camera = camera
camera.data.type = 'ORTHO'          # استفاده از حالت orthographic برای زاویه‌های استاندارد
camera.data.ortho_scale = 2.0       # مقدار اولیه (بعداً تنظیم می‌شود)

# انتخاب مش و محاسبه bounding box
bpy.context.view_layer.objects.active = target_obj
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
target_obj.select_set(True)

# محاسبه ابعاد bounding box
bbox = [target_obj.matrix_world @ Vector(corner) for corner in target_obj.bound_box]
min_x = min(v.x for v in bbox)
max_x = max(v.x for v in bbox)
min_y = min(v.y for v in bbox)
max_y = max(v.y for v in bbox)
min_z = min(v.z for v in bbox)
max_z = max(v.z for v in bbox)
width = max_x - min_x
depth = max_y - min_y
height = max_z - min_z
max_dim = max(width, depth, height)
center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2
center_z = (min_z + max_z) / 2

# تنظیم فاصله دوربین و ortho_scale
distance = max_dim * CAMERA_DISTANCE_FACTOR
camera.data.ortho_scale = max_dim * ORTHO_SCALE_FACTOR

# تنظیم مرکز دید دوربین روی مرکز مش
look_at = Vector((center_x, center_y, center_z))

# ====== تنظیم مسیر ذخیره ======
output_dir = bpy.path.abspath(RENDER_DIR)
os.makedirs(output_dir, exist_ok=True)

# ====== رندر از چهار زاویه ======
for i, angle in enumerate(CAMERA_ANGLES):
    rad = math.radians(angle)
    # محاسبه موقعیت دوربین
    cam_x = look_at.x + distance * math.sin(rad)
    cam_y = look_at.y + distance * math.cos(rad)
    cam_z = look_at.z  # ارتفاع یکسان با مرکز مش
    camera.location = (cam_x, cam_y, cam_z)
    
    # نشانه‌گیری به مرکز
    direction = look_at - camera.location
    camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    # تنظیم نام فایل خروجی
    scene.render.filepath = os.path.join(output_dir, OUTPUT_NAMES[i])
    
    # رندر
    print(f"🎨 در حال رندر {OUTPUT_NAMES[i]}...")
    bpy.ops.render.render(write_still=True)
    print(f"✅ ذخیره شد: {scene.render.filepath}")

# پاک‌سازی انتخاب
target_obj.select_set(False)
print("🚀 همه رندرها با موفقیت انجام شد!")
