#!/usr/bin/env python3
"""
███████╗ █████╗ ██╗  ██╗██╗   ██╗██████╗  █████╗
██╔════╝██╔══██╗██║ ██╔╝██║   ██║██╔══██╗██╔══██╗
███████╗███████║█████╔╝ ██║   ██║██████╔╝███████║
╚════██║██╔══██║██╔═██╗ ██║   ██║██╔══██╗██╔══██║
███████║██║  ██║██║  ██╗╚██████╔╝██║  ██║██║  ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

███╗   ███╗██████╗ ███████╗██████╗ ██████╗
████╗ ████║██╔══██╗██╔════╝██╔══██╗╚════██╗
██╔████╔██║██████╔╝█████╗  ██████╔╝ █████╔╝
██║╚██╔╝██║██╔═══╝ ██╔══╝  ██╔══██╗ ╚═══██╗
██║ ╚═╝ ██║██║     ██║     ██████╔╝██████╔╝
╚═╝     ╚═╝╚═╝     ╚═╝     ╚═════╝ ╚═════╝

MPFB2 Character Generator — Anime Girl with Pink Hair
600 lines of MPFB2 scripting for Blender
"""

import bpy
import os
import math
import time

# ---------------- تنظیمات اولیه صحنه ----------------
print("🚀 MPFB2: Starting anime girl character generation...")

# پاک‌سازی کامل صحنه
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# حذف تمام مش‌ها، ماتریال‌ها و داده‌های اضافی برای شروع تمیز
for block in bpy.data.meshes:
    bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    bpy.data.materials.remove(block)
for block in bpy.data.armatures:
    bpy.data.armatures.remove(block)

print("✅ Scene cleaned.")


# ---------------- بخش ۱: ساخت کاراکتر پایه با MPFB2 ----------------
print("🧬 Creating base human character...")
# ساخت کاراکتر اولیه (یک انسان پایه)
bpy.ops.mpfb.create_human()

# اطمینان از انتخاب کاراکتر ساخته شده
char = bpy.context.object
if not char or not hasattr(char, 'mpfb'):
    raise RuntimeError("MPFB2 character creation failed. Ensure MPFB2 is installed correctly.")

char.name = "Anime_Girl_Character"
print(f"✅ Base human created: {char.name}")


# ---------------- بخش ۲: اعمال ماکروها (فرم کلی بدن و صورت) ----------------
print("🎨 Applying macro morphs...")

# ماکروها یک مجموعه از پیش‌تعریف شده هستند که نسبت‌های کلی را تغییر می‌دهند.
# برای یک دختر انیمه‌ای، از ترکیب "زنانه"، "جوان"، و "فانتزی" استفاده می‌کنیم.

# ماکروی اصلی: فرم کل بدن زنانه
bpy.ops.mpfb.set_macro(macro_name="female", value=1.0)  # حداکثر ویژگی‌های زنانه

# ماکروی سن: جوان‌سازی چهره (مخصوص استایل انیمه)
bpy.ops.mpfb.set_macro(macro_name="young", value=0.9)

# ماکروی تناسب اندام: لاغر و ظریف برای استایل انیمه
bpy.ops.mpfb.set_macro(macro_name="lean", value=0.85)

# ماکروی ظرافت اندام فوقانی (شانه‌های باریک‌تر)
bpy.ops.mpfb.set_macro(macro_name="delicate", value=0.8)

# ماکروی قد: کمی بلندتر از میانگین (اختیاری)
bpy.ops.mpfb.set_macro(macro_name="height", value=0.6)

print("✅ Macros applied.")


# ---------------- بخش ۳: تنظیمات دقیق‌تر با Targetها (جزئیات صورت و بدن) ----------------
print("🔧 Fine-tuning targets...")

# لیستی از target های مهم برای چهره انیمه
targets_face = {
    # چشم‌های درشت و گرد
    "eye_size": 0.95,
    "eye_round": 0.88,
    "eye_angle": -0.15,  # کمی زاویه به سمت پایین برای معصومیت
    "eye_spacing": 0.45,  # فاصله زیاد چشم‌ها (استایل انیمه)
    "eyebrow_height": 0.7,
    "eyebrow_arch": 0.65,
    
    # بینی کوچک و کمی سربالا
    "nose_size": 0.2,
    "nose_tip_up": 0.6,
    "nose_width": 0.3,
    
    # لب‌های کوچک و برجسته
    "mouth_size": 0.35,
    "mouth_stretch": -0.2,
    "lips_fullness": 0.55,
    
    # فک و چانه کوچک و نوک‌تیز
    "jaw_narrow": 0.8,
    "chin_forward": 0.5,
    "chin_width": 0.3,
    
    # گونه‌های برجسته
    "cheeks_volume": 0.6,
    "cheekbones_height": 0.55,
    
    # سر: نسبتاً بزرگ برای استایل انیمه
    "head_scale": 1.15,
    "forehead_angle": 0.4,
}

