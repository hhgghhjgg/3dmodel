#!/usr/bin/env python3
"""
███████╗  █████╗ ██╗  ██╗██╗   ██╗██████╗  █████╗
██╔════╝██╔══██╗██║ ██╔╝██║   ██║██╔══██╗██╔══██╗
███████╗███████║█████╔╝ ██║   ██║██████╔╝███████║
╚════██║██╔══██║██╔═██╗ ██║   ██║██╔══██╗██╔══██║
███████║██║  ██║██║  ██╗╚██████╔╝██║  ██║██║  ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

Ultimate Anime Character Builder – Genshin Quality
Pink hair, Blue eyes, Cel‑shading + Rim Light + Outline
Full debug log every ~5 lines
Headless fix v4: Import real CharMorphUIProps from addon
"""

import bpy
import os
import math
import sys
from mathutils import Vector

print("=" * 70)
print("🚀 ULTIMATE ANIME CHARACTER BUILDER — STARTING")
print("=" * 70)

# ─────────────────────────────────────────────────────
# 0. CLEANUP SCENE
# ─────────────────────────────────────────────────────
print("[DEBUG] 0. Cleaning scene...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
for a in list(bpy.data.armatures):
    bpy.data.armatures.remove(a)
print("[DEBUG] ✅ Scene completely cleaned.")

# ─────────────────────────────────────────────────────
# 0.5 HEADLESS FIX: REGISTER THE REAL CHARMORPH UI PROPS
# ─────────────────────────────────────────────────────
print("[DEBUG] 0.5. Registering CharMorphUIProps from original module...")

# Import the genuine UIProps class (contains base_model, rig, etc.)
from char_morph.common import CharMorphUIProps
from char_morph.lib.charlib import library

try:
    bpy.utils.register_class(CharMorphUIProps)
    print("[DEBUG] ✅ CharMorphUIProps registered successfully.")
except Exception as e:
    print(f"[WARN] Could not register CharMorphUIProps: {e}")
    # Continue anyway – may already be registered

# Attach to WindowManager
bpy.types.WindowManager.charmorph_ui = bpy.props.PointerProperty(type=CharMorphUIProps)

# Load the character library and pick a default model
library.load()
if library.chars:
    default_model = list(library.chars.keys())[0]
    bpy.context.window_manager.charmorph_ui.base_model = default_model
    print(f"[DEBUG] ✅ base_model set to '{default_model}'")
else:
    print("[FATAL] ❌ No characters found in library! Cannot continue.")
    sys.exit(1)

# ─────────────────────────────────────────────────────
# 1. IMPORT CHARACTER FROM CHARMORPH
# ─────────────────────────────────────────────────────
print("[DEBUG] 1. Importing character from CharMorph...")
from char_morph.library import OpImport

try:
    OpImport.execute(None, bpy.context)
    print("[DEBUG] ✅ OpImport.execute() succeeded – character imported.")
except Exception as e:
    print(f"[FATAL] ❌ Import failed: {e}")
    sys.exit(1)

# ─────────────────────────────────────────────────────
# 2. FIND BODY MESH AND ARMATURE
# ─────────────────────────────────────────────────────
print("[DEBUG] 2. Locating body mesh and armature...")
body = None
armature = None

for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'body' in obj.name.lower():
        body = obj
        print(f"[DEBUG]   Candidate body found by name: {obj.name}")
        break
if not body:
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    if meshes:
        body = max(meshes, key=lambda o: len(o.data.vertices))
        print(f"[DEBUG]   Body not named, using largest mesh: {body.name}")
    else:
        print("[FATAL] ❌ No mesh objects found after import!")
        sys.exit(1)

for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        print(f"[DEBUG]   Armature found: {obj.name}")
        break
if not armature:
    print("[FATAL] ❌ No armature found – character may have no rig!")
    sys.exit(1)

print(f"[DEBUG] ✅ Body: {body.name} ({len(body.data.vertices)} vertices)")
print(f"[DEBUG] ✅ Armature: {armature.name}")

# ─────────────────────────────────────────────────────
# 3. ANIME FACE MORPHS (SHAPE KEYS)
# ─────────────────────────────────────────────────────
print("[DEBUG] 3. Applying anime face proportions via shape keys...")
if body.data.shape_keys:
    sk_map = {sk.name: sk for sk in body.data.shape_keys.key_blocks}
    print(f"[DEBUG]   Found {len(sk_map)} shape keys.")

    anime_morphs = {
        "Eye_Size": 1.0,
        "Eye_Round": 0.9,
        "Eye_Spacing": 0.75,
        "Eye_Angle": -0.15,
        "Eyebrow_Height": 0.7,
        "Eyebrow_Arch": 0.6,
        "Nose_Size": -0.4,
        "Nose_Tip_Up": 0.6,
        "Nose_Width": -0.6,
        "Mouth_Size": -0.3,
        "Lips_Fullness": 0.45,
        "Jaw_Narrow": 0.85,
        "Chin_Forward": 0.55,
        "Chin_Width": -0.5,
        "Head_Scale": 1.18,
        "Cheeks_Volume": 0.4,
        "Neck_Thin": 0.5,
        "Waist_Narrow": 0.6,
        "Hip_Narrow": 0.45,
    }

    for key, val in anime_morphs.items():
        if key in sk_map:
            sk_map[key].value = val
            print(f"[DEBUG]   ✅ {key} = {val}")
        else:
            low_key = key.lower().replace("_", "")
            found = False
            for sk_name in sk_map.keys():
                if low_key in sk_name.lower().replace("_", ""):
                    sk_map[sk_name].value = val
                    print(f"[DEBUG]   ⚠️ {key} → {sk_name} = {val}")
                    found = True
                    break
            if not found:
                print(f"[DEBUG]   ❌ Shape key not found: {key}")
else:
    print("[DEBUG] ⚠️ No shape keys on body – skipping face morphs.")

# ─────────────────────────────────────────────────────
# 4. CEL‑SHADING MATERIAL (TOON SKIN with RIM LIGHT)
# ─────────────────────────────────────────────────────
print("[DEBUG] 4. Creating cel‑shading material for skin...")

skin_mat = bpy.data.materials.new("Anime_Skin")
skin_mat.use_nodes = True
nodes = skin_mat.node_tree.nodes
links = skin_mat.node_tree.links
nodes.clear()

diffuse = nodes.new('ShaderNodeBsdfDiffuse')
diffuse.location = (-600, 300)
diffuse.inputs['Color'].default_value = (0.98, 0.85, 0.72, 1.0)
diffuse.inputs['Roughness'].default_value = 0.55

shader2rgb = nodes.new('ShaderNodeShaderToRGB')
shader2rgb.location = (-400, 300)

band_ramp = nodes.new('ShaderNodeValToRGB')
band_ramp.location = (-200, 300)
band_ramp.color_ramp.interpolation = 'CONSTANT'
band_ramp.color_ramp.elements[0].position = 0.35
band_ramp.color_ramp.elements[0].color = (0.25, 0.25, 0.3, 1.0)
band_ramp.color_ramp.elements[1].position = 0.65
band_ramp.color_ramp.elements[1].color = (0.98, 0.85, 0.72, 1.0)
highlight = band_ramp.color_ramp.elements.new(0.88)
highlight.color = (1.0, 1.0, 1.0, 1.0)

fresnel = nodes.new('ShaderNodeFresnel')
fresnel.location = (-600, 50)
fresnel.inputs['IOR'].default_value = 1.35

rim_ramp = nodes.new('ShaderNodeValToRGB')
rim_ramp.location = (-400, 50)
rim_ramp.color_ramp.elements[0].position = 0.45
rim_ramp.color_ramp.elements[1].position = 0.8
rim_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
rim_ramp.color_ramp.elements[1].color = (0.9, 0.7, 1.0, 1.0)

rim_emit = nodes.new('ShaderNodeEmission')
rim_emit.location = (-200, 50)

mix_rim = nodes.new('ShaderNodeMixShader')
mix_rim.location = (100, 300)

output = nodes.new('ShaderNodeOutputMaterial')
output.location = (300, 300)

links.new(diffuse.outputs['BSDF'], shader2rgb.inputs['Shader'])
links.new(shader2rgb.outputs['Shader'], band_ramp.inputs['Fac'])
links.new(band_ramp.outputs['Color'], mix_rim.inputs[1])
links.new(fresnel.outputs['Fac'], rim_ramp.inputs['Fac'])
links.new(rim_ramp.outputs['Color'], rim_emit.inputs['Color'])
links.new(rim_emit.outputs['Emission'], mix_rim.inputs[2])
links.new(mix_rim.outputs['Shader'], output.inputs['Surface'])

if body:
    body.data.materials.clear()
    body.data.materials.append(skin_mat)
    print("[DEBUG] ✅ Cel‑shading skin material applied to body.")
else:
    print("[FATAL] ❌ Body object missing, cannot assign material.")

# ─────────────────────────────────────────────────────
# 5. OUTLINE (BLACK INK)
# ─────────────────────────────────────────────────────
print("[DEBUG] 5. Adding black outline (solidify + backface culling)...")

def add_outline(mesh_obj, arm_obj):
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.duplicate()
    outline = bpy.context.active_object
    outline.name = mesh_obj.name + "_Outline"
    outline.data.materials.clear()

    black_mat = bpy.data.materials.new("Outline_Black")
    black_mat.use_nodes = True
    emit_node = black_mat.node_tree.nodes.new('ShaderNodeEmission')
    emit_node.inputs['Color'].default_value = (0.01, 0.01, 0.01, 1.0)
    emit_node.inputs['Strength'].default_value = 1.0
    out_node = black_mat.node_tree.nodes['Material Output']
    black_mat.node_tree.links.new(emit_node.outputs['Emission'], out_node.inputs['Surface'])
    black_mat.use_backface_culling = True
    outline.data.materials.append(black_mat)

    solidify = outline.modifiers.new(name="Outline", type='SOLIDIFY')
    solidify.thickness = 0.018
    solidify.offset = -1
    solidify.use_flip_normals = True
    solidify.use_quality_normals = True

    outline.parent = arm_obj
    arm_mod = outline.modifiers.new(name='Armature', type='ARMATURE')
    arm_mod.object = arm_obj

    print(f"[DEBUG]   ✅ Outline created: {outline.name}")
    return outline

add_outline(body, armature)

# ─────────────────────────────────────────────────────
# 6. BLUE EYES (GLOWING ANIME STYLE)
# ─────────────────────────────────────────────────────
print("[DEBUG] 6. Enhancing eyes with bright blue glow...")
eye_objs = [o for o in bpy.data.objects if 'eye' in o.name.lower() and o.type == 'MESH']
if not eye_objs:
    eye_objs = [o for o in bpy.data.objects if o.type == 'MESH' and len(o.data.vertices) < 50]

if eye_objs:
    for eye in eye_objs:
        mat_name = f"Anime_Eye_{eye.name}"
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        diff = nodes.new('ShaderNodeBsdfDiffuse')
        diff.inputs['Color'].default_value = (0.2, 0.65, 1.0, 1.0)

        emit = nodes.new('ShaderNodeEmission')
        emit.inputs['Color'].default_value = (0.2, 0.65, 1.0, 1.0)
        emit.inputs['Strength'].default_value = 0.35

        mix = nodes.new('ShaderNodeMixShader')
        mix.inputs['Fac'].default_value = 0.65

        out = nodes.new('ShaderNodeOutputMaterial')

        links.new(diff.outputs['BSDF'], mix.inputs[1])
        links.new(emit.outputs['Emission'], mix.inputs[2])
        links.new(mix.outputs['Shader'], out.inputs['Surface'])

        eye.data.materials.clear()
        eye.data.materials.append(mat)
        print(f"[DEBUG]   ✅ Eye material set: {eye.name}")
else:
    print("[WARN] ⚠️ No eye meshes found – skipping eye setup.")

# ─────────────────────────────────────────────────────
# 7. PINK HAIR (ANISOTROPIC STRANDS)
# ─────────────────────────────────────────────────────
print("[DEBUG] 7. Creating pink hair...")

try:
    from char_morph.hair import OpCreateHair
    OpCreateHair.execute(None, bpy.context)
    print("[DEBUG]   ✅ OpCreateHair executed.")
except Exception as e:
    print(f"[WARN] ⚠️ Hair creation operator failed (non‑fatal): {e}")

hair_obj = None
for obj in bpy.data.objects:
    if 'hair' in obj.name.lower() and obj.type == 'MESH' and obj != body:
        hair_obj = obj
        break
if not hair_obj:
    candidates = [o for o in bpy.data.objects if o.type == 'MESH' and o != body and 'outline' not in o.name.lower()]
    if candidates:
        hair_obj = max(candidates, key=lambda o: len(o.data.vertices))
        print(f"[WARN] Hair mesh guessed: {hair_obj.name}")
    else:
        print("[ERROR] ❌ No separate hair mesh found – pink hair skipped.")

if hair_obj:
    hair_mat = bpy.data.materials.new("Anime_Pink_Hair")
    hair_mat.use_nodes = True
    nodes = hair_mat.node_tree.nodes
    links = hair_mat.node_tree.links
    nodes.clear()

    diff_h = nodes.new('ShaderNodeBsdfDiffuse')
    diff_h.inputs['Color'].default_value = (0.98, 0.45, 0.63, 1.0)
    diff_h.inputs['Roughness'].default_value = 0.3

    glossy_h = nodes.new('ShaderNodeBsdfAnisotropic')
    glossy_h.inputs['Color'].default_value = (1.0, 0.8, 0.9, 1.0)
    glossy_h.inputs['Roughness'].default_value = 0.08
    glossy_h.inputs['Anisotropy'].default_value = 0.85

    mix_h = nodes.new('ShaderNodeMixShader')
    mix_h.inputs['Fac'].default_value = 0.15

    shader2rgb_h = nodes.new('ShaderNodeShaderToRGB')
    shader2rgb_h.location = (-300, 200)

    band_h = nodes.new('ShaderNodeValToRGB')
    band_h.color_ramp.interpolation = 'CONSTANT'
    band_h.color_ramp.elements[0].position = 0.3
    band_h.color_ramp.elements[0].color = (0.35, 0.1, 0.18, 1.0)
    band_h.color_ramp.elements[1].position = 0.7
    band_h.color_ramp.elements[1].color = (0.98, 0.45, 0.63, 1.0)

    out_h = nodes.new('ShaderNodeOutputMaterial')

    links.new(diff_h.outputs['BSDF'], shader2rgb_h.inputs['Shader'])
    links.new(shader2rgb_h.outputs['Shader'], band_h.inputs['Fac'])
    links.new(band_h.outputs['Color'], mix_h.inputs[1])
    links.new(glossy_h.outputs['BSDF'], mix_h.inputs[2])
    links.new(mix_h.outputs['Shader'], out_h.inputs['Surface'])

    hair_obj.data.materials.clear()
    hair_obj.data.materials.append(hair_mat)
    print("[DEBUG] ✅ Pink hair material applied.")

    add_outline(hair_obj, armature)
else:
    print("[WARN] ⚠️ Hair mesh not found; skipping hair setup.")

# ─────────────────────────────────────────────────────
# 8. ACCESSORIES: RIBBON & EARRINGS
# ─────────────────────────────────────────────────────
print("[DEBUG] 8. Adding accessories (ribbon, earrings)...")

bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.02, location=(0, -0.28, 1.35))
ribbon = bpy.context.active_object
ribbon.name = "Back_Ribbon"
ribbon.parent = armature
ribbon.parent_type = 'BONE'
spine_bones = ['spine.003', 'spine.004', 'spine']
for bone_name in spine_bones:
    if bone_name in armature.data.bones:
        ribbon.parent_bone = bone_name
        break
