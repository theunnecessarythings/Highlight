import bpy
from pygments.lexers import get_all_lexers


def get_language_items():
    items = []
    lexers = get_all_lexers()
    for lexer in lexers:
        items.append((lexer[0], lexer[0], ','.join(lexer[3])))
    
    return tuple(items)

class HighlightPanel(bpy.types.Panel):
    """Highlight"""
    bl_label = "Highlight"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'FONT'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        row = layout.row()
        row.label(text='Selected: ' + scene.hl_language)
        row.prop_menu_enum(scene, 'hl_language', text='Language')
        row = layout.row()
        row.operator('text.syntax_highlight', icon='FILE_REFRESH')
        
        row = layout.row(align=True)
        row.prop(context.active_object, 'hl_source')
        row.operator('text.load_src', icon="FILE_FOLDER", text="")
        

def register():
    bpy.types.Scene.hl_language = bpy.props.EnumProperty(
        items=get_language_items(),
        default='Python',
        name='Language'
    )
    
    bpy.types.Object.hl_source = bpy.props.StringProperty(name='Load From Source')
