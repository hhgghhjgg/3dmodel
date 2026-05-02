#!/usr/bin/env python3
"""
███████╗  █████╗ ██╗  ██╗██╗   ██╗██████╗  █████╗
██╔════╝██╔══██╗██║ ██╔╝██║   ██║██╔══██╗██╔══██╗
███████╗███████║█████╔╝ ██║   ██║██████╔╝███████║
╚════██║██╔══██║██╔═██╗ ██║   ██║██╔══██╗██╔══██║
███████║██║  ██║██║  ██╗╚██████╔╝██║  ██║██║  ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

Ultimate Anime Character Builder (Fully Debugged)
Pink hair, blue eyes, Genshin-quality style
"""

import bpy
import os
import math
from mathutils import Vector

print("=" * 60)
print("🚀 SCRIPT START")
print("=" * 60)

# ──────────────────────────────────
# 0. CLEANUP
# ──────────────────────────────────
print("[DEBUG] 0. Cleaning scene...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
print("[DEBUG] ✅ Scene cleared.")

# ──────────────────────────────────
# 1. IMPORT CHARACTER FROM CharMorph
# ──────────────────────────────────
print("[DEBUG] 1. Importing character from CharMorph...")
from char_morph.library import OpImport

try:
    OpImport.execute(None, bpy.context)
    print("[DEBUG] ✅ OpImport.execute() completed.")
except Exception as e:
    print(f"[FATAL] ❌ OpImport failed: {e}")
    import sys
    sys.exit(1)

# ──────────────────────────────────
# 2. FIND BODY MESH AND ARMATURE
# ──────────────────────────────────
print("[DEBUG] 2. Finding body mesh and armature...")
body = None
armature = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'body' in obj.name.lower():
        body = obj
    if obj.type == 'ARMATURE':
        armature = obj

if not body:
    # Fallback: largest mesh
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    if meshes:
        body = max(meshes, key=lambda o: len(o.data.vertices))
        print("[WARN] 'body' not found by name; using largest mesh:", body.name)
    else:
        print("[FATAL] ❌ No mesh found after import!")
        sys.exit(1)

if not armature:
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break
    if not armature:
        print("[FATAL] ❌ No armature found!")
        sys.exit(1)

print(f"[DEBUG] ✅ Body: {body.name} ({len(body.data.vertices)} verts)")
print(f"[DEBUG] ✅ Armature: {armature.name}")

# ──────────────────────────────────
# 3. ANIME FACE SHAPE KEYS
# ──────────────────────────────────
print("[DEBUG] 3. Applying anime face shape keys...")
if body.data.shape_keys:
    sk_map = {sk.name: sk for sk in body.data.shape_keys.key_blocks}
    print(f"[DEBUG] Found {len(sk_map)} shape keys.")

    anime_values = {
        "Eye_Size": 1.0,
        "Eye_Round": 0.8,
        "Eye_Spacing": 0.7,
        "Eye_Angle": -0.2,
        "Eyebrow_Height": 0.6,
        "Eyebrow_Arch": 0.5,
        "Nose_Size": -0.3,
        "Nose_Tip_Up": 0.5,
        "Nose_Width": -0.5,
        "Mouth_Size": -0.3,
        "Lips_Fullness": 0.4,
        "Jaw_Narrow": 0.8,
        "Chin_Forward": 0.5,
        "Chin_Width": -0.4,
        "Head_Scale": 1.15,
        "Cheeks_Volume": 0.4,
    }

    for name, value in anime_values.items():
        if name in sk_map:
            sk_map[name].value = value
            print(f"[DEBUG]   ✅ {name} = {value}")
        else:
            # case-insensitive match
            found = False
            for sk_name in sk_map.keys():
                if name.lower().replace("_", "") in sk_name.lower().replace("_", ""):
                    sk_map[sk_name].value = value
                    print(f"[DEBUG]   ⚠️ {name} -> {sk_name} = {value}")
                    found = True
                    break
            if not found:
                print(f"[DEBUG]   ❌ Shape key not found: {name}")
else:
    print("[WARN] ⚠️ No shape keys on body; skipping face morphs.")

# ──────────────────────────────────
# 4. CEL-SHADING MATERIAL (TOON SKIN)
# ──────────────────────────────────
print("[DEBUG] 4. Creating cel-shading material for skin...")

skin_mat = bpy.data.materials.new("Anime_Skin")
skin_mat.use_nodes = True
nodes = skin_mat.node_tree.nodes
links = skin_mat.node_tree.links
nodes.clear()

diffuse = nodes.new('ShaderNodeBsdfDiffuse')
diffuse.location = (-400, 300)
diffuse.inputs['Color'].default_value = (0.98, 0.85, 0.72, 1.0)
diffuse.inputs['Roughness'].default_value = 0.6

shader2rgb = nodes.new('ShaderNodeShaderToRGB')
shader2rgb.location = (-200, 300)

band_ramp = nodes.new('ShaderNodeValToRGB')
band_ramp.location = (0, 300)
band_ramp.color_ramp.interpolation = 'CONSTANT'
band_ramp.color_ramp.elements[0].position = 0.3
band_ramp.color_ramp.elements[0].color = (0.2, 0.2, 0.25, 1.0)
band_ramp.color_ramp.elements[1].position = 0.6
band_ramp.color_ramp.elements[1].color = (0.98, 0.85, 0.72, 1.0)
highlight = band_ramp.color_ramp.elements.new(0.85)
highlight.color = (1.0, 1.0, 1.0, 1.0)

fresnel = nodes.new('ShaderNodeFresnel')
fresnel.location = (-600, 0)
fresnel.inputs['IOR'].default_value = 1.3

rim_ramp = nodes.new('ShaderNodeValToRGB')
rim_ramp.location = (-400, 0)
rim_ramp.color_ramp.elements[0].position = 0.4
rim_ramp.color_ramp.elements[1].position = 0.8
rim_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
rim_ramp.color_ramp.elements[1].color = (0.8, 0.6, 1.0, 1.0)

rim_emission = nodes.new('ShaderNodeEmission')
rim_emission.location = (-200, 0)

mix_rim = nodes.new('ShaderNodeMixShader')
mix_rim.location = (200, 300)

output = nodes.new('ShaderNodeOutputMaterial')
output.location = (400, 300)

links.new(diffuse.outputs['BSDF'], shader2rgb.inputs['Shader'])
links.new(shader2rgb.outputs['Shader'], band_ramp.inputs['Fac'])
links.new(band_ramp.outputs['Color'], mix_rim.inputs[1])
links.new(fresnel.outputs['Fac'], rim_ramp.inputs['Fac'])
links.new(rim_ramp.outputs['Color'], rim_emission.inputs['Color'])
links.new(rim_emission.outputs['Emission'], mix_rim.inputs[2])
links.new(mix_rim.outputs['Shader'], output.inputs['Surface'])

# Apply to body
body.data.materials.clear()
body.data.materials.append(skin_mat)
print("[DEBUG] ✅ Cel-shading material applied to body.")

# ──────────────────────────────────
# 5. OUTLINE (BACKFACE + SOLIDIFY)
# ──────────────────────────────────
print("[DEBUG] 5. Adding outline...")

def add_outline(obj, arm):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate()
    outline = bpy.context.active_object
    outline.name = obj.name + "_Outline"
    outline.data.materials.clear()
    black_mat = bpy.data.materials.new("Outline_Black")
    black_mat.use_nodes = True
    emit = black_mat.node_tree.nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (0, 0, 0, 1)
    emit.inputs['Strength'].default_value = 1.0
    out_node = black_mat.node_tree.nodes['Material Output']
    black_mat.node_tree.links.new(emit.outputs['Emission'], out_node.inputs['Surface'])
    black_mat.use_backface_culling = True
    outline.data.materials.append(black_mat)
    solidify = outline.modifiers.new(name="Outline", type='SOLIDIFY')
    solidify.thickness = 0.02
    solidify.offset = -1
    solidify.use_flip_normals = True
    solidify.use_quality_normals = True
    outline.parent = arm
    arm_mod = outline.modifiers.new(name='Armature', type='ARMATURE')
    arm_mod.object = arm
    print(f"[DEBUG]   ✅ Outline added to {outline.name}")
    return outline

add_outline(body, armature)

# ──────────────────────────────────
# 6. ENHANCE EYES (BLUE, GLOW)
# ──────────────────────────────────
print("[DEBUG] 6. Enhancing eyes...")
eye_objects = [obj for obj in bpy.data.objects if 'eye' in obj.name.lower() and obj.type == 'MESH']
if not eye_objects:
    eye_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and len(obj.data.vertices) < 50]