rib_mat = bpy.data.materials.new("Ribbon_Red")
rib_mat.use_nodes = True
for node in rib_mat.node_tree.nodes:
    if node.type == 'BSDF_PRINCIPLED':
        node.inputs['Base Color'].default_value = (0.9, 0.1, 0.1, 1.0)
        node.inputs['Roughness'].default_value = 0.4
ribbon.data.materials.append(rib_mat)
print("[DEBUG]   ✅ Red ribbon added.")

for side, x_offset in [('L', -0.14), ('R', 0.14)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, location=(x_offset, 0.0, 1.62))
    earring = bpy.context.active_object
    earring.name = f"Earring_{side}"
    earring.parent = armature
    earring.parent_type = 'BONE'
    if 'head' in armature.data.bones:
        earring.parent_bone = 'head'
    gold_mat = bpy.data.materials.new(f"Gold_{side}")
    gold_mat.use_nodes = True
    for node in gold_mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            node.inputs['Base Color'].default_value = (0.95, 0.7, 0.2, 1.0)
            node.inputs['Metallic'].default_value = 1.0
            node.inputs['Roughness'].default_value = 0.2
    earring.data.materials.append(gold_mat)
print("[DEBUG]   ✅ Earrings added.")

bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0, 0.0, 1.25), rotation=(0,0,0), major_radius=0.13, minor_radius=0.02)
necklace = bpy.context.active_object
necklace.name = "Necklace"
necklace.parent = armature
necklace.parent_type = 'BONE'
if 'neck' in armature.data.bones:
    necklace.parent_bone = 'neck'