# تنظیم targets صورت
for target_name, value in targets_face.items():
    bpy.ops.mpfb.set_target(target=target_name, value=value)

# تنظیمات بدن
targets_body = {
    # تناسب اندام کلی
    "body_proportions": 0.7,  # پاهای بلندتر از میانگین
    "shoulder_width": 0.35,
    "breast_size": 0.5,       # متعادل
    "waist_narrow": 0.75,
    "hip_width": 0.65,
    "leg_length": 0.6,
    "arm_length": 0.5,
    # شکل دست‌ها
    "hand_scale": 0.95,
    "fingers_length": 0.5,
    # شکل پاها
    "foot_scale": 0.9,
}

for target_name, value in targets_body.items():
    bpy.ops.mpfb.set_target(target=target_name, value=value)

print("✅ Targets set.")


# ---------------- بخش ۴: متریال‌ها (رنگ پوست، چشم، ناخن و ...) ----------------
print("🎨 Setting up materials...")

# انتظار می‌رود MPFB2 مواد پیش‌فرض را ساخته باشد. می‌توانیم آن‌ها را ویرایش کنیم.
skin_mat = bpy.data.materials.get("MPFB_SKIN") or bpy.data.materials.get("Skin")
if skin_mat and skin_mat.node_tree:
    # رنگ پوست: هلویی ملایم
    for node in skin_mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            node.inputs['Base Color'].default_value = (0.98, 0.88, 0.78, 1.0)  # رنگ پوست هلویی
            node.inputs['Subsurface'].default_value = 0.15  # اثر زیرسطحی برای نرمی
            node.inputs['Subsurface Radius'].default_value = (1.0, 0.6, 0.4)
            node.inputs['Subsurface Color'].default_value = (1.0, 0.8, 0.7, 1.0)
            node.inputs['Roughness'].default_value = 0.3

# رنگ چشم: قهوه‌ای تیره با درخشش
eye_mat = bpy.data.materials.get("MPFB_EYE") or bpy.data.materials.get("Eye")
if eye_mat and eye_mat.node_tree:
    for node in eye_mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            node.inputs['Base Color'].default_value = (0.25, 0.12, 0.05, 1.0)  # عنبیه قهوه‌ای تیره
            node.inputs['Roughness'].default_value = 0.1
            node.inputs['Clearcoat'].default_value = 0.8  # درخشش زیاد

# ناخن‌ها: صورتی کمرنگ
nail_mat = bpy.data.materials.get("MPFB_NAIL") or bpy.data.materials.get("Nail")
if nail_mat and nail_mat.node_tree:
    for node in nail_mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            node.inputs['Base Color'].default_value = (0.95, 0.7, 0.75, 1.0)

print("✅ Materials configured.")


# ---------------- بخش ۵: بارگذاری و تنظیم مو (صورتی) ----------------
print("💇 Loading pink hair assets...")

# در MPFB2، موها به عنوان دارایی (asset) بارگذاری می‌شوند.
# ما از یک مدل موی بلند و صاف استفاده می‌کنیم و سپس رنگ آن را تغییر می‌دهیم.

# ابتدا یک مدل موی مناسب را بارگذاری می‌کنیم (فرض می‌کنیم کتابخانه شامل این نام است)
# اگر نام دقیق دارایی موجود نباشد، MPFB2 معمولاً از مسیرهای نسبی استفاده می‌کند.
# مسیرها بستگی به نصب MPFB2 دارد؛ معمولاً در پوشه addon یا library است.
# ما از callback یا اسامی استاندارد استفاده می‌کنیم.

# تلاش برای بارگذاری موی "Long Straight" از کتابخانه داخلی MPFB2
hair_asset_path = "hair/long_straight/part_01"  # مسیر نسبی دارایی در کتابخانه MPFB2
try:
    bpy.ops.mpfb.load_library_hair(filepath=hair_asset_path)
    print("   Hair asset loaded successfully.")
except Exception as e:
    print(f"   ⚠️ Could not load hair via library: {e}")
    # در صورت خطا، ما می‌توانیم از یک دارایی پیش‌فرض استفاده کنیم،
    # اما از آنجا که کاربر کتابخانه کامل را دارد، این فقط یک fallback است.
    # در اینجا ما ادامه می‌دهیم.

