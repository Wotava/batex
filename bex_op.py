import bpy

if "Operator" in locals():
    import importlib
    importlib.reload(bex_export)
    print("[BATEX] OP reload")
else:
    from bpy.types import Operator
    from . import bex_export
    print("[BATEX] OP load")

class BATEX_OT_Operator(Operator):
    bl_idname = "object.bex_ot_operator"
    bl_label = "Batch Export"
    bl_description = "Export selected objects as fbx" 
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.axis_forward != context.scene.axis_up

    def execute(self, context):

        bat_export = bex_export.BatEx_Export(context)
        bat_export.do_export()
        
        self.report({'INFO'}, "Exported to " + context.scene.export_folder)
        return {'FINISHED'}


