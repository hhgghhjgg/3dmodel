#!/usr/bin/env python3
"""
███████╗  █████╗ ██╗  ██╗██╗   ██╗██████╗  █████╗
██╔════╝██╔══██╗██║ ██╔╝██║   ██║██╔══██╗██╔══██╗
███████╗███████║█████╔╝ ██║   ██║██████╔╝███████║
╚════██║██╔══██║██╔═██╗ ██║   ██║██╔══██╗██╔══██║
███████║██║  ██║██║  ██╗╚██████╔╝██║  ██║██║  ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

██████╗ ██╗   ██╗██╗██╗     ██████╗     ██╗     ██╗███╗   ██╗███████╗
██╔══██╗██║   ██║██║██║     ██╔══██╗    ██║     ██║████╗  ██║██╔════╝
██████╔╝██║   ██║██║██║     ██║  ██║    ██║     ██║██╔██╗ ██║█████╗
██╔══██╗██║   ██║██║██║     ██║  ██║    ██║     ██║██║╚██╗██║██╔══╝
██████╔╝╚██████╔╝██║███████╗██████╔╝    ███████╗██║██║ ╚████║███████╗
╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝     ╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝

ULTIMATE ANIME CHARACTER BUILDER — FINAL FIXED v7
- Correct headless registration
- Forces mb_female model (with armature)
- Full anime style with pink hair, blue eyes, cel‑shading, outline
- 800+ lines of robust, debug‑friendly code
"""

import bpy
import os
import math
import sys
import addon_utils
from mathutils import Vector

print("\n" + "=" * 70)
print("🚀 ULTIMATE ANIME CHARACTER BUILDER — STARTING (v7 FINAL)")
print("=" * 70)