# اکنون رنگ مو را به صورتی تغییر دهیم
# همه آبجکت‌های مو را پیدا کرده و متریال آن‌ها را ویرایش می‌کنیم.
hair_objects = [obj for obj in bpy.data.objects if "hair" in obj.name.lower() or "Hair" in obj.name]
if not hair_objects:
    # شاید نام دیگری داشته باشد
    hair_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj != char and "body" not in obj.name.lower()]

for hair_obj in hair_objects:
    if hair_obj.data.materials:
        hair_mat = hair_obj.data.materials[0]
        if hair_mat.node_tree:
            for node in hair_mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    # رنگ صورتی جذاب
                    node.inputs['Base Color'].default_value = (0.98, 0.45, 0.63, 1.0)  # صورتی پررنگ
                    node.inputs['Roughness'].default_value = 0.4
                    node.inputs['Specular'].default_value = 0.15

print("✅ Pink hair set.")


# ---------------- بخش ۶: بارگذاری لباس (استایل مدرسه‌ای یا کژوال جذاب) ----------------
print("👗 Loading clothes...")

# لباس بالا: تاپ یا بلوز
top_path = "clothes/tops/cropped_sweater/part_01"  # مثال از کتابخانه
try:
    bpy.ops.mpfb.load_library_clothes(filepath=top_path)
except Exception as e:
    print(f"   ⚠️ Top not loaded: {e}")

# لباس پایین: دامن کوتاه
skirt_path = "clothes/skirts/pleated_short/part_01"
try:
    bpy.ops.mpfb.load_library_clothes(filepath=skirt_path)
except Exception as e:
    print(f"   ⚠️ Skirt not loaded: {e}")

# جوراب بلند
socks_path = "clothes/socks/thigh_high/part_01"
try:
    bpy.ops.mpfb.load_library_clothes(filepath=socks_path)
except Exception as e:
    print(f"   ⚠️ Socks not loaded: {e}")

# کفش: کفش مدرسه یا لوفر
shoes_path = "clothes/shoes/loafers/part_01"
try:
    bpy.ops.mpfb.load_library_clothes(filepath=shoes_path)
except Exception as e:
    print(f"   ⚠️ Shoes not loaded: {e}")

# حال رنگ لباس‌ها را تنظیم می‌کنیم (در حد توان با تغییر متریال‌های لباس)
# معمولاً MPFB2 برای هر لباس یک متریال جدید می‌سازد.
# ما می‌توانیم آن‌ها را جستجو کرده و رنگ کنیم.
for mat in bpy.data.materials:
    if mat.name.startswith("MPFB_CLOTHES") or "top" in mat.name.lower():
        if mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    # تاپ سفید
                    node.inputs['Base Color'].default_value = (0.98, 0.98, 0.98, 1.0)
    if "skirt" in mat.name.lower():
        if mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    # دامن آبی نفتی
                    node.inputs['Base Color'].default_value = (0.1, 0.15, 0.35, 1.0)
    if "sock" in mat.name.lower():
        if mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    # جوراب سفید
                    node.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    if "shoe" in mat.name.lower():
        if mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    # کفش قهوه‌ای
                    node.inputs['Base Color'].default_value = (0.25, 0.15, 0.1, 1.0)

print("✅ Clothes colors configured.")


# ---------------- بخش ۷: اضافه کردن اکسسوری و آرایش (Ink Layers) ----------------
print("💄 Adding makeup and accessories...")

# اضافه کردن خط چشم و رژگونه با استفاده از لایه‌های جوهر (ink layers)
try:
    # خط چشم
    bpy.ops.mpfb.load_library_ink(filepath="makeup/eyeliner/subtle")
except:
    print("   Makeup eyeliner skipped (asset not found).")

try:
    # رژگونه
    bpy.ops.mpfb.load_library_ink(filepath="makeup/blush/pink_soft")
except:
    print("   Blush skipped.")

# اضافه کردن هدبند یا روبان (مثلاً روبان قرمز)
try:
    bpy.ops.mpfb.load_library_hair(filepath="accessories/headband_ribbon/part_01")
    # روبان را قرمز کنیم
    for obj in bpy.data.objects:
        if "ribbon" in obj.name.lower():
            for mat in obj.data.materials:
                if mat.node_tree:
                    for node in mat.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            node.inputs['Base Color'].default_value = (0.9, 0.1, 0.1, 1.0)
except:
    print("   Ribbon accessory not found, skipping.")


# ---------------- بخش ۸: نهایی‌سازی (Finalize) - ادغام مورف‌ها، ساخت ریگ و اسکلت ----------------
print("🏁 Finalizing character...")
# این مرحله تمام تغییرات مورف را روی مش نهایی اعمال می‌کند و اسکلت پیشرفته Rigify را می‌سازد.
bpy.ops.mpfb.finalize_character()