necklace.data.materials.append(gold_mat)
print("[DEBUG]   ✅ Necklace added.")

# ─────────────────────────────────────────────────────
# 9. GROUND PLANE (Stylized checkered)
# ─────────────────────────────────────────────────────
print("[DEBUG] 9. Creating stylized ground...")
bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground_mat = bpy.data.materials.new("Ground_Stylized")
ground_mat.use_nodes = True
gnodes = ground_mat.node_tree.nodes
glinks = ground_mat.node_tree.links
gnodes.clear()
tex_coord_g = gnodes.new('ShaderNodeTexCoord')
tex_coord_g.location = (-600, 300)
checker = gnodes.new('ShaderNodeTexChecker')
checker.location = (-400, 300)
checker.inputs['Scale'].default_value = 12.0
ramp_g = gnodes.new('ShaderNodeValToRGB')
ramp_g.location = (-200, 300)
ramp_g.color_ramp.elements[0].color = (0.8, 0.7, 0.9, 1.0)
ramp_g.color_ramp.elements[1].color = (0.2, 0.1, 0.3, 1.0)
emit_g = gnodes.new('ShaderNodeEmission')
emit_g.location = (0, 300)
out_g = gnodes.new('ShaderNodeOutputMaterial')
out_g.location = (200, 300)
glinks.new(tex_coord_g.outputs['Object'], checker.inputs['Vector'])
glinks.new(checker.outputs['Color'], ramp_g.inputs['Fac'])
glinks.new(ramp_g.outputs['Color'], emit_g.inputs['Color'])
glinks.new(emit_g.outputs['Emission'], out_g.inputs['Surface'])
ground.data.materials.append(ground_mat)
print("[DEBUG] ✅ Ground plane added with checkered material.")

