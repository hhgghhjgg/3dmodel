import bpy
import os

print("🔍 Listing all char_morph operators...")
for op in dir(bpy.ops.char_morph):
    if not op.startswith('_'):
        print(f"  - bpy.ops.char_morph.{op}()")