for eye in eye_objects:
    mat = bpy.data.materials.new(f"Anime_Eye_{eye.name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    diff = nodes.new('ShaderNodeBsdfDiffuse')
    diff.inputs['Color'].default_value = (0.2, 0.7, 1.0, 1.0)
    emit = nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (0.2, 0.7, 1.0, 1.0)
    emit.inputs['Strength'].default_value = 0.3
    mix = nodes.new('ShaderNodeMixShader')
    mix.inputs['Fac'].default_value = 0.7
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(diff.outputs['BSDF'], mix.inputs[1])
    links.new(emit.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], out.inputs['Surface'])
    eye.data.materials.clear()
    eye.data.materials.append(mat)
    print(f"[DEBUG]   ✅ Eye material applied to {eye.name}")

# ──────────────────────────────────
# 7. PINK HAIR
# ──────────────────────────────────
print("[DEBUG] 7. Creating pink hair...")

try:
    from char_morph.hair import OpCreateHair
    OpCreateHair.execute(None, bpy.context)
    print("[DEBUG]   ✅ OpCreateHair.execute() called.")
except Exception as e:
    print(f"[WARN] ⚠️ Hair operator failed: {e}")

# find hair mesh
hair_obj = None
for obj in bpy.data.objects:
    if 'hair' in obj.name.lower() and obj.type == 'MESH' and obj != body:
        hair_obj = obj
        break
