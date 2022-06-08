#!/usr/bin/python3

import os
from bpy.types import (Armature, BlendData, Camera, Image, Light,
                       Material, Mesh, Object)
import bpy

def clear_data(data: BlendData) -> None:
    armature: Armature
    for armature in data.armatures:
        data.armatures.remove(armature)
    mesh: Mesh
    for mesh in data.meshes:
        data.meshes.remove(mesh)
    object: Object
    for object in data.objects:
        data.objects.remove(object)
    material: Material
    for material in data.materials:
        data.materials.remove(material)
    camera: Camera
    for camera in data.cameras:
        data.cameras.remove(camera)
    light: Light
    for light in data.lights:
        data.lights.remove(light)
    image: Image
    for image in data.images:
        data.images.remove(image)

    return None

def dae_to_stl(file_path) -> None:
    for file in os.listdir(file_path):
        if file.endswith('.dae'):
            dae_mesh_path = os.path.join(file_path, file)
            stl_mesh_path = dae_mesh_path.replace("dae", "stl")
            bpy.ops.wm.collada_import(filepath=dae_mesh_path)
            for object in bpy.data.objects:
                object.select_set(True)
                object.rotation_mode = 'XYZ'
                object.rotation_euler = (0, 0, 0)
                object.select_set(False)
            bpy.ops.export_mesh.stl(filepath=stl_mesh_path)
            clear_data(bpy.data)

    return None

if __name__ == '__main__':
    file_path = '/home/giang/Workspace/mujoco_ws/src/mujoco_robots/tiago/tiago_mujoco/model/tiago/meshes/'
    clear_data(bpy.data)
    dae_to_stl(file_path)