# ─────────────────────────────────────────────────────
# 10. LIGHTING (THREE‑POINT STUDIO)
# ─────────────────────────────────────────────────────
print("[DEBUG] 10. Setting up studio lighting...")
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj)

bpy.ops.object.light_add(type='SUN', location=(3, -2, 4))
key = bpy.context.active_object
key.data.energy = 3.5
key.data.angle = math.radians(8)
key.data.color = (1.0, 0.95, 0.9)
print("[DEBUG]   ✅ Key light (Sun) created.")

bpy.ops.object.light_add(type='AREA', location=(-2, 1, 2))
fill = bpy.context.active_object
fill.data.energy = 90
fill.data.size = 3.5
fill.data.color = (0.8, 0.85, 1.0)
print("[DEBUG]   ✅ Fill light (Area) created.")

bpy.ops.object.light_add(type='AREA', location=(0, 2, 3.5))
rim = bpy.context.active_object
rim.data.energy = 160
rim.data.size = 2.5
rim.data.color = (1.0, 0.55, 0.7)
print("[DEBUG]   ✅ Rim light (Area) created.")

world = bpy.data.worlds['World']
world.use_nodes = True
bg_node = world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.75, 0.75, 0.78, 1.0)
bg_node.inputs['Strength'].default_value = 0.35
print("[DEBUG] ✅ World background set to light grey.")

