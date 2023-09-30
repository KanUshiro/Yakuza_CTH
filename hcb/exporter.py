#from binary_reader import BinaryReader ####for vs code purposesnot blender!!!
from yakuza_cth.BinaryReader.binary_reader import BinaryReader

def HCB_Write_Exp_Data(directory,obj): ## check what inputs need later andconnect the shit n all

    #name = obj.name
    #filepath = obj.name
    f = open(directory + obj.name + ".hcb" , 'wb')

    w = BinaryReader()
    w.set_endian(True)
    w.write_bytes(b'\x68\x69\x74\x63\x02\x01\x00\x00\x0B\x00\x01\x00\x00\x00\x00\x00')

    armature = obj.data
    bonecount = len(armature.bones)
    props = armature.hcb_arm_prop_grp

    w.write_uint32(bonecount)

    if props.is_y5: w.set_endian(False)

    w.write_float(props.unkfloat)
    w.write_uint32(props.unkint)

    if props.is_y5: w.set_endian(True)

    w.pad(4)

    for i,x in enumerate(armature.bones):
        ## type 0 : only 1 bone 1 coordinates
        ## type 1: 2 bones 2 coordinates
        ## type 2: 1 bone 2 coordinates
        ## => learn more about type 0 and cover it later ig

        boneprops = x.hcb_bone_prop_grp
        bone1 = obj.parent.data.bones[boneprops.bone_parent1]

        btype = 2 ## change later for type 0 too
        bsize = 64 ##
        if boneprops.bone_parent2:
            btype = 1
            bsize = 80
            bone2 = obj.parent.data.bones[boneprops.bone_parent2]

        w.write_uint32((btype,bsize))
        w.write_uint8((boneprops.unkval1,boneprops.unkval2,boneprops.unkval3,boneprops.unkval4))
        w.pad(4) ## ?
        w.write_str_fixed(bone1.name,16)
        if boneprops.bone_parent2: w.write_str_fixed(bone2.name,16)

        (X1, Y1, Z1) = tuple(x.head_local)
        (X2, Y2, Z2) = tuple(bone1.head_local)

        W1 = x.head_radius

        w.write_float(( -(X1 - X2), Z1 - Z2, Y1 - Y2, W1))

            
        (X1, Y1, Z1) = tuple(x.tail_local)
        
        if boneprops.bone_parent2: (X2, Y2, Z2) = tuple(bone2.head_local)
        else: (X2, Y2, Z2) = tuple(bone1.tail_local)

        W1 = x.tail_radius

        w.write_float(( -(X1 - X2), Z1 - Z2, Y1 - Y2, W1))



    f.write(w.buffer())
    f.close()