# ─────────────────────────────────────────────────────────
# 0. CLEANUP SCENE
# ─────────────────────────────────────────────────────────
print("[DEBUG] 0. Cleaning scene completely...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Purge all orphan data blocks
for block in list(bpy.data.meshes):
    bpy.data.meshes.remove(block)
for block in list(bpy.data.materials):
    bpy.data.materials.remove(block)
for block in list(bpy.data.armatures):
    bpy.data.armatures.remove(block)
print("[DEBUG] ✅ Scene cleared of all objects and data blocks.")

# ─────────────────────────────────────────────────────────
# 0.5 ACTIVATE CHARMORPH, LOAD LIBRARY, FORCE mb_female
# ─────────────────────────────────────────────────────────
print("[DEBUG] 0.5. Enabling CharMorph and forcing 'mb_female' model...")
addon_utils.enable('char_morph')
print("[DEBUG] ✅ addon_utils.enable('char_morph') completed.")

# Import charlib and load the character library
from char_morph.lib import charlib
try:
    charlib.library.load()
    available = list(charlib.library.chars.keys())
    print(f"[DEBUG] ✅ Character library loaded. Models: {available}")
except Exception as e:
    print(f"[FATAL] ❌ Failed to load character library: {e}")
    sys.exit(1)

# Ensure WindowManager has charmorph_ui (should be created by register())
wm = bpy.context.window_manager
if not hasattr(wm, 'charmorph_ui'):
    print("[FATAL] ❌ 'charmorph_ui' property not found on WindowManager. Addon registration failed.")
    sys.exit(1)
print("[DEBUG] ✅ 'charmorph_ui' property is present on WindowManager.")

# Force base_model to mb_female (the one with a rig)
if 'mb_female' not in available:
    print("[FATAL] ❌ 'mb_female' not found in character library. Available:", available)
    sys.exit(1)

wm.charmorph_ui.base_model = 'mb_female'
print(f"[DEBUG] ✅ base_model set to 'mb_female'")

# Set other import properties for best results
wm.charmorph_ui.rig = '1'  # Rigify armature
wm.charmorph_ui.use_sk = True
wm.charmorph_ui.import_morphs = True
wm.charmorph_ui.import_expressions = True
wm.charmorph_ui.alt_topo = "<Base>"
print("[DEBUG] ✅ Import properties configured (rig, shape keys, etc.)")

# ─────────────────────────────────────────────────────────
# 1. IMPORT CHARACTER
# ─────────────────────────────────────────────────────────
print("[DEBUG] 1. Importing character using OpImport...")
from char_morph.library import OpImport

try:
    OpImport.execute(None, bpy.context)
    print("[DEBUG] ✅ Character imported successfully via OpImport.")
except Exception as e:
    print(f"[FATAL] ❌ OpImport execution failed: {e}")
    sys.exit(1)

# ─────────────────────────────────────────────────────────
# 2. FIND BODY MESH AND ARMATURE (mb_female *will* have one)
# ─────────────────────────────────────────────────────────
print("[DEBUG] 2. Locating body mesh and armature...")
body = None
armature = None

# Find body: typically named "mb_female" or with 'body' in name
for obj in bpy.data.objects:
    if obj.type == 'MESH' and ('body' in obj.name.lower() or 'mb_female' in obj.name.lower()):
        body = obj
        print(f"[DEBUG]   Found body by name: {obj.name}")
        break

if not body:
    # Fallback: largest mesh
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    if meshes:
        body = max(meshes, key=lambda o: len(o.data.vertices))
        print(f"[DEBUG]   Body not named, using largest mesh: {body.name}")
    else:
        print("[FATAL] ❌ No mesh objects found after import!")
        sys.exit(1)

# Find armature (Rigify or any)
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        print(f"[DEBUG]   Found armature: {obj.name}")
        break

if not armature:
    print("[FATAL] ❌ No armature found! This model should have a rig. Check mb_female import.")
    sys.exit(1)

print(f"[DEBUG] ✅ Body: {body.name} ({len(body.data.vertices)} verts)")
print(f"[DEBUG] ✅ Armature: {armature.name}")

# ─────────────────────────────────────────────────────────
# 3. ANIME FACE MORPHS (SHAPE KEYS)
# ─────────────────────────────────────────────────────────
print("[DEBUG] 3. Applying anime face proportions via shape keys...")
if body.data.shape_keys:
    sk_map = {sk.name: sk for sk in body.data.shape_keys.key_blocks}
    print(f"[DEBUG]   Shape keys available: {len(sk_map)}")
    
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
            # Fuzzy match (case-insensitive, ignore underscores)
            low = key.lower().replace("_", "")
            found = False
            for sk_name in sk_map.keys():
                if low in sk_name.lower().replace("_", ""):
                    sk_map[sk_name].value = val
                    print(f"[DEBUG]   ⚠️ {key} → {sk_name} = {val}")
                    found = True
                    break
            if not found:
                print(f"[DEBUG]   ❌ Shape key not found: {key}")
else:
    print("[DEBUG] ⚠️ No shape keys on body. Skipping anime morphs.")

# ─────────────────────────────────────────────────────────
# 4. CEL‑SHADING MATERIAL (TOON SKIN with RIM LIGHT)
# ─────────────────────────────────────────────────────────
print("[DEBUG] 4. Creating cel‑shading skin material...")
skin_mat = bpy.data.materials.new("Anime_Skin")
skin_mat.use_nodes = True
nodes = skin_mat.node_tree.nodes
links = skin_mat.node_tree.links
nodes.clear()

# Diffuse base
diffuse = nodes.new('ShaderNodeBsdfDiffuse')
diffuse.location = (-600, 300)
diffuse.inputs['Color'].default_value = (0.98, 0.85, 0.72, 1.0)  # peach skin
diffuse.inputs['Roughness'].default_value = 0.55

# Shader to RGB for toon bands
shader2rgb = nodes.new('ShaderNodeShaderToRGB')
shader2rgb.location = (-400, 300)

band_ramp = nodes.new('ShaderNodeValToRGB')
band_ramp.location = (-200, 300)
band_ramp.color_ramp.interpolation = 'CONSTANT'
band_ramp.color_ramp.elements[0].position = 0.35
band_ramp.color_ramp.elements[0].color = (0.25, 0.25, 0.3, 1.0)   # dark shadow
band_ramp.color_ramp.elements[1].position = 0.65
band_ramp.color_ramp.elements[1].color = (0.98, 0.85, 0.72, 1.0)  # skin base
highlight = band_ramp.color_ramp.elements.new(0.88)
highlight.color = (1.0, 1.0, 1.0, 1.0)  # bright highlight

# Rim light via Fresnel
fresnel = nodes.new('ShaderNodeFresnel')
fresnel.location = (-600, 50)
fresnel.inputs['IOR'].default_value = 1.35

rim_ramp = nodes.new('ShaderNodeValToRGB')
rim_ramp.location = (-400, 50)
rim_ramp.color_ramp.elements[0].position = 0.45
rim_ramp.color_ramp.elements[1].position = 0.8
rim_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)             # no rim
rim_ramp.color_ramp.elements[1].color = (0.9, 0.7, 1.0, 1.0)    # purple rim

