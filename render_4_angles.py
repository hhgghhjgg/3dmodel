import bpy
import os
import math
from mathutils import Vector

# =============================================================================
# 1. آشکارسازی تمام مش‌ها و چاپ اطلاعات صحنه
# =============================================================================
print("\n" + "=" * 60)
print("🔍 بررسی وضعیت صحنه:")
print("=" * 60)

for obj in bpy.data.objects:
    print(f"شیء: '{obj.name}' | نوع: {obj.type} | مخفی رندر: {obj.hide_render} | مخفی ویو: {obj.hide_viewport}")
    if obj.type == 'MESH':
        print(f"  └─ رأس‌ها: {len(obj.data.vertices)} | تعداد متریال: {len(obj.data.materials)}")
        for mat in obj.data.materials:
            if mat:
                print(f"     └─ متریال: {mat.name}")

# از حالت مخفی خارج کردن همه مش‌ها
print("\n🔓 خارج کردن تمام مش‌ها از حالت مخفی...")
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.hide_render = False
        obj.hide_viewport = False
        obj.hide_set(False)          # برای Blender 2.8+

# =============================================================================
# 2. تنظیمات اصلی رندر
# =============================================================================
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
scene.render.film_transparent = False   # پس‌زمینه شفاف نباشد تا جسم بدون نور دیده شود
scene.cycles.samples = 64               # می‌توانید افزایش دهید (128-256)
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

# =============================================================================
# 3. تنظیم نور و پس‌زمینه (برای جلوگیری از سیاهی مطلق)
# =============================================================================
# اضافه کردن World روشن (آسمان خاکستری روشن)
world = bpy.data.worlds.new("RenderWorld") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.8, 0.8, 0.8, 1.0)  # خاکستری روشن
    bg_node.inputs['Strength'].default_value = 1.0

# اگر نور کافی در صحنه نیست، یک نور Sun اضافه کن
light_found = False
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        light_found = True
        break

if not light_found:
    print("💡 نوری یافت نشد، یک نور خورشید اضافه می‌شود.")
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), math.radians(30), math.radians(45))

# =============================================================================
# 4. پیدا کردن مش اصلی کاراکتر
# =============================================================================
def find_character_mesh():
    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    # اولویت 1: کلیدواژه‌های مرتبط با کاراکتر
    keywords = ['girl', 'character', 'body', 'female', 'anime', 'woman', 'human', 'base', 'woman']
    for kw in keywords:
        for m in meshes:
            if kw in m.name.lower() and len(m.data.vertices) > 100:
                print(f"✅ کاراکتر پیدا شد: '{m.name}' (کلیدواژه: {kw})")
                return m

    # اولویت 2: بزرگترین مش که Cube نباشد
    non_cubes = [m for m in meshes if 'cube' not in m.name.lower()]
    if non_cubes:
        best = max(non_cubes, key=lambda m: len(m.data.vertices))
        if len(best.data.vertices) > 8:
            print(f"⚠️ مش غیر Cube انتخاب شد: '{best.name}' با {len(best.data.vertices)} رأس")
            return best

    # اولویت 3: فقط Cube وجود دارد
    print("❌ هیچ کاراکتری پیدا نشد، تنها مکعب‌های پیش‌فرض باقی مانده‌اند.")
    return None

target = find_character_mesh()

if target is None:
    print("🚨 خطای مرگبار: هیچ مش کاراکتری برای رندر وجود ندارد!")
    print("فایل char_final.blend احتمالاً خالی یا خراب است. مراحل قبلی را بررسی کنید.")
    import sys
    sys.exit(1)

# فعال‌سازی مش انتخاب‌شده
bpy.context.view_layer.objects.active = target
target.select_set(True)

# =============================================================================
# 5. آماده‌سازی دوربین (Orthographic)
# =============================================================================
if 'RenderCamera' not in bpy.data.objects:
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = 'RenderCamera'
else:
    cam = bpy.data.objects['RenderCamera']

scene.camera = cam
cam.data.type = 'ORTHO'

# محاسبه bounding box مش برای تنظیم مقیاس دوربین
# ابتدا origin را به مرکز هندسی ببریم (اختیاری اما بهتر نتیجه می‌دهد)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

bbox_corners = [target.matrix_world @ Vector(corner) for corner in target.bound_box]
min_x = min(v.x for v in bbox_corners)
max_x = max(v.x for v in bbox_corners)
min_y = min(v.y for v in bbox_corners)
max_y = max(v.y for v in bbox_corners)
min_z = min(v.z for v in bbox_corners)
max_z = max(v.z for v in bbox_corners)

width   = max_x - min_x
depth   = max_y - min_y
height  = max_z - min_z
max_dim = max(width, depth, height)

center_x = (min_x + max_x) / 2.0
center_y = (min_y + max_y) / 2.0
center_z = (min_z + max_z) / 2.0

distance = max_dim * 2.5
cam.data.ortho_scale = max_dim * 1.6   # حاشیه امن دور شخصیت

look_at = Vector((center_x, center_y, center_z))

# =============================================================================
# 6. رندر از چهار زاویه
# =============================================================================
output_dir = os.path.abspath(bpy.path.abspath("//renders/"))
os.makedirs(output_dir, exist_ok=True)

angles = [0, 90, 180, 270]
names  = ["angle_front.png", "angle_left.png", "angle_back.png", "angle_right.png"]

for i, angle in enumerate(angles):
    rad = math.radians(angle)
    cam_x = look_at.x + distance * math.sin(rad)
    cam_y = look_at.y + distance * math.cos(rad)
    cam_z = look_at.z
    cam.location = (cam_x, cam_y, cam_z)

    # نشانه‌روی دوربین به مرکز کاراکتر
    dir_vec = look_at - cam.location
    cam.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()

    filepath = os.path.join(output_dir, names[i])
    scene.render.filepath = filepath

    print(f"🎨 رندر {names[i]} ...")
    bpy.ops.render.render(write_still=True)
    print(f"✅ ذخیره شد: {filepath}")

target.select_set(False)
print("\n🚀 تمام رندرها با موفقیت انجام شد!")
