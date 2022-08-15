import bpy
import bmesh
import os
from . bex_utils import *

class BatEx_Export:

  def __init__(self, context):
    self.__context = context
    
    self.__export_folder = context.scene.export_folder
    if self.__export_folder.startswith("//"):
      self.__export_folder = os.path.abspath(bpy.path.abspath(context.scene.export_folder))

    self.__center_transform = context.scene.center_transform
    self.__apply_transform = context.scene.apply_transform
    self.__one_material_id = context.scene.one_material_ID
    self.__export_objects = context.selected_objects
    self.__export_animations = context.scene.export_animations
    self.__remove_postfix = context.scene.remove_postfix
    self.__remove_postfix_types = context.scene.remove_postfix_types
    self.__mat_faces = {}
    self.__materials = []
  
  def do_center(self, obj):
    if self.__center_transform:
      loc = get_object_loc(obj)
      set_object_to_loc(obj, (0,0,0))
      return loc

    return None

  def remove_materials(self, obj):
    if obj.type != 'MESH':
      return False

    mat_count = len(obj.data.materials)

    if mat_count > 1 and self.__one_material_id:

      # Save material ids for faces
      bpy.ops.object.mode_set(mode='EDIT')

      bm = bmesh.from_edit_mesh(obj.data)

      for face in bm.faces:
        self.__mat_faces[face.index] = face.material_index

      # Save and remove materials except the last one
      # so that we keep this as material id
      bpy.ops.object.mode_set(mode='OBJECT')
      self.__materials.clear()

      for idx in range(mat_count):
        self.__materials.append(obj.data.materials[0])
        if idx < mat_count - 1:
          obj.data.materials.pop(index=0)

      return True
    else:
      return False

  def restore_materials(self, obj):

    # Restore the materials for the object
    obj.data.materials.clear()

    for mat in self.__materials:
      obj.data.materials.append(mat)

    obj.data.update()

    # Reassign the material ids to the faces of the mesh
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)

    for face in bm.faces:
        mat_index = self.__mat_faces[face.index]
        face.material_index = mat_index

    bmesh.update_edit_mesh(obj.data)

    bpy.ops.object.mode_set(mode='OBJECT')

  def do_export(self):

    bpy.ops.object.mode_set(mode='OBJECT')
    global_renames = dict()

    for obj in self.__export_objects:
      bpy.ops.object.select_all(action='DESELECT') 
      obj.select_set(state=True)

      # Center selected object
      old_pos = self.do_center(obj)

      # Select children if exist
      children = []
      for child in get_children(obj):
        child.select_set(state=True)
        children.append(child)

      # Remove materials except the last one
      materials_removed = self.remove_materials(obj)

      # Remove name postfix
      if self.__remove_postfix:

        # Rename parent object if needed
        # Parent names should be preserved and incremented consistently across the entire export process since you
        # can't export objects with the same names to different files (yet), because exporter will keep overriding one
        # file with that name, like Cube, Cube.001 and Cube.002 will be written to Cube.fbx over each other
        # But "local" (child) renames are tracked separately, because their names don't affect export file name
        local_renames = dict()
        if len(obj.name) > 3 and obj.name[-4] == '.' and obj.type in self.__remove_postfix_types:
          if obj.name[0:-4] in global_renames:
            global_renames[obj.name[0:-4]] += 1
            target_name = obj.name[0:-4] + "." + str(1000 + global_renames[obj.name[0:-4]])[-3:]
          else:
            target_name = obj.name[0:-4]
            global_renames[target_name] = 0
          swap_names(self.__context, target_name, obj)
        elif obj.type in self.__remove_postfix_types:
          global_renames[obj.name] = 0

        # rename child objects
        for selection in children:
          if selection.name[-4] != '.':
            local_renames[selection.name] = 0
          if selection.name[-4] != '.' or selection.type not in self.__remove_postfix_types:
            continue

          # if this name was not affected during this export yet,
          # check if it's related to parent object and rename accordingly
          target_name = selection.name[0:-4]
          if target_name not in local_renames and target_name not in global_renames:
            if selection.parent.name == target_name:
              local_renames[target_name] = 1
              target_name = selection.name[0:-4] + ".001"
            else:
              local_renames[target_name] = 0
            swap_names(self.__context, target_name, selection)
            continue

          # process already used names
          if selection.name[0:-4] in local_renames:
            local_renames[selection.name[0:-4]] += 1
            target_name = selection.name[0:-4] + "." + str(1000 + local_renames[selection.name[0:-4]])[-3:]
          elif selection.name[0:-4] in global_renames:
            local_renames[selection.name[0:-4]] = global_renames[selection.name[0:-4]] + 1
            target_name = selection.name[0:-4] + "." + str(1000 + local_renames[selection.name[0:-4]])[-3:]
          swap_names(self.__context, target_name, selection)
          print(selection.name)

      ex_object_types = self.__context.scene.object_types

      if(self.__export_animations):
        ex_object_types.add('ARMATURE')

      # De-select objects with types not selected in object_types and skip export if no objects remain selected so
      # we won't export empty files
      for obj_s in self.__context.selected_objects:
        if obj_s.type not in ex_object_types:
          obj_s.select_set(state=False)
      if len(self.__context.selected_objects) == 0:
        continue

      # Export the selected object as fbx
      bpy.ops.export_scene.fbx(check_existing=False,
      filepath=self.__export_folder + "/" + obj.name + ".fbx",
      filter_glob="*.fbx",
      use_selection=True,
      object_types=ex_object_types,
      bake_anim=self.__export_animations,
      bake_anim_use_all_bones=self.__export_animations,
      bake_anim_use_all_actions=self.__export_animations,
      use_armature_deform_only=True,
      bake_space_transform=self.__apply_transform,
      mesh_smooth_type=self.__context.scene.export_smoothing,
      add_leaf_bones=False,
      path_mode='ABSOLUTE',
      axis_forward=self.__context.scene.axis_forward,
      axis_up=self.__context.scene.axis_up,
      apply_unit_scale=self.__context.scene.apply_unit_scale,
      apply_scale_options=self.__context.scene.apply_scale_options,
      global_scale=self.__context.scene.global_scale,
      use_triangles=self.__context.scene.use_triangles
      )

      if materials_removed:
        self.restore_materials(obj)

      if old_pos is not None:
        set_object_to_loc(obj, old_pos)