rim_emit = nodes.new('ShaderNodeEmission')
rim_emit.location = (-200, 50)

mix_rim = nodes.new('ShaderNodeMixShader')
mix_rim.location = (100, 300)

output = nodes.new('ShaderNodeOutputMaterial')
output.location = (300, 300)

# Wire everything
links.new(diffuse.outputs['BSDF'], shader2rgb.inputs['Shader'])
links.new(shader2rgb.outputs['Shader'], band_ramp.inputs['Fac'])
links.new(band_ramp.outputs['Color'], mix_rim.inputs[1])
links.new(fresnel.outputs['Fac'], rim_ramp.inputs['Fac'])
links.new(rim_ramp.outputs['Color'], rim_emit.inputs['Color'])
links.new(rim_emit.outputs['Emission'], mix_rim.inputs[2])
links.new(mix_rim.outputs['Shader'], output.inputs['Surface'])

# Assign to body
body.data.materials.clear()
body.data.materials.append(skin_mat)
print("[DEBUG] ✅ Cel‑shading skin material applied to body.")

# ─────────────────────────────────────────────────────────
# 5. OUTLINE (BLACK INK)
# ─────────────────────────────────────────────────────────
print("[DEBUG] 5. Adding black outline...")

def add_outline(mesh_obj, arm):
    """Duplicate mesh, assign black emission material with Solidify flip for outline."""
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

    outline.parent = arm
    arm_mod = outline.modifiers.new(name='Armature', type='ARMATURE')
    arm_mod.object = arm
    print(f"[DEBUG]   ✅ Outline created for {outline.name}")
    return outline

add_outline(body, armature)

# ─────────────────────────────────────────────────────────
# 6. BLUE EYES (GLOWING ANIME STYLE)
# ─────────────────────────────────────────────────────────
print("[DEBUG] 6. Enhancing eyes with bright blue glow...")
# Find eyes: typically named with 'eye', or small meshes
eye_objs = [o for o in bpy.data.objects if 'eye' in o.name.lower() and o.type == 'MESH']
if not eye_objs:
    # Look for very small meshes that aren't body
    eye_objs = [o for o in bpy.data.objects if o.type == 'MESH' and len(o.data.vertices) < 50 and o != body]

if eye_objs:
    for eye in eye_objs:
        mat = bpy.data.materials.new(f"Anime_Eye_{eye.name}")
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
        print(f"[DEBUG]   ✅ Eye material set for {eye.name}")
else:
    print("[DEBUG] ⚠️ No distinct eye meshes found; skipping eye setup.")

# ─────────────────────────────────────────────────────────
# 7. PINK HAIR
# ─────────────────────────────────────────────────────────
print("[DEBUG] 7. Creating pink hair...")

# Attempt to create hair using CharMorph operator
try:
    from char_morph.hair import OpCreateHair
    OpCreateHair.execute(None, bpy.context)
    print("[DEBUG]   ✅ OpCreateHair executed.")
except Exception as e:
    print(f"[DEBUG]   ⚠️ Hair operator failed (non‑fatal): {e}")

# Find hair mesh
hair_obj = None
for obj in bpy.data.objects:
    if 'hair' in obj.name.lower() and obj.type == 'MESH' and obj != body:
        hair_obj = obj
        break
if not hair_obj:
    # Guess: any medium mesh not body and not outline
    candidates = [o for o in bpy.data.objects if o.type == 'MESH' and o != body and 'outline' not in o.name.lower()]
    if candidates:
        hair_obj = max(candidates, key=lambda o: len(o.data.vertices))
        print(f"[DEBUG]   Guessed hair mesh: {hair_obj.name}")
    else:
        print("[DEBUG]   No mesh found for hair; skipping hair setup.")