# ─────────────────────────────────────────────────────
# 11. CAMERA (ORTHOGRAPHIC FULL‑BODY)
# ─────────────────────────────────────────────────────
print("[DEBUG] 11. Configuring camera...")
bpy.ops.object.camera_add(location=(0, -5.5, 1.2))
camera = bpy.context.active_object
camera.name = "Main_Camera"
camera.rotation_euler = (math.radians(82), 0, 0)
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.4
bpy.context.scene.camera = camera
print("[DEBUG] ✅ Camera set and assigned to scene.")

# ─────────────────────────────────────────────────────
# 12. APPLY POSE (RELAXED ARMS)
# ─────────────────────────────────────────────────────
print("[DEBUG] 12. Posing character (relaxed arms, slight head tilt)...")
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

for bone_name in ['upper_arm.L', 'upper_arm.R']:
    bone = armature.pose.bones.get(bone_name)
    if bone:
        bone.rotation_euler = (0, 0.35 if '.L' in bone_name else -0.35, 0)
        print(f"[DEBUG]   ✅ {bone_name} rotated.")
    else:
        print(f"[WARN]   ⚠️ Bone {bone_name} not found.")

neck_bone = armature.pose.bones.get('neck')
if neck_bone:
    neck_bone.rotation_euler = (0.1, 0, 0.05)
    print("[DEBUG]   ✅ Neck tilted for cuteness.")
