import bpy
import bmesh
from bpy import context
from yakuza_cth.BinaryReader.binary_reader import BinaryReader
from yk_gmd_blender.blender.materials import *
#from yk_gmd_blender.blender.importer.scene_creators.base import *
from yk_gmd_blender.yk_gmd.v2.abstract.gmd_attributes import *
from yk_gmd_blender.yk_gmd.v2.abstract.gmd_shader import *
from yk_gmd_blender.yk_gmd.v2.structure.version import GMDVersion
#from bpy.props import FloatVectorProperty, StringProperty, BoolProperty, IntProperty
from bpy.types import NodeSocket, NodeSocketColor, ShaderNodeTexImage, \
    PropertyGroup
import json
import re
#import os
from typing import Optional, Tuple, cast

def CTH_Write_Imp_Data(filename, filedir, r): 
    def make_cth_material(collection: bpy.types.Collection, gmd_attribute_set: GMDAttributeSet) -> bpy.types.Material: ###(self, collection: bpy.types.Collection, gmd_attribute_set: GMDAttributeSet) -> bpy.types.Material:
            ### i stole turnip's code hi turnip ily
            
            """
            Given a gmd_attribute_set, make a Blender material.
            The material name is based on the collection name NOT the gmd_scene name, in case duplicate scenes exist.
            i.e. if c_am_kiryu is imported twice, the second collection will be named c_am_kiryu.001.
            For consistency, the materials can take this c_am_kiryu.001 as a prefix.
            :param collection: The collection the scene is associated with.
            :param gmd_attribute_set: The attribute set to create a material for.
            :return: A Blender material with all of the data from the gmd_attribute_set represented in an exportable way.
            """
            ####### not needed cuz cth is 1 mat only
            # If the attribute set has a material already, reuse it.
            #if id(gmd_attribute_set) in self.material_id_to_blender:
            #    return self.material_id_to_blender[id(gmd_attribute_set)]
            ####### 

            def make_yakuza_cth_node_group(node_tree: bpy.types.NodeTree):
                node = node_tree.nodes.new("ShaderNodeGroup")
                node.node_tree = get_yakuza_shader_node_group()
                return node
            
            material_name = f"{collection.name_full}_{gmd_attribute_set.texture_diffuse or 'no_tex'}"

            material = bpy.data.materials.new(material_name)
            # Yakuza shaders all use backface culling (even the transparent ones!) # not in cth
            #material.use_backface_culling = True
            # They all have to use nodes, of course
            material.use_nodes = True
            # Don't use the default node setup
            material.node_tree.nodes.clear()
            # Make a Yakuza Shader group, and position it
            yakuza_shader_node_group = make_yakuza_cth_node_group(material.node_tree)
            yakuza_shader_node_group.location = (0, 0)
            yakuza_shader_node_group.width = 400
            yakuza_shader_node_group.height = 800
            # Hook up the Yakuza Shader to the output
            output_node = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
            output_node.location = (500, 0)
            material.node_tree.links.new(yakuza_shader_node_group.outputs["Shader"], output_node.inputs["Surface"])

            yakuza_inputs = yakuza_shader_node_group.inputs
            # Set up the group inputs and material data based on the attribute set.
            '''set_yakuza_shader_material_from_attributeset(
                material,
                yakuza_shader_node_group.inputs,
                gmd_attribute_set,
                os.path.dirname(filedir)
            )'''
            material.yakuza_data.inited = True
            material.yakuza_data.shader_name = gmd_attribute_set.shader.name
            material.yakuza_data.attribute_set_flags = f"{gmd_attribute_set.attr_flags:016x}"
            material.yakuza_data.unk12 = gmd_attribute_set.unk12.float_data if gmd_attribute_set.unk12 else [0] * 32
            material.yakuza_data.unk14 = gmd_attribute_set.unk14.int_data if gmd_attribute_set.unk14 else [0] * 32
            material.yakuza_data.attribute_set_floats = gmd_attribute_set.attr_extra_properties
            material.yakuza_data.material_origin_type = gmd_attribute_set.material.origin_version.value
            material.yakuza_data.material_json = json.dumps(vars(gmd_attribute_set.material.origin_data))

            # Set the skin shader to 1 if the shader is a skin shader
            yakuza_inputs["Skin Shader"].default_value = 1.0 if "[skin]" in gmd_attribute_set.shader.name else 0.0

            # Convenience function for creating a texture node for an Optional texture
            def set_texture(set_into: NodeSocketColor, tex_name: Optional[str],
                            next_image_y: int = 0, color_if_not_found=(1, 0, 1, 1)) -> Tuple[Optional[ShaderNodeTexImage], int]:
                if not tex_name:
                    return None, next_image_y
                image_node = load_texture_from_name(material.node_tree, filedir, tex_name, color_if_not_found)
                image_node.location = (-500, next_image_y)
                # image_node.label = tex_name
                image_node.hide = True
                material.node_tree.links.new(image_node.outputs["Color"], set_into)
                next_image_y -= 100
                return image_node, next_image_y

            # Create the diffuse texture
            diffuse_tex, next_y = set_texture(yakuza_inputs["texture_diffuse"], gmd_attribute_set.texture_diffuse)
            if diffuse_tex and re.search(r'^s_b', gmd_attribute_set.shader.name):
                # The shader name starts with s_b so we know it's transparent
                # Link the texture alpha with the Yakuza Shader, and make the material do alpha blending.
                material.node_tree.links.new(diffuse_tex.outputs["Alpha"], yakuza_inputs["Diffuse Alpha"])
                material.blend_method = "BLEND"
            # Attach the other textures.
            _, next_y = set_texture(yakuza_inputs["texture_multi"], gmd_attribute_set.texture_multi, next_y, DEFAULT_MULTI_COLOR)
            _, next_y = set_texture(yakuza_inputs["texture_normal"], gmd_attribute_set.texture_normal, next_y, DEFAULT_NORMAL_COLOR)
            _, next_y = set_texture(yakuza_inputs["texture_refl"], gmd_attribute_set.texture_refl, next_y)
            _, next_y = set_texture(yakuza_inputs["texture_unk1"], gmd_attribute_set.texture_unk1, next_y)
            _, next_y = set_texture(yakuza_inputs["texture_rs"], gmd_attribute_set.texture_rs, next_y)
            _, next_y = set_texture(yakuza_inputs["texture_rt"], gmd_attribute_set.texture_rt, next_y)
            _, next_y = set_texture(yakuza_inputs["texture_rd"], gmd_attribute_set.texture_rd, next_y)



            #self.material_id_to_blender[id(gmd_attribute_set)] = material
            return material

    # file = open(filepath,"rb")
    # filename = os.path.basename(filepath)
    # filedir = filepath[:len(filename)]
    # filename = filename[:filename.rindex(".")]
    # r = BinaryReader(file.read())
    # r.set_endian(True)
    # file.close()

    # assert r.read_str(4) == "CTH1"

    newmesh = bpy.data.meshes.new('newmesh')
    bm = bmesh.new()

    physics_on = True # user choice

    ### header ###

    r.seek(16)

    stiffness = r.read_uint8()
    closed_mesh = r.read_uint8()
    hpad = r.read_uint16()
    column_read = r.read_uint16()
    row_read = r.read_uint16()
    texturecount = r.read_uint32()
    texturepointer = r.read_uint32()
    nodecount = r.read_uint32()
    nodepointer = r.read_uint32()
    vertexcount = r.read_uint32()
    vertexpointer = r.read_uint32()
    shadingcount1 = r.read_uint32()
    shadingpointer1 = r.read_uint32()
    shadingcount2 = r.read_uint32()
    shadingpointer2 = r.read_uint32()

    ### material ###


    #newmat = bpy.data.materials.new("Material")

    r.seek(66)

    shadername = r.read_str(30)

    #newmat.yakuza_data.inited = True
    #newmat.yakuza_data.shader_name = shadername

    # textures
    di = r.read_uint16()
    refl = r.read_uint16()
    mt = r.read_uint16()
    sp = r.read_uint16()
    rs = r.read_uint16()
    tn = r.read_uint16()
    rt = r.read_uint16()
    rd = r.read_uint16()

    uvprimary = bm.loops.layers.uv.new("UV_Primary")
    uv_lay = bm.loops.layers.uv["UV_Primary"]

    #newmat.use_nodes

    # yakuza numba
    cunk1 = r.read_uint8(4)
    spec = r.read_uint8(3)
    pad = r.read_uint8()
    diffuse = r.read_uint8(3)
    opac = r.read_uint8()
    cunk2 = r.read_uint8(4)

    # attribute set floats

    atsetfloat1 = r.read_float(16)
    atsetfloat2 = r.read_float(16)

    for x in range(16): atsetfloat2 += (0.0,)

    # texture names

    r.seek(texturepointer)
    texturenames = []
    for i in range(texturecount):
        r.seek(2,1)
        texturename = r.read_str(30)
        texturenames.append(texturename)
        
    ### nodes/bones ###

    r.seek(nodepointer)

    collection = bpy.data.collections.new(filename)
    bpy.ops.object.armature_add(False, enter_editmode = True)

    armature_obj = bpy.context.active_object
    armature = armature_obj.data

    armature.name = filename
    armature.display_type = 'STICK'


    armature_obj.show_in_front = True
    armature_obj.name = filename

    #### displaced to after ops for violet error (?)
    #for x in armature_obj.users_collection: x.objects.unlink(armature_obj)
    #collection.objects.link(armature_obj)
    #collection_l = bpy.context.scene.collection.children.link(collection)

    bonenames = []
    
    bone = armature.edit_bones
    bone.remove(bone[0])
    
    for i in range(nodecount): # -3?
        r.seek(2,1)
        bonename = r.read_str(30)
        bonenames.append(bonename)
        bone.new(bonename)
        parentindex = r.read_int32()
        childindex = r.read_int32()
        siblingindex = r.read_int32()
        shallbeunused = r.read_int32()
        
        (localx,localy,localz,localw) = r.read_float(4)
        localpos = (-localx,localz,localy)
        
        localrot = r.read_float(4)
        localscale = r.read_float(4)
        
        blenderisshit = (-localx + 0.0001,localz,localy)
        
        bone[i].tail = localpos
        bone[i].head = blenderisshit
        bone[i].use_relative_parent = True
        
        if parentindex > -1:
            bone[i].parent = bone[parentindex]
            bone[i].translate(bone[parentindex].tail)
            
    bpy.ops.object.mode_set(False,mode='OBJECT')

    for x in armature_obj.users_collection: x.objects.unlink(armature_obj)
    collection.objects.link(armature_obj)
    collection_l = bpy.context.scene.collection.children.link(collection)
                
    ###############


    
    ### vertices ###

    r.seek(vertexpointer)

    bmvertsbuffer = []
    bmuvbuffer = []
    vertsweights = []
    vertsbonemap = []
    physics = []
    for i in range(vertexcount):
        x = r.read_float()
        y = r.read_float()
        z = r.read_float()
        pos = (-x,z,y)
        maybetheyrenormals = r.read_float(3)
        physics_pin = r.read_uint8()
        physics_ff = r.read_uint8(3)
        physics.append(1 - physics_pin * 1/255)
        bonecollicount = r.read_uint32() # maybe rename later but this is just normal weights
        bonecolli = []
        boneindex = []
        for u in range(bonecollicount):
            bonecolli.append(r.read_float())
            boneindex.append(r.read_int32())
        vertsweights.append(bonecolli)
        vertsbonemap.append(boneindex)
        r.seek((4 - bonecollicount) * 8 , 1)

        (x0,y0) = r.read_float(2)
        r.seek(24,1)
        
        (x1,y1) = r.read_float(2)
        r.seek(24,1)
        
        (x2,y2) = r.read_float(2)
        r.seek(24,1)
        
        (x3,y3) = r.read_float(2)
        r.seek(24,1)
        
        ############ FLIP UV MAP TODO
        
        bmuvbuffer.append([(x0,1-y0),(x1,1-y1),(x2,1-y2),(x3,1-y3)])
        bmvertsbuffer.append(bm.verts.new(pos))


    ### faces ###

    # generate basic faces & uv (very sharp and ugly)

    for u in range(column_read - 1):
        for i in range(row_read - 1):
            ff = bm.faces.new(( bmvertsbuffer[i + u * row_read] , bmvertsbuffer[i + 1 + u * row_read] , bmvertsbuffer[i + row_read + 1 + u * row_read] , bmvertsbuffer[i + row_read + u * row_read]))
            ff.loops[0][uv_lay].uv = bmuvbuffer[i + u * row_read][3]
            ff.loops[1][uv_lay].uv = bmuvbuffer[i + 1 + u * row_read][2]
            ff.loops[2][uv_lay].uv = bmuvbuffer[i + row_read + 1 + u * row_read][0]
            ff.loops[3][uv_lay].uv = bmuvbuffer[i + row_read + u * row_read][1]

    if closed_mesh:
        for i in range(row_read - 1):
            ff = bm.faces.new(( bmvertsbuffer[i + ((column_read - 1)* row_read)] , bmvertsbuffer[i + ((column_read - 1)* row_read) + 1]  , bmvertsbuffer[i + 1] , bmvertsbuffer[i]))
            ff.loops[0][uv_lay].uv = bmuvbuffer[i + ((column_read - 1)* row_read)][3]
            ff.loops[1][uv_lay].uv = bmuvbuffer[i + ((column_read - 1)* row_read) + 1][2]
            ff.loops[2][uv_lay].uv = bmuvbuffer[i + 1][0]
            ff.loops[3][uv_lay].uv = bmuvbuffer[i][1]
            

    bm.faces.ensure_lookup_table()

    # beautify faces, calculate normals, shade smooth (america's next top model beauty standards)

    beauty = bmesh.ops.beautify_fill(bm, faces = bm.faces, edges = bm.edges, method = "ANGLE")

    beautiful_faces = [ele for ele in beauty['geom']
                    if isinstance(ele, bmesh.types.BMFace)]
    beautiful_edges = [ele for ele in beauty['geom']
                    if isinstance(ele, bmesh.types.BMEdge)]
                    
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    for x in beautiful_faces: bm.faces[x.index].copy_from(x)
        
    for x in beautiful_edges: bm.edges[x.index].copy_from(x)

    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)

    for i in range(len(bm.faces)): bm.faces[i].smooth = True

    bm.to_mesh(newmesh)
    
    cthshader = GMDShader(name = shadername,assume_skinned = True, vertex_buffer_layout = GMDVertexBufferLayout(
            assume_skinned = True,
            pos_unpacker = BaseUnpacker[Vector],
            weights_unpacker = Optional[BaseUnpacker[Vector]],
            bones_unpacker = Optional[BaseUnpacker[Vector]],
            normal_unpacker = Optional[BaseUnpacker[Vector]],
            tangent_unpacker = Optional[BaseUnpacker[Vector]],
            unk_unpacker = Optional[BaseUnpacker[Vector]],
            col0_unpacker = Optional[BaseUnpacker[Vector]],
            col1_unpacker = Optional[BaseUnpacker[Vector]],
            uv_unpackers = Tuple[BaseUnpacker[Vector], ...],

            pos_storage = VecStorage,
            weights_storage = Optional[VecStorage],
            bones_storage = Optional[VecStorage],
            normal_storage = Optional[VecStorage],
            tangent_storage = Optional[VecStorage],
            unk_storage = Optional[VecStorage],
            col0_storage = Optional[VecStorage],
            col1_storage = Optional[VecStorage],
            uv_storages = Tuple[VecStorage, ...],
            packing_flags = 0
            ))
        
    cthmaterial = GMDMaterial(
        origin_version = GMDVersion(3),
        origin_data = MaterialStruct_YK1(
            diffuse = list(diffuse),
            opacity = opac,
            specular = spec,
            unk1 = list(cunk1),
            unk2 = list(cunk2),)
        )
        

    cthset = GMDAttributeSet(
        shader = cthshader,

        texture_diffuse = texturenames[di],
        texture_refl = texturenames[refl],
        texture_multi = texturenames[mt],
        texture_unk1 = texturenames[sp],
        texture_rs = texturenames[rs],
        texture_normal = texturenames[tn],
        texture_rt = texturenames[rt],
        texture_rd = texturenames[rd],

        material = cthmaterial,
        unk12 = GMDUnk12(float_data = atsetfloat2),
        unk14 = GMDUnk14(int_data = [0]*32),
        attr_extra_properties = atsetfloat1,
        attr_flags = 0
        )


    newmat = make_cth_material(collection = collection, gmd_attribute_set = cthset)
    newmesh.materials.append(newmat)

    #######################

    newobject = bpy.data.objects.new(bonenames[-1], newmesh)

    newobject.parent = armature_obj#bpy.context.active_object

    ############# ADD MATERIALS TODO

    #######################
    ### VERTEX GROUPS ? ###
    #######################

    for i in range(nodecount): newobject.vertex_groups.new(name=bonenames[i])
        
    for i in range(vertexcount):
        # physics
        newobject.vertex_groups[0].add(index = [i], weight = physics[i], type = 'ADD')
        
        # bone weights
        listofbones = vertsbonemap[i]
        numberofbones = len(listofbones)
        boneweights = vertsweights[i]
        for a in range(numberofbones):
            boneindex = listofbones[a]
            newobject.vertex_groups[boneindex].add(index = [i], weight = boneweights[a], type = 'ADD')

    #######################

    modifier = newobject.modifiers.new(armature.name,type='ARMATURE')
    modifier.object = armature_obj

    if physics_on == True: cloth_modifier = newobject.modifiers.new(name='Cloth',type='CLOTH')
    s = cloth_modifier.settings

    s.use_internal_springs = True
    s.quality = 80
    s.vertex_group_mass = bonenames[0]
    s.pin_stiffness = 10
    s.use_dynamic_mesh = True
    s.internal_compression_stiffness = 1
    s.internal_compression_stiffness_max = 1

    props = newobject.data.cth_prop_grp

    props.ismesh_closed = closed_mesh
    props.stiffness = 255 - stiffness
    props.column_count = column_read
    props.row_count = row_read


    collection.objects.link(newobject)