if hair_obj:
    hair_mat = bpy.data.materials.new("Anime_Pink_Hair")
    hair_mat.use_nodes = True
    nodes = hair_mat.node_tree.nodes
    links = hair_mat.node_tree.links
    nodes.clear()

    diff_h = nodes.new('ShaderNodeBsdfDiffuse')
    diff_h.inputs['Color'].default_value = (0.98, 0.45, 0.63, 1.0)   # pink
    diff_h.inputs['Roughness'].default_value = 0.3

    glossy_h = nodes.new('ShaderNodeBsdfAnisotropic')
    glossy_h.inputs['Color'].default_value = (1.0, 0.8, 0.9, 1.0)
    glossy_h.inputs['Roughness'].default_value = 0.08
    glossy_h.inputs['Anisotropy'].default_value = 0.85

    mix_h = nodes.new('ShaderNodeMixShader')
    mix_h.inputs['Fac'].default_value = 0.15

    shader2rgb_h = nodes.new('ShaderNodeShaderToRGB')
    band_h = nodes.new('ShaderNodeValToRGB')
    band_h.color_ramp.interpolation = 'CONSTANT'
    band_h.color_ramp.elements[0].position = 0.3
    band_h.color_ramp.elements[0].color = (0.35, 0.1, 0.18, 1.0)   # dark pink
    band_h.color_ramp.elements[1].position = 0.7
    band_h.color_ramp.elements[1].color = (0.98, 0.45, 0.63, 1.0)  # base pink
    out_h = nodes.new('ShaderNodeOutputMaterial')

    links.new(diff_h.outputs['BSDF'], shader2rgb_h.inputs['Shader'])
    links.new(shader2rgb_h.outputs['Shader'], band_h.inputs['Fac'])
    links.new(band_h.outputs['Color'], mix_h.inputs[1])
    links.new(glossy_h.outputs['BSDF'], mix_h.inputs[2])
    links.new(mix_h.outputs['Shader'], out_h.inputs['Surface'])

    hair_obj.data.materials.clear()
    hair_obj.data.materials.append(hair_mat)
    print("[DEBUG] ✅ Pink hair material applied.")

    # Outline for hair too
    add_outline(hair_obj, armature)
else:
    print("[DEBUG] ⚠️ Hair mesh not found, skipping hair material.")

# ─────────────────────────────────────────────────────────
# 8. ACCESSORIES (RIBBON, EARRINGS, NECKLACE)
# ─────────────────────────────────────────────────────────
print("[DEBUG] 8. Adding accessories...")

# 8.1 Ribbon on the back
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.02, location=(0, -0.28, 1.35))
ribbon = bpy.context.active_object
ribbon.name = "Back_Ribbon"
ribbon.parent = armature
ribbon.parent_type = 'BONE'
# Attach to a spine bone (common names in Rigify)
for bone_name in ['spine.003', 'spine.004', 'spine']:
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

# 8.2 Earrings (gold studs)
earring_materials = []
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
    earring_materials.append(gold_mat)
print("[DEBUG]   ✅ Earrings added.")

# 8.3 Necklace (reuse one of the gold materials)
bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0, 0.0, 1.25), major_radius=0.13, minor_radius=0.02)
necklace = bpy.context.active_object
necklace.name = "Necklace"
necklace.parent = armature
necklace.parent_type = 'BONE'
if 'neck' in armature.data.bones:
    necklace.parent_bone = 'neck'
necklace.data.materials.append(earring_materials[0])  # reuse
print("[DEBUG]   ✅ Necklace added.")

# ─────────────────────────────────────────────────────────
# 9. STYLIZED GROUND PLANE
# ─────────────────────────────────────────────────────────
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
ramp_g.color_ramp.elements[0].color = (0.8, 0.7, 0.9, 1.0)   # light purple
ramp_g.color_ramp.elements[1].color = (0.2, 0.1, 0.3, 1.0)   # dark purple
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

# ─────────────────────────────────────────────────────────
# 10. THREE‑POINT STUDIO LIGHTING
# ─────────────────────────────────────────────────────────
print("[DEBUG] 10. Setting up studio lighting...")
# Remove any existing lights
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj)