else:
    head_bone = armature.pose.bones.get('head')
    if head_bone:
        head_bone.rotation_euler = (0.05, 0, 0.03)

finger_bones = ['f_index.01.L', 'f_index.01.R', 'thumb.01.L', 'thumb.01.R']
for fname in finger_bones:
    bone = armature.pose.bones.get(fname)
    if bone:
        bone.rotation_euler = (0, 0, 0.25 if '.L' in fname else -0.25)
        print(f"[DEBUG]   ✅ Finger {fname} curled.")

bpy.ops.object.mode_set(mode='OBJECT')
print("[DEBUG] ✅ Pose applied.")

# ─────────────────────────────────────────────────────
# 13. RENDER SETTINGS
# ─────────────────────────────────────────────────────
print("[DEBUG] 13. Configuring render engine...")
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
print("[DEBUG] ✅ Render settings: Cycles 64 samples, 1024x1024, transparent.")

# ─────────────────────────────────────────────────────
# 14. SAVE FINAL BLEND
# ─────────────────────────────────────────────────────
print("[DEBUG] 14. Saving char_final.blend...")
try:
    bpy.ops.wm.save_as_mainfile(filepath="char_final.blend")
    print("[DEBUG] ✅ char_final.blend saved successfully.")
except Exception as e:
    print(f"[FATAL] ❌ Could not save blend: {e}")
    sys.exit(1)

print("=" * 70)
print("🎉 ULTIMATE ANIME CHARACTER BUILDER — FINISHED")
print("=" * 70)
