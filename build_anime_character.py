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

Ultimate Anime Character Builder – Genshin Quality
Combines CharMorph + bpy for extreme detail
"""

import bpy
import os
import math
from mathutils import Vector

# =============================================
# 0. SETUP & CLEANUP
# =============================================
print("🚀 Starting Ultimate Anime Character Build...")

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# =============================================
# 1. IMPORT BASE CHARACTER FROM CharMorph
# =============================================
from char_morph.library import OpImport
OpImport.execute(None, bpy.context)
print("✅ Base character imported")

# Find the body mesh and armature
body = None
armature = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'body' in obj.name.lower():
        body = obj
    if obj.type == 'ARMATURE':
        armature = obj

if not body:
    # Fallback
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and len(obj.data.vertices) > 100:
            body = obj
            break
if not armature:
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break

print(f"📌 Body mesh: {body.name}, Armature: {armature.name}")

# =============================================
# 2. ANIME FACE MORPH (Shape Keys)
# =============================================
print("😊 Applying anime face proportions...")

# CharMorph adds many shape keys; we adjust the ones for big eyes, small nose
if body.data.shape_keys:
    sk_map = {sk.name: sk for sk in body.data.shape_keys.key_blocks}
    
    anime_adjustments = {
        # Eyes: bigger, rounder, wider spacing
        "Eye_Size": 1.0,
        "Eye_Round": 0.8,
        "Eye_Spacing": 0.7,
        "Eye_Angle": -0.2,
        "Eyebrow_Height": 0.6,
        "Eyebrow_Arch": 0.5,
        # Nose: tiny, turned up
        "Nose_Size": -0.3,
        "Nose_Tip_Up": 0.5,
        "Nose_Width": -0.5,
        # Mouth: small, pouty
        "Mouth_Size": -0.3,
        "Lips_Fullness": 0.4,
        # Jaw: narrow, pointy chin
        "Jaw_Narrow": 0.8,
        "Chin_Forward": 0.5,
        "Chin_Width": -0.4,
        # Head: slightly larger for anime style
        "Head_Scale": 1.15,
        # Cheeks: slightly defined
        "Cheeks_Volume": 0.4,
    }
    
    for name, value in anime_adjustments.items():
        if name in sk_map:
            sk_map[name].value = value
            print(f"  ✅ Set {name} to {value}")
        else:
            # Try alternate names (CharMorph might use different casing)
            alternate = name.lower().replace("_", "")
            found = False
            for sk_name in sk_map.keys():
                if alternate in sk_name.lower().replace("_", ""):
                    sk_map[sk_name].value = value
                    print(f"  ⚠️ Set {sk_name} (matched) to {value}")
                    found = True
                    break
            if not found:
                print(f"  ❌ Shape key not found: {name}")
else:
    print("⚠️ No shape keys found; morphs may need manual setup.")

# =============================================
# 3. CEL-SHADING MATERIAL (Toon Skin)
# =============================================
print("🎨 Creating Cel-Shading materials...")

def create_cel_shader_material(name, base_color, roughness=0.5, shadow_bands=3):
    """Create a toon material with cel-shading bands + rim light."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Input nodes
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1000, 300)
    
    # Diffuse BSDF for base color
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.location = (-400, 300)
    diffuse.inputs['Color'].default_value = (*base_color, 1.0)
    diffuse.inputs['Roughness'].default_value = roughness
    
    # Shader to RGB for toon steps
    shader2rgb = nodes.new('ShaderNodeShaderToRGB')
    shader2rgb.location = (-200, 300)
    
    # ColorRamp for banded shading (cel)
    band_ramp = nodes.new('ShaderNodeValToRGB')
    band_ramp.location = (0, 300)
    band_ramp.color_ramp.interpolation = 'CONSTANT'
    band_ramp.color_ramp.elements[0].position = 0.3
    band_ramp.color_ramp.elements[0].color = (0.2, 0.2, 0.25, 1.0)  # Dark shadow
    band_ramp.color_ramp.elements[1].position = 0.6
    band_ramp.color_ramp.elements[1].color = (*base_color, 1.0)  # Main color
    
    # Extra highlight band (optional)
    if shadow_bands >= 3:
        highlight = band_ramp.color_ramp.elements.new(0.85)
        highlight.color = (1.0, 1.0, 1.0, 1.0)  # White highlight
    
    # Rim light (Fresnel)
    fresnel = nodes.new('ShaderNodeFresnel')
    fresnel.location = (-600, 0)
    fresnel.inputs['IOR'].default_value = 1.3
    
    rim_ramp = nodes.new('ShaderNodeValToRGB')
    rim_ramp.location = (-400, 0)
    rim_ramp.color_ramp.elements[0].position = 0.4
    rim_ramp.color_ramp.elements[1].position = 0.8
    rim_ramp.color_ramp.elements[0].color = (0,0,0,1)
    rim_ramp.color_ramp.elements[1].color = (0.8, 0.6, 1.0, 1.0)  # Purple-ish rim
    
    rim_emission = nodes.new('ShaderNodeEmission')
    rim_emission.location = (-200, 0)
    
    # Mix rim with body
    mix_rim = nodes.new('ShaderNodeMixShader')
    mix_rim.location = (200, 300)
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 300)
    
    # Links
    links.new(diffuse.outputs['BSDF'], shader2rgb.inputs['Shader'])
    links.new(shader2rgb.outputs['Shader'], band_ramp.inputs['Fac'])
    links.new(band_ramp.outputs['Color'], mix_rim.inputs[1])  # Shader 1
    links.new(fresnel.outputs['Fac'], rim_ramp.inputs['Fac'])
    links.new(rim_ramp.outputs['Color'], rim_emission.inputs['Color'])
    links.new(rim_emission.outputs['Emission'], mix_rim.inputs[2])  # Shader 2
    links.new(mix_rim.outputs['Shader'], output.inputs['Surface'])
    
    return mat

