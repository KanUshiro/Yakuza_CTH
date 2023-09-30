import bpy
import importlib.util
import os
from yakuza_cth.cth.classes import *
from yakuza_cth.cloth_preset.Yakuza_CTH import Yakuza_CTH_preset

blender_loader = importlib.util.find_spec('bpy')

# Include the bl_info at the top level always
bl_info = {
    "name": "Yakuza CTH File Import/Export",
    "author": "Kan",
    "version": (0, 1, 1),
    "blender": (3, 5, 1),
    "location": "File > Import-Export",
    "description": "Import-Export Yakuza CTH Files",
    "warning": "Yakuza GMD add-on by TheTurboTurnip required",
    "doc_url": "",
    "category": "Import-Export",
}

classes = (
    ImportCTH,
    ExportCTH,
    CTHPropertyGroup,
    CTHPanel,
    HCBArmaturePropertyGroup,
    HCBArmaturePanel,
    HCBBonePropertyGroup,
    HCBBonePanel
    )

functions = (
    CTH_Write_Imp_Data,
    HCB_Write_Imp_Data,
    Checksum,
    Write_Str_Ch,
    TexToID,
    CTH_Write_Exp_Data,
    CTH_Import_File,
    CTH_Export_File
)

def menu_func_import_cth(self, context):
     self.layout.operator(ImportCTH.bl_idname, text="Yakuza CTH/HCB [Cloth Physics/Collision] (.cth/.hcb)")

def menu_func_export_cth(self, context):
    self.layout.operator(ExportCTH.bl_idname, text="Yakuza CTH [Cloth Physics] (.cth)")
    
def register():
    for c in classes: bpy.utils.register_class(c)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_cth)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_cth)
    bpy.types.Mesh.cth_prop_grp = bpy.props.PointerProperty(type=CTHPropertyGroup)
    bpy.types.Armature.hcb_arm_prop_grp = bpy.props.PointerProperty(type=HCBArmaturePropertyGroup)
    bpy.types.EditBone.hcb_bone_prop_grp = bpy.props.PointerProperty(type=HCBBonePropertyGroup)

    ###

    bpy.types.Bone.hcb_bone_prop_grp = bpy.props.PointerProperty(type=HCBBonePropertyGroup)

    ###

    userpath = bpy.utils.resource_path(type='USER')
    clothpath = None
    for x in bpy.utils.preset_paths("cloth"):
        if userpath in x:
            clothpath = x
        
    if not clothpath:
        for x in bpy.utils.preset_paths(""):
            if userpath in x:
                clothpath = os.path.join(x,"cloth")
                os.mkdir(clothpath)
                
    if not clothpath:
        clothpath = os.path.join(userpath,"scripts/addons/presets/cloth")
        os.makedirs(clothpath, exist_ok=True)

    yakuza_cth_preset = os.path.join(clothpath,"Yakuza_CTH.py")
    if not os.path.isfile(yakuza_cth_preset):
        preset_file = open(yakuza_cth_preset,"wt")
        preset_file.write(Yakuza_CTH_preset)
        preset_file.close()

    bpy.utils.refresh_script_paths()

def unregister():
    for c in classes: bpy.utils.unregister_class(c)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_cth)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_cth)
    del bpy.types.Mesh.cth_prop_grp
    del bpy.types.Armature.hcb_arm_prop_grp
    del bpy.types.EditBone.hcb_bone_prop_grp
    for x in functions: del x
    

    userpath = bpy.utils.resource_path(type='USER')
    clothpath = None
    for x in bpy.utils.preset_paths("cloth"):
        if userpath in x:
            clothpath = x
    
    if clothpath:
        yakuza_cth_preset = os.path.join(clothpath,"Yakuza_CTH.py")
        if os.path.exists(yakuza_cth_preset):
            os.remove(yakuza_cth_preset)