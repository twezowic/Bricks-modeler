# skrypt dla blendera

import bpy
import os

def import_stl(filepath):
    bpy.ops.wm.stl_import(filepath=filepath)

def export_obj(filepath):
    bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True,export_materials=False)

directory = "D:\LEGO_MOJE\\test"
destination = "D:\LEGO_MOJE\\test\\obj"

def del_collection(coll):
    for c in coll.children:
        del_collection(c)
    bpy.data.collections.remove(coll,do_unlink=True)

for file in os.listdir(directory):
    if file.endswith(".stl"):
        filepath = os.path.join(directory, file)
        import_stl(filepath)

        scene_collection = bpy.context.scene.collection

        output_filepath = os.path.join(destination, os.path.splitext(file)[0] + ".obj")
        export_obj(output_filepath)
        if bpy.context.scene.collection.objects:
            last_object = bpy.context.scene.collection.objects[-1]
            bpy.data.objects.remove(last_object)