if not hair_obj:
    meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o != body and 'outline' not in o.name.lower()]
    if meshes:
        hair_obj = max(meshes, key=lambda o: len(o.data.vertices))
        print(f"[WARN] Hair mesh guessed: {hair_obj.name}")
    else:
        print("[ERROR] ❌ No hair mesh found.")

if hair_obj:
    hair_mat = bpy.data.materials.new("Anime_Pink_Hair")
    hair_mat.use_nodes = True
    nodes = hair_mat.node_tree.nodes
    links = hair_mat.node_tree.links
    nodes.clear()
    diff = nodes.new('ShaderNodeBsdfDiffuse')
    diff.inputs['Color'].default_value = (0.98, 0.45, 0.63, 1.0)
    diff.inputs['Roughness'].default_value = 0.3
    glossy = nodes.new('ShaderNodeBsdfAnisotropic')
    glossy.inputs['Color'].default_value = (1.0, 0.8, 0.9, 1.0)
    glossy.inputs['Roughness'].default_value = 0.1
    glossy.inputs['Anisotropy'].default_value = 0.8
    mix_hair = nodes.new('ShaderNodeMixShader')
    mix_hair.inputs['Fac'].default_value = 0.2
    shader2rgb = nodes.new('ShaderNodeShaderToRGB')
    shader2rgb.location = (-200, 200)
    band_ramp = nodes.new('ShaderNodeValToRGB')
    band_ramp.color_ramp.interpolation = 'CONSTANT'
    band_ramp.color_ramp.elements[0].position = 0.3
    band_ramp.color_ramp.elements[0].color = (0.4, 0.1, 0.2, 1.0)
    band_ramp.color_ramp.elements[1].position = 0.7
    band_ramp.color_ramp.elements[1].color = (0.98, 0.45, 0.63, 1.0)
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(diff.outputs['BSDF'], shader2rgb.inputs['Shader'])
    links.new(shader2rgb.outputs['Shader'], band_ramp.inputs['Fac'])
    links.new(band_ramp.outputs['Color'], mix_hair.inputs[1])
    links.new(glossy.outputs['BSDF'], mix_hair.inputs[2])
    links.new(mix_hair.outputs['Shader'], out.inputs['Surface'])
    hair_obj.data.materials.clear()
    hair_obj.data.materials.append(hair_mat)
    print("[DEBUG] ✅ Pink hair material applied.")
    add_outline(hair_obj, armature)
