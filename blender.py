import bpy
from math import radians

gltf_file_path = "/home/tomek/Documents/lego_pd/api/database/gltf/1.gltf"

bpy.ops.import_scene.gltf(filepath=gltf_file_path)


obj = bpy.context.object

obj.rotation_euler[0] = radians(-90)

obj.matrix_world = obj.matrix_world @ obj.rotation_euler.to_matrix().to_4x4()


