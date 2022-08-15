import bpy

# Get a copy of an object's location
def get_object_loc(obj):
  return obj.location.copy()

# Set the location of an object
def set_object_to_loc(obj, loc):
  obj.location = loc

def get_children(obj): 
  children = [] 
  for ob in bpy.data.objects: 
      if ob.parent == obj: 
          children.append(ob) 
  return children 

def get_cursor_loc(context):
  return context.scene.cursor.location.copy()

def selected_to_cursor():
  bpy.ops.view3d.snap_selected_to_cursor()

def set_cursor_loc(context, loc : tuple):
  context.scene.cursor.location = loc

def swap_names(context, target_name, target_object):
    scene_objs = context.scene.objects
    ref_index = scene_objs.find(target_name)
    if ref_index != -1:
        ref = scene_objs[ref_index]
        temp_name = target_object.name + ";"
        ref.name = temp_name
        target_object.name = target_name
        ref.name = ref.name.strip(";")
    else:
        target_object.name = target_name