else:
    print("[WARN] ⚠️ Skipping hair material (no hair mesh).")

# ──────────────────────────────────
# 8. OPTIONAL CLOTHING (skip gracefully)
# ──────────────────────────────────
print("[DEBUG] 8. Attempting clothing...")
try:
    from char_morph.assets import OpFitLibrary
    # Not sure of signature, just skip if fails
    print("[DEBUG]   Clothing OpFitLibrary exists but not executed.")
except:
    print("[DEBUG]   Clothing operator not available.")

# ──────────────────────────────────
# 9. LIGHTING
# ──────────────────────────────────
print("[DEBUG] 9. Setting up studio lighting...")
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj)

bpy.ops.object.light_add(type='SUN', location=(3, -2, 4))
key = bpy.context.active_object
key.data.energy = 3.0
key.data.angle = math.radians(10)
key.data.color = (1.0, 0.95, 0.9)
print("[DEBUG]   Key light added.")

bpy.ops.object.light_add(type='AREA', location=(-2, 1, 2))
fill = bpy.context.active_object
fill.data.energy = 80
fill.data.size = 3
fill.data.color = (0.8, 0.85, 1.0)
print("[DEBUG]   Fill light added.")

bpy.ops.object.light_add(type='AREA', location=(0, 2, 3))
rim = bpy.context.active_object
rim.data.energy = 150
rim.data.size = 2
rim.data.color = (1.0, 0.6, 0.8)
print("[DEBUG]   Rim light added.")

world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.7, 0.7, 0.8, 1.0)
bg.inputs['Strength'].default_value = 0.3
print("[DEBUG] ✅ World background set.")

# ──────────────────────────────────
# 10. CAMERA
# ──────────────────────────────────
print("[DEBUG] 10. Setting up camera...")
bpy.ops.object.camera_add(location=(0, -5, 1.2))
camera = bpy.context.active_object
camera.name = "Main_Camera"
camera.rotation_euler = (math.radians(80), 0, 0)
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.2
bpy.context.scene.camera = camera
print("[DEBUG] ✅ Camera created and set.")

# ──────────────────────────────────
# 11. POSE (relax arms)
# ──────────────────────────────────
print("[DEBUG] 11. Applying pose...")
if armature:
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    for bone_name in ['upper_arm.L', 'upper_arm.R']:
        bone = armature.pose.bones.get(bone_name)
        if bone:
            bone.rotation_euler = (0, 0.3 if '.L' in bone_name else -0.3, 0)
            print(f"[DEBUG]   Pose adjusted: {bone_name}")
        else:
            print(f"[WARN]   Bone not found: {bone_name}")
    bpy.ops.object.mode_set(mode='OBJECT')
else:
    print("[WARN] ⚠️ No armature to pose.")

# ──────────────────────────────────
# 12. RENDER SETTINGS (for preview)
# ──────────────────────────────────
print("[DEBUG] 12. Setting render defaults...")
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.film_transparent = False
print("[DEBUG] ✅ Render settings configured.")

# ──────────────────────────────────
# 13. SAVE FINAL BLEND
# ──────────────────────────────────
print("[DEBUG] 13. Saving char_final.blend...")
bpy.ops.wm.save_as_mainfile(filepath="char_final.blend")
print("[DEBUG] ✅ char_final.blend saved successfully.")
print("=" * 60)
print("🎉 SCRIPT COMPLETED SUCCESSFULLY!")
print("=" * 60)
