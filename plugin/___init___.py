import bpy
from bpy.types import panel

class ToolPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Tolds Tab Label'
    bl_context = 'objectmode'
    bl_category = 'Other'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("Organize parts", text = 'Organize parts')
        
        
def register():
    bpy.utils.register_class(ToolPanel)
    
def unregister():
    bpy.utils.register_class(ToolPanel)
    
if __name__ == '__main__':
    register()
    