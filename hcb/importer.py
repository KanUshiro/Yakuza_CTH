#from bpy import context
import bpy

def HCB_Write_Imp_Data(filename, filedir, r):

    #props_cache = []
    arm_hook_obj = bpy.context.object
    armature_hook = bpy.context.object.data

    for x in bpy.data.collections:
        for z in x.objects:
            if z == arm_hook_obj:
                collection = x

    bpy.ops.object.armature_add(False, enter_editmode = True)

    armature_obj = bpy.context.active_object
    armature = armature_obj.data

    armature.name = filename
    armature.display_type = 'ENVELOPE'

    armature_obj.name = filename
    for x in armature_obj.users_collection: x.objects.unlink(armature_obj)

    collection.objects.link(armature_obj)
    armature_obj.parent = arm_hook_obj

    props = armature.hcb_arm_prop_grp

    r.seek(16)

    bonecount = r.read_uint32()

    ## next 2 values: little endian in y5

    props.unkfloat = r.read_float()
    props.unkint = r.read_uint32()

    if props.unkint > 150000:
        r.seek(20)
        r.set_endian(False)
        props.unkfloat = r.read_float()
        props.unkint = r.read_uint32()
        r.set_endian(True)
        
        props.is_y5 = True

    r.seek(4,1)

    bone = armature.edit_bones
    bone.remove(bone[0])
    bones = []
    unkvals = []

    for i in range(bonecount):
        type = r.read_uint32()
        nodesize = r.read_uint32()

        unkvals = r.read_uint8(4)

        unk1 = r.read_uint32()
        
        bonename = r.read_str(16)
        bonename2 = None

        if type == 1: bonename2 = r.read_str(16)
        
        (X1,Y1,Z1,W1) = r.read_float(4)
        (BX1, BY1, BZ1) = armature_hook.bones[bonename].head_local
        (X1,Y1,Z1) = (-X1 + BX1, Z1 + BY1, Y1 + BZ1)
        
        bone.new(bonename)
        
        boneprops = bone[i].hcb_bone_prop_grp

        (boneprops.unkval1, boneprops.unkval2, boneprops.unkval3, boneprops.unkval4) = unkvals
        
        boneprops.bone_parent1 = bonename

        if bonename2 and bonename2 != bonename: boneprops.bone_parent2 = bonename2

        bone[i].head = (X1,Y1,Z1)
        bone[i].head_radius = W1
        bone[i].envelope_distance = 0
        
        if type > 0:
            (X2,Y2,Z2,W2) = r.read_float(4)
            
            (BX2, BY2, BZ2) = armature_hook.bones[bonename2 if bonename2 else bonename].head_local
            (X2,Y2,Z2) = (-X2 + BX2, Z2 + BY2, Y2 + BZ2)
            bone[i].tail = (X2,Y2,Z2)
            bone[i].tail_radius = W2
            
        else:
            bone[i].tail = (X1, Y1, Z1 + 0.0001)
            bone[i].tail_radius = 0
            
            
        if bone[i].head == bone[i].tail:
            bone[i].tail = (X1, Y1, Z1 + 0.0001)

        bones.append((bonename,bonename2))

        ###

        #props_cache.append(boneprops)
        #armature.bones[i].hcb_bone_prop_grp = boneprops
        ###

    bpy.ops.object.mode_set(False,mode='POSE')

    for i,x in enumerate(bpy.context.visible_pose_bones):
        constraint = x.constraints.new('ARMATURE')
        target = constraint.targets.new()
        target.target = arm_hook_obj
        target.subtarget = bones[i][0]
        
        if bones[i][1] and bones[i][1] != bones[i][0]:
            target.weight = 0.5
            
            target2 = constraint.targets.new()
            target2.target = arm_hook_obj
            target2.subtarget = bones[i][1]
            target2.weight = 0.5


        ###

        #armature.bones[i].hcb_bone_prop_grp = props_cache[i]

        ###

    bpy.ops.object.mode_set(False,mode='OBJECT')

'''
    for i,x in enumerate(bones):
        boneprops = armature.bones[x[0]].hcb_bone_prop_grp

        (boneprops.unkval1, boneprops.unkval2, boneprops.unkval3, boneprops.unkval4) = unkvals[i]'''