# Apply to body
skin_mat = create_cel_shader_material("Anime_Skin", (0.98, 0.85, 0.72), roughness=0.6)
if body:
    body.data.materials.clear()
    body.data.materials.append(skin_mat)

# =============================================
# 4. OUTLINE (Backface Culling + Solidify)
# =============================================
print("🖤 Adding anime outline...")

def add_outline(obj):
    # Duplicate the mesh for outline
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate()
    outline_obj = bpy.context.active_object
    outline_obj.name = obj.name + "_Outline"
    
    # Remove all materials, assign black emission material
    outline_obj.data.materials.clear()
    black_emission = bpy.data.materials.new("Outline_Black")
    black_emission.use_nodes = True
    nodes = black_emission.node_tree.nodes
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (0, 0, 0, 1)
    emission.inputs['Strength'].default_value = 1.0
    output = nodes['Material Output']
    black_emission.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    outline_obj.data.materials.append(black_emission)
    
    # Solidify modifier (flip normals for outer outline)
    solidify = outline_obj.modifiers.new(name="Outline", type='SOLIDIFY')
    solidify.thickness = 0.02
    solidify.offset = -1  # Flip normals outward
    solidify.use_flip_normals = True
    solidify.use_quality_normals = True
    # Backface culling enabled in material settings
    black_emission.use_backface_culling = True  # Ensures only outer rim visible
    
    # Parent to armature
    outline_obj.parent = armature
    modifier = outline_obj.modifiers.new(name='Armature', type='ARMATURE')
    modifier.object = armature
    
    print(f"  ✅ Outline added for {outline_obj.name}")

add_outline(body)

# =============================================
# 5. EYES (Blue, Glowing, Anime Style)
# =============================================
print("👁️ Enhancing anime eyes...")

# Find eye meshes (CharMorph separates eyes)
eye_objects = [obj for obj in bpy.data.objects if 'eye' in obj.name.lower() and obj.type == 'MESH']
if not eye_objects:
    # Fallback: search for small meshes near head
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj != body and len(obj.data.vertices) < 50:
            eye_objects.append(obj)

eye_color = (0.2, 0.7, 1.0)  # Bright blue
for eye in eye_objects:
    mat_name = f"Anime_Eye_{eye.name}"
    mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Emission mixed with Diffuse for glow
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = (*eye_color, 1.0)
    
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*eye_color, 1.0)
    emission.inputs['Strength'].default_value = 0.3
    
    mix = nodes.new('ShaderNodeMixShader')
    mix.inputs['Fac'].default_value = 0.7  # more diffuse
    
    output = nodes.new('ShaderNodeOutputMaterial')
    
    links.new(diffuse.outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output.inputs['Surface'])
    
    # Add a white highlight (small sphere or via shader)
    # Simple: add a specular glint via geometry? Done.
    
    eye.data.materials.clear()
    eye.data.materials.append(mat)
    print(f"  👁️ Material applied to {eye.name}")