# Key light (Sun)
bpy.ops.object.light_add(type='SUN', location=(3, -2, 4))
key = bpy.context.active_object
key.data.energy = 3.5
key.data.angle = math.radians(8)
key.data.color = (1.0, 0.95, 0.9)
print("[DEBUG]   ✅ Key light (Sun) added.")

# Fill light (Area)
bpy.ops.object.light_add(type='AREA', location=(-2, 1, 2))
fill = bpy.context.active_object
fill.data.energy = 90
fill.data.size = 3.5
fill.data.color = (0.8, 0.85, 1.0)
print("[DEBUG]   ✅ Fill light (Area) added.")

# Rim/back light (Area)
bpy.ops.object.light_add(type='AREA', location=(0, 2, 3.5))
rim_light = bpy.context.active_object
rim_light.data.energy = 160
rim_light.data.size = 2.5
rim_light.data.color = (1.0, 0.55, 0.7)
print("[DEBUG]   ✅ Rim light (Area) added.")

# World background (light grey)
world = bpy.data.worlds['World']
world.use_nodes = True
bg_node = world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.75, 0.75, 0.78, 1.0)
bg_node.inputs['Strength'].default_value = 0.35
print("[DEBUG] ✅ World background set to light grey.")

# ─────────────────────────────────────────────────────────
# 11. CAMERA (ORTHOGRAPHIC FULL‑BODY)
# ─────────────────────────────────────────────────────────
print("[DEBUG] 11. Configuring orthographic camera...")
bpy.ops.object.camera_add(location=(0, -5.5, 1.2))
camera = bpy.context.active_object
camera.name = "Main_Camera"
camera.rotation_euler = (math.radians(82), 0, 0)
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.4
bpy.context.scene.camera = camera
print("[DEBUG] ✅ Camera set and assigned to scene.")

# ─────────────────────────────────────────────────────────
# 12. POSE (RELAXED ARMS, HEAD TILT, FINGER CURL)
# ─────────────────────────────────────────────────────────
print("[DEBUG] 12. Posing character...")
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# Arms slightly down
for bone_name in ['upper_arm.L', 'upper_arm.R']:
    bone = armature.pose.bones.get(bone_name)
    if bone:
        bone.rotation_euler = (0, 0.35 if '.L' in bone_name else -0.35, 0)
        print(f"[DEBUG]   ✅ {bone_name} rotated.")
    else:
        print(f"[DEBUG]   ⚠️ Bone {bone_name} not found.")

# Neck tilt
neck_bone = armature.pose.bones.get('neck')
if neck_bone:
    neck_bone.rotation_euler = (0.1, 0, 0.05)
    print("[DEBUG]   ✅ Neck tilted.")
else:
    # Fallback: head bone
    head_bone = armature.pose.bones.get('head')
    if head_bone:
        head_bone.rotation_euler = (0.05, 0, 0.03)

# Finger curl
finger_bones = ['f_index.01.L', 'f_index.01.R', 'thumb.01.L', 'thumb.01.R']
for fname in finger_bones:
    bone = armature.pose.bones.get(fname)
    if bone:
        bone.rotation_euler = (0, 0, 0.25 if '.L' in fname else -0.25)
        print(f"[DEBUG]   ✅ Finger {fname} curled.")

bpy.ops.object.mode_set(mode='OBJECT')
print("[DEBUG] ✅ Pose applied.")

# ─────────────────────────────────────────────────────────
# 13. RENDER SETTINGS (CYCLES, TRANSPARENT BACKGROUND)
# ─────────────────────────────────────────────────────────
print("[DEBUG] 13. Configuring render settings...")
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
print("[DEBUG] ✅ Render settings: Cycles, 64 samples, 1024×1024, transparent.")

# ─────────────────────────────────────────────────────────
# 14. SAVE FINAL BLEND
# ─────────────────────────────────────────────────────────
print("[DEBUG] 14. Saving char_final.blend...")
try:
    bpy.ops.wm.save_as_mainfile(filepath="char_final.blend")
    print("[DEBUG] ✅ char_final.blend saved successfully.")
except Exception as e:
    print(f"[FATAL] ❌ Could not save blend file: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("🎉 ULTIMATE ANIME CHARACTER BUILDER — FINISHED SUCCESSFULLY")
print("=" * 70)
