import bpy
from bpy import context
from yakuza_cth.cth.exporter import *
from yakuza_cth.blender.import_export import *

class ExportCTH(bpy.types.Operator):
    """Export Yakuza CTH File"""
    bl_idname = "yakuza_cth.export"
    bl_label = "Export Yakuza CTH"

    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    @classmethod
    def poll(cls, context):
        return context.object is not None and type(context.object.data) is bpy.types.Armature

    def execute(self, context):
        CTH_Write_Exp_Data(self.directory)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ImportCTH(bpy.types.Operator):
    """Import Yakuza CTH/HCB File"""
    bl_idname = "yakuza_cth.import"
    bl_label = "Import Yakuza CTH/HCB"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = ".cth;.hcb"
    filter_glob: StringProperty(default = "*.cth;*.hcb" ,options = {'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.scene is not None ################

    def execute(self, context):
        #CTH_Write_Imp_Data(self.filepath)
        CTH_Import_File(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    

class CTHPropertyGroup(bpy.types.PropertyGroup):
    column_count: bpy.props.IntProperty(name="Column Count",soft_min = 0)
    row_count: bpy.props.IntProperty(name="Row Count",soft_min = 0)
    stiffness: bpy.props.IntProperty(name="Stiffness",soft_min = 0, soft_max = 255)
    ismesh_closed: bpy.props.BoolProperty(name="Mesh is closed")
    origin_X: bpy.props.FloatProperty(name="X", default = 0)
    origin_Y: bpy.props.FloatProperty(name="Y", default = -1)
    sort_mode: bpy.props.BoolProperty(name="Sort Mode", default = False)
    pro_mode: bpy.props.BoolProperty(name="Show Advanced Settings", default = False)

class CTHPanel(bpy.types.Panel):
    bl_label = "CTH Properties"
    bl_idname = "yakuza_cth.properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    ###
    @classmethod
    def poll(cls, context):
        return context.object is not None and type(context.object.data) is bpy.types.Mesh
    ###
    
    def draw(self, context):
        layout = self.layout

        props = context.object.data.cth_prop_grp
        
        ismesh_closed = layout.row()
        ismesh_closed.prop(props,"ismesh_closed")

        sort_mode = layout.row()
        sort_mode.label(text="Sort Mode: ")
        if props.sort_mode == 0: sort_translate = "AUTO"
        else: sort_translate = "MANUAL"
        sort_mode.prop(props,"sort_mode", text = sort_translate, toggle = True)

        origin = layout.row()
        origin.label(text="Origin Vector")
        vector = origin.box()
        vector.prop(props,"origin_X")
        vector.prop(props,"origin_Y")
        
        stiffness = layout.row()
        stiffness.prop(props,"stiffness")
        
        column = layout.row()
        column.prop(props,"column_count")
        
        row = layout.row()
        row.prop(props,"row_count")
        
        Vert_Expected = props.column_count * props.row_count
        Vert_Found = len(context.object.data.vertices)
        
        if Vert_Expected == Vert_Found: icon = 'NONE'
        else: icon = 'ERROR'
        
        vert_count = layout.row()
        vert_str = "Expected Vertices: {}"
        vert_count.label(text = vert_str.format(Vert_Expected))
        
        vert_found = layout.row()
        vert_str = "Found Vertices: {}"
        vert_found.label(text = vert_str.format(Vert_Found), icon = icon)

        pro_mode = layout.row()
        pro_mode.prop(props,"pro_mode")

        if props.pro_mode:
            pro_mode = layout.row()
            pro_mode.label(text = "TBA")
            '''
            if props.sort_mode == 4: Edges_Expected = props.column_count * (props.row_count - 1)
            elif props.sort_mode == 5: Edges_Expected = (props.column_count - 1) * props.row_count
            else: Edges_Expected = "NOT IN MANUAL MODE"
            Edges_Found = len(context.object.data.edges)
        
            if Edges_Expected == Edges_Found: icon = 'NONE'
            else: icon = 'ERROR'

            edge_count = layout.row()
            edge_str = "Expected Edges: {}"
            edge_count.label(text = edge_str.format(Edges_Expected))
            
            edge_found = layout.row()
            edge_str = "Found Edges: {}"
            edge_found.label(text = edge_str.format(Edges_Found), icon = icon)'''
    

class HCBArmaturePropertyGroup(bpy.types.PropertyGroup):
    unkfloat: bpy.props.FloatProperty(name="Unk Float")
    unkint: bpy.props.IntProperty(name="Unk Int", soft_min = 0)
    is_y5: bpy.props.BoolProperty(name="Yakuza 5 HCB")


class HCBArmaturePanel(bpy.types.Panel):
    bl_label = "HCB Armature Properties"
    bl_idname = "yakuza_hcb.armature.properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    ###
    @classmethod
    def poll(cls, context):
        return context.object is not None and type(context.object.data) is bpy.types.Armature
    ###
    
    def draw(self, context):
        layout = self.layout

        props = context.object.data.hcb_arm_prop_grp

        unkfloat = layout.row()
        unkfloat.prop(props,"unkfloat")

        unkint = layout.row()
        unkint.prop(props,"unkint")

        is_y5 = layout.row()
        is_y5.prop(props,"is_y5")

class HCBBonePropertyGroup(bpy.types.PropertyGroup):
    unkval1: bpy.props.IntProperty(name="Unk", soft_min = 0, soft_max = 255)
    unkval2: bpy.props.IntProperty(name="Unk", soft_min = 0, soft_max = 255)
    unkval3: bpy.props.IntProperty(name="Unk", soft_min = 0, soft_max = 255)
    unkval4: bpy.props.IntProperty(name="Unk", soft_min = 0, soft_max = 255)
    bone_parent1: bpy.props.StringProperty(name="Bone Constraint 1")
    bone_parent2: bpy.props.StringProperty(name="Bone Constraint 2")

class HCBBonePanel(bpy.types.Panel):
    bl_label = "HCB Bone Properties"
    bl_idname = "yakuza_hcb.bone.properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    ###
    @classmethod
    def poll(cls, context):
        return context.active_bone is not None ### add other condition be in Edit Mode
    ###
    
    def draw(self, context):
        layout = self.layout

        props = context.active_bone.hcb_bone_prop_grp

        unkbox = layout.row()#.box()
        unkbox.label(text="Unk Values")
        for i in range(1,5): unkbox.prop(props,"unkval" + str(i))

        radius = layout.row()
        radius.label(text="Head Radius")
        radius.prop(context.active_bone,"head_radius")
        radius.label(text="Tail Radius")
        radius.prop(context.active_bone,"tail_radius")

        bonpar = layout.row()
        #bonpar.label(text="Bone Constraint")
        bonpar.prop(props, "bone_parent1")

        if props.bone_parent2:
            bonpar = layout.row()
            #bonpar.label(text="Bone Constraint 2")
            bonpar.prop(props, "bone_parent2")