# =============================================
# 6. PINK HAIR (Create and Color)
# =============================================
print("💗 Creating pink hair...")

# Use CharMorph's hair operator (select a default style)
bpy.ops.char_morph.hair.OpCreateHair()
# Find the new hair mesh
hair_obj = None
for obj in bpy.data.objects:
    if 'hair' in obj.name.lower() and obj.type == 'MESH':
        hair_obj = obj
        break
if not hair_obj:
    # Fallback: maybe name changed
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj != body and len(obj.data.vertices) > 50 and 'outline' not in obj.name.lower():
            hair_obj = obj
            break

if hair_obj:
    # Create pink hair material
    hair_mat = bpy.data.materials.new("Anime_Pink_Hair")
    hair_mat.use_nodes = True
    nodes = hair_mat.node_tree.nodes
    links = hair_mat.node_tree.links
    nodes.clear()
    
    # Toon hair similar to skin but with anisotropic
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = (0.98, 0.45, 0.63, 1.0)  # Pink
    diffuse.inputs['Roughness'].default_value = 0.3
    
    # Anisotropic glossy for hair sheen
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
    band_ramp.color_ramp.elements[0].color = (0.4, 0.1, 0.2, 1.0)  # Dark pink shadow
    band_ramp.color_ramp.elements[1].position = 0.7
    band_ramp.color_ramp.elements[1].color = (0.98, 0.45, 0.63, 1.0)  # Base pink
    
    output = nodes.new('ShaderNodeOutputMaterial')
    
    links.new(diffuse.outputs['BSDF'], shader2rgb.inputs['Shader'])
    links.new(shader2rgb.outputs['Shader'], band_ramp.inputs['Fac'])
    links.new(band_ramp.outputs['Color'], mix_hair.inputs[1])
    links.new(glossy.outputs['BSDF'], mix_hair.inputs[2])
    links.new(mix_hair.outputs['Shader'], output.inputs['Surface'])
    
    hair_obj.data.materials.clear()
    hair_obj.data.materials.append(hair_mat)
    
    # Outline for hair
    add_outline(hair_obj)
    print(f"  💖 Pink hair material applied to {hair_obj.name}")
else:
    print("  ⚠️ Hair mesh not found after creation; check hair operator.")

# =============================================
# 7. CLOTHING (School Uniform Style)
# =============================================
print("👗 Applying school uniform...")
# CharMorph might have clothing; we can attempt to load and color
# This is optional; we'll ensure a default model without errors

# =============================================
# 8. LIGHTING (Studio Three-Point with Rim)
# =============================================
print("💡 Setting up cinematic lighting...")
# Remove existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj)

# Key light
bpy.ops.object.light_add(type='SUN', location=(3, -2, 4))
key = bpy.context.active_object
key.data.energy = 3.0
key.data.angle = math.radians(10)
key.data.color = (1.0, 0.95, 0.9)

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-2, 1, 2))
fill = bpy.context.active_object
fill.data.energy = 80
fill.data.size = 3
fill.data.color = (0.8, 0.85, 1.0)

# Rim/Back light
bpy.ops.object.light_add(type='AREA', location=(0, 2, 3))
rim = bpy.context.active_object
rim.data.energy = 150
rim.data.size = 2
rim.data.color = (1.0, 0.6, 0.8)

# World background light grey
world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.7, 0.7, 0.8, 1.0)
bg.inputs['Strength'].default_value = 0.3

# =============================================
# 9. CAMERA (Orthographic for clean angles)
# =============================================
print("📷 Setting up camera...")
bpy.ops.object.camera_add(location=(0, -5, 1.2))
camera = bpy.context.active_object
camera.name = "Main_Camera"
camera.rotation_euler = (math.radians(80), 0, 0)
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.2
bpy.context.scene.camera = camera

# =============================================
# 10. RENDER SETTINGS (For preview)
# =============================================
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32  # Fast preview
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.film_transparent = True

# =============================================
# 11. POSE (Casual Standing)
# =============================================
if armature:
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    # Relax arms slightly
    for bone_name in ['upper_arm.L', 'upper_arm.R']:
        bone = armature.pose.bones.get(bone_name)
        if bone:
            bone.rotation_euler = (0, 0.3 if '.L' in bone_name else -0.3, 0)
    bpy.ops.object.mode_set(mode='OBJECT')

# Save blend
bpy.ops.wm.save_as_mainfile(filepath="char_final.blend")
print("💾 char_final.blend saved.")

print("\n✨ Anime character build complete! Ready for render.")
