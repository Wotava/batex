bl_info = {
    "name" : "Batex",
    "author" : "jayanam, fork maintainer: wotava",
    "descrtion" : "Batch export as Fbx",
    "blender" : (2, 80, 0),
    "version" : (0, 6, 1, 0),
    "location" : "3D View -> Batex panel",
    "warning" : "",
    "doc_url": "https://github.com/Wotava/batex/blob/master/README.md",
    "tracker_url": "https://github.com/Wotava/batex/issues",
    "category" : "Import-Export"
}
if "bpy" in locals():
    import importlib
    importlib.reload(bex_panel)
    importlib.reload(bex_op)
    importlib.reload(bex_folder_op)
    print("[BATEX] Addon reload")
else:
    import bpy
    from bpy.props import *
    from . import bex_panel
    from . import bex_op
    from . import bex_folder_op
    print("[BATEX] Addon load")


bpy.types.Scene.export_folder = StringProperty(name="Export folder",
               subtype="DIR_PATH", 
               description="Directory to export the fbx files into")

bpy.types.Scene.center_transform = BoolProperty(name="Center transform",
                default=True,
                description="Set the pivot point of the object to the center")

bpy.types.Scene.apply_transform = BoolProperty(name="Apply transform",
                default=True,
                description="Applies scale and transform (Experimental)")

bpy.types.Scene.export_smoothing = EnumProperty(
    name="Smoothing",
    description="Defines the export smoothing information",
    items=(
        ('EDGE', 'Edge', 'Write edge smoothing',0),
        ('FACE', 'Face', 'Write face smoothing',1),
        ('OFF', 'Normals Only', 'Write normals only',2)
        ),
    default='OFF'
    )

def check_armature(self, context):  # enable armature export if export_animations is enabled
    if self.export_animations:
        temp = self.object_types
        temp.add('ARMATURE')
        self.object_types = temp

bpy.types.Scene.export_animations = BoolProperty(name="Export Rig & Animations",
                default=False,
                description="Export rig and animations",
                update=check_armature
                                                )

bpy.types.Scene.one_material_ID = BoolProperty(name="One material ID",
                default=True,
                description="Export just one material per object")

bpy.types.Scene.global_scale = FloatProperty(
        name="Scale",
        description="Scale all data (Some importers do not support scaled armatures!)",
        min=0.001, max=1000.0,
        soft_min=0.01, soft_max=1000.0,
        default=1.0,
        )
bpy.types.Scene.apply_unit_scale = BoolProperty(
        name="Apply Unit",
        description="Take into account current Blender units settings (if unset, raw Blender Units values are used as-is)",
        default=True,
        )
bpy.types.Scene.apply_scale_options = EnumProperty(
        items=(('FBX_SCALE_NONE', "All Local",
                "Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0"),
               ('FBX_SCALE_UNITS', "FBX Units Scale",
                "Apply custom scaling to each object transformation, and units scaling to FBX scale"),
               ('FBX_SCALE_CUSTOM', "FBX Custom Scale",
                "Apply custom scaling to FBX scale, and units scaling to each object transformation"),
               ('FBX_SCALE_ALL', "FBX All",
                "Apply custom scaling and units scaling to FBX scale"),
               ),
        name="Apply Scalings",
        description="How to apply custom and units scalings in generated FBX file "
                    "(Blender uses FBX scale to detect units on import, "
                    "but many other applications do not handle the same way)",
        )

bpy.types.Scene.use_triangles = BoolProperty(
            name="Triangulate Faces",
            description="Convert all faces to triangles",
            default=False,
            )

bpy.types.Scene.axis_forward = EnumProperty(
    name="Axis Forward",
    items=(
        ('X', '+X Forward', ''),
        ('Y', '+Y Forward', ''),
        ('Z', '+Z Forward', ''),
        ('-X', '-X Forward', ''),
        ('-Y', '-Y Forward', ''),
        ('-Z', '-Z Forward', ''),
    ),
    default='-Z'
    )

bpy.types.Scene.axis_up = EnumProperty(
    name="Axis Up",
    items=(
        ('X', '+X Up', ''),
        ('Y', '+Y Up', ''),
        ('Z', '+Z Up', ''),
        ('-X', '-X Up', ''),
        ('-Y', '-Y Up', ''),
        ('-Z', '-Z Up', ''),
    ),
    default='Y'
    )

bpy.types.Scene.object_types = EnumProperty(
    name="Object Types",
    options={'ENUM_FLAG'},
    items=(('EMPTY', "Empty", ""),
           ('CAMERA', "Camera", ""),
           ('LIGHT', "Lamp", ""),
           ('ARMATURE', "Armature", "WARNING: not supported in dupli/group instances"),
           ('MESH', "Mesh", ""),
           ('OTHER', "Other", "Other geometry types, like curve, metaball, etc. (converted to meshes)"),
           ),
    description="Which kind of object to export",
    default={'MESH'},
)

bpy.types.Scene.remove_postfix = BoolProperty(name="Remove postfixes",
                default=True,
                description="Attempts to remove .XXX (ex: name.012) postfix from object names of specified types."
                            "[Parents]: If same names present in multiple objects, sorts their postfixes."
                            "[Childs]: Objects will be renamed with incremented postfix from parent if they "
                            "have the same name, otherwise child names will be sorted per parent,"
                            "[!WARNING!]May produce unexpected results if you have lots of naming repetition between "
                            "parent and child objects with different types. It's intended to rename SOCKET_ empties"
                            "for use with Unreal Engine")

bpy.types.Scene.remove_postfix_types = EnumProperty(
    name="Object Types",
    options={'ENUM_FLAG'},
    items=(('EMPTY', "Empty", ""),
           ('CAMERA', "Camera", ""),
           ('LIGHT', "Lamp", ""),
           ('MESH', "Mesh", ""),
           ('OTHER', "Other", "Other geometry types, like curve, metaball, etc. (converted to meshes)"),
           ),
    description="Which kind of object to rename",
    default={'MESH', 'EMPTY'},
)

classes = (bex_panel.BATEX_PT_Panel, bex_op.BATEX_OT_Operator, bex_folder_op.BATEX_OT_OpenFolder )

register, unregister = bpy.utils.register_classes_factory(classes)
    
if __name__ == "__main__":
    register()
