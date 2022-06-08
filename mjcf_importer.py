#!/usr/bin/python3

import os
from xml.etree import ElementTree
from bpy.types import (Armature, BlendData, Camera, Image, Light,
                       Material, Mesh, Object)
from typing import Dict, List
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

class MJCFBuilder:
    def __init__(self, file_in: str, file_out: str):
        clear_data(bpy.data)
        self.file_path = file_in
        self.remove_meshes: Dict[str, str] = {}
        self.add_meshes: Dict[str, Dict[str, str]] = {}
        self.tree = ElementTree.parse(self.file_path)
        self.build_mjcf()
        self.tree.write(file_out)

    def replace_mesh(self, ele: ElementTree.Element):
        remove_eles = []
        for ele_child in ele:
            if ele_child.tag == 'geom' and self.remove_meshes.get(ele_child.attrib.get('mesh')) is not None:
                mesh_name = ele_child.attrib.get('mesh')
                if self.add_meshes.get(mesh_name) is not None:
                    for add_mesh_name in self.add_meshes.get(mesh_name):
                        new_ele = ElementTree.Element('geom')
                        if ele_child.attrib.get('pos') is not None:
                            new_ele.attrib['pos'] = ele_child.attrib.get('pos')
                        if ele_child.attrib.get('quat') is not None:
                            new_ele.attrib['quat'] = ele_child.attrib.get('quat')
                        new_ele.attrib['type'] = 'mesh'
                        new_ele.attrib['mesh'] = add_mesh_name
                        ele.append(new_ele)
                    remove_eles.append(ele_child)
            self.replace_mesh(ele_child)
        for remove_ele in remove_eles:
            ele.remove(remove_ele)

    def build_mjcf(self) -> None:
        root = self.tree.getroot()
        mesh_dir = os.path.dirname(self.file_path)
        for ele1 in root:
            if ele1.tag == 'compiler' and ele1.attrib.get('meshdir') is not None:
                mesh_dir = ele1.attrib['meshdir']
            if ele1.tag == 'asset':
                for ele2 in ele1:
                    if ele2.tag == 'mesh':
                        self.remove_meshes[ele2.attrib['name']] = ele2.attrib['file']

        for mesh_name in self.remove_meshes:
            mesh_path = os.path.join(mesh_dir, self.remove_meshes[mesh_name])
            bpy.ops.import_scene.obj(filepath=mesh_path)

            bpy.ops.object.select_all(action='DESELECT')

            object: Object
            i = 0
            new_mesh: Dict[str, str] = {}
            for object in bpy.data.objects:
                object.select_set(True)
                object.rotation_mode = 'XYZ'
                object.rotation_euler = (0, 0, 0)
                file_name = object.name + '.stl'
                new_mesh_path = os.path.join(os.path.dirname(mesh_path), file_name)
                bpy.ops.export_mesh.stl(filepath=new_mesh_path, use_selection=True)
                object.select_set(False)
                new_mesh[mesh_name + str(i)] = new_mesh_path
                i += 1

            self.add_meshes[mesh_name] = new_mesh
            clear_data(bpy.data)

        for ele1 in root:
            if ele1.tag == 'asset':
                remove_eles = []
                for ele2 in ele1:
                    if ele2.tag == 'mesh' and self.remove_meshes.get(ele2.attrib.get('name')) is not None:
                        remove_eles.append(ele2)

                for remove_ele in remove_eles:
                    ele1.remove(remove_ele)

            if ele1.tag == 'worldbody':
                self.replace_mesh(ele1)

        new_asset = ElementTree.Element('asset')
        for new_meshes in self.add_meshes.values():
            for new_mesh_name, new_mesh_file in new_meshes.items():
                new_mesh = ElementTree.Element('mesh')
                new_mesh.attrib['name'] = new_mesh_name
                new_mesh.attrib['file'] = new_mesh_file
                new_asset.append(new_mesh)
        root.insert(0, new_asset)

        return None

if __name__ == '__main__':
    file_in = '/home/giang/Workspace/mujoco_ws/src/mujoco_world/mujoco_world/model/iai_kitchen_python.xml'
    file_out = '/home/giang/Workspace/mujoco_ws/src/mujoco_world/mujoco_world/model/iai_kitchen_python.xml'
    MJCFBuilder(file_in, file_out)