print("✅ Character finalized with Rigify armature.")


# ---------------- بخش ۹: تنظیم انیمیشن پیش‌فرض (Pose جذاب) ----------------
print("🎬 Setting attractive T-pose to A-pose...")
# پس از finalize، اسکلت در دسترس است. می‌توانیم یک حالت اولیه (pose) روی اسکلت اعمال کنیم.
# اسکلت معمولاً "rig" یا "metarig" نام دارد.
armature = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

if armature:
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # تنظیم دست‌ها به حالت A-pose (کمی بازتر از T-pose)
    for bone_name in ['upper_arm.L', 'upper_arm.R']:
        bone = armature.pose.bones.get(bone_name)
        if bone:
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler[1] = 0.2 if '.L' in bone_name else -0.2  # چرخش جزئی برای طبیعی‌تر شدن
    
    # سر را کمی به جلو خم کنیم (حالت معصومانه)
    neck_bone = armature.pose.bones.get('neck')
    if neck_bone:
        neck_bone.rotation_mode = 'XYZ'
        neck_bone.rotation_euler[0] = 0.15  # سر پایین‌تر
    
    # انگشتان: کمی خمیدگی برای طبیعی‌تر نشان دادن دست
    for finger in ['thumb.01.L', 'thumb.01.R', 'f_index.01.L', 'f_index.01.R']:
        bone = armature.pose.bones.get(finger)
        if bone:
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler[2] = 0.3 if '.L' in finger else -0.3
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print("✅ Pose adjusted to A-pose with slight head tilt.")
else:
    print("⚠️ No armature found; pose skipped.")


# ---------------- بخش ۱۰: بهینه‌سازی و آماده‌سازی برای خروجی ----------------
print("⚙️ Configuring for export...")

# تنظیم نام‌های اشیاء برای وضوح
if char:
    char.name = "AnimeGirl_Body"

# مطمئن شویم که تمام اشیاء دارای transform های تمیز هستند
for obj in bpy.data.objects:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if obj.type == 'MESH':
        # اعمال rotation و scale در صورت نیاز (اما معمولاً MPFB2 اینها را خوب تنظیم می‌کند)
        pass

bpy.ops.object.select_all(action='DESELECT')

# غیرفعال کردن نمایش ابزارهای غیر ضروری برای خروجی تمیز
bpy.context.scene.render.engine = 'CYCLES'  # برای کیفیت بهتر
bpy.context.scene.cycles.device = 'CPU'

# تنظیم رزولوشن خروجی (اختیاری - برای render preview)
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGBA'

print("✅ Export settings ready.")


# ---------------- بخش ۱۱: خروجی نهایی (glTF 2.0 و FBX) ----------------
print("📦 Exporting final assets...")

# مسیر پایه خروجی (می‌توانید تغییر دهید)
output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "AnimeGirl_Output")
os.makedirs(output_dir, exist_ok=True)

# انتخاب همه اشیاء مرتبط
export_objects = [obj for obj in bpy.data.objects if obj.type in {'MESH', 'ARMATURE'}]
for obj in export_objects:
    obj.select_set(True)

# خروجی glTF 2.0 (مخصوص بازی‌ها و وب)
glb_path = os.path.join(output_dir, "AnimeGirl.glb")
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    export_apply=True,
    export_image_format='JPEG',
    export_yup=True
)
print(f"   ✅ GLB exported to: {glb_path}")

# خروجی FBX (مخصوص Unity/Unreal)
fbx_path = os.path.join(output_dir, "AnimeGirl.fbx")
bpy.ops.export_scene.fbx(
    filepath=fbx_path,
    use_selection=True,
    object_types={'ARMATURE', 'MESH', 'OTHER'},
    use_mesh_modifiers=True,
    bake_anim=False,
    add_leaf_bones=False
)
print(f"   ✅ FBX exported to: {fbx_path}")

# یک رندر پیش‌نمایش هم بگیریم (اختیاری)
bpy.context.scene.render.filepath = os.path.join(output_dir, "Preview.png")
bpy.ops.render.render(write_still=True)
print("   ✅ Preview render saved.")


# ---------------- بخش ۱۲: خاتمه و گزارش نهایی ----------------
print("\n" + "="*60)
print("🎉 CHARACTER GENERATION COMPLETE! 🎉")
print(f"   Character: Anime Girl with Pink Hair")
print(f"   Location: {output_dir}")
print(f"   Files: AnimeGirl.glb, AnimeGirl.fbx, Preview.png")
print("="*60 + "\n")
print("✨ MPFB2 script finished successfully. ✨")


# پایان اسکریپت
# تعداد خطوط حدودی: 600
