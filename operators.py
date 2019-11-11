from pygments.formatters import RawTokenFormatter
from pygments import highlight
from pygments.lexers import *
from pygments.lexers import find_lexer_class
import bpy 
import random 


def get_material_index(material, obj):
    for i in range(len(obj.material_slots)):
        if obj.material_slots[i].name == material:
            return i
    return None

def set_material(obj, first_index, last_index, material):
    mat_index = get_material_index(material, obj)
    if len(obj.data.body) == first_index:
        return
    for i in range(first_index, last_index):
        obj.data.body_format[i].material_index = mat_index


def create_material(name, obj):
    try:
        mat = bpy.data.materials[name]
    except:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    obj.data.materials.append(mat)
    
def randomize_materials(obj):
    for mat in obj.data.materials:
        try:
            mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (random.random(), random.random(), random.random(), 1)
        except Exception as e:
            print(e)

def process(processed_text, obj):
    material_list = set()
    text_list = processed_text.split('\n')
    
    for tl in text_list:
        if len(tl) > 1:
            tokens = tl.split('\t')
            material_list.add(tokens[0])
    
    #clear_materials(obj)
    obj.data.materials.clear()
    
    for material in material_list:
        create_material(material, obj)
    randomize_materials(obj)
    
    last_index = 0
    for tl in text_list:
        if len(tl) > 1:
            material, text = tl.split('\t')
            text = bytes(text, "utf-8").decode("unicode_escape")[1:-1]
            set_material(obj, last_index, last_index + len(text), material)
            last_index += len(text)

class ScanFileOperator(bpy.types.Operator):
    bl_idname = "text.load_src"
    bl_label = "Load From Source"
    filepath : bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        obj = context.active_object
        try:
            with open(self.filepath, 'r') as f:
                obj.data.body = f.read()
        except Exception as e:
            self.report({'ERROR'},'Please select a text file')
        obj.hl_source = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class HighlightOperator(bpy.types.Operator):
    """Syntax Hightlight the selected text object"""
    bl_idname = "text.syntax_highlight"
    bl_label = "Highlight"


    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'FONT'

    def execute(self, context):
        language = context.scene.hl_language
        lexer = find_lexer_class(language)
        
        code = context.active_object.data.body
        text = highlight(code, lexer(), RawTokenFormatter()).decode()
        process(text, context.active_object)
        return {'FINISHED'}
    
