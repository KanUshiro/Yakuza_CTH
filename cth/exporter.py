import bpy
from yakuza_cth.BinaryReader.binary_reader import BinaryReader
from yakuza_cth.cth.functions import *
from yakuza_cth.hcb.exporter import *
import mathutils
import json
    
def CTH_Write_Exp_Data(directory): 
    armature = bpy.context.active_object
    fix_armature = False
    objs = []
    #hcbs = []

    for obj in bpy.data.objects:
        if obj.parent == armature:
            if obj.type == "MESH": objs.append(obj)
            elif obj.type == "ARMATURE": objs.append(obj)
        
    children = {}
    bones_buffer = []
    bones_append = []

    for x in armature.data.bones:
        append = False
        loc_child = []
        for z in x.children: loc_child.append(z)
        if len(loc_child) > 1: children[x] = loc_child
        
        ### FOR NEW BONES IG
        
        for z in x.items():
            if z == ('append', True):
                append = True
        
        if append: bones_append.append(x)
        else: bones_buffer.append(x)
        
        ###
        
    bones_buffer.extend(bones_append)

    b = BinaryReader()
    b.set_endian(True)
    b_skin = BinaryReader()
    b_skin.set_endian(True)
    rotscale = (0.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0)

    for x in bones_buffer:
        (parent, child, sibling) = (-1,-1,-1)
        
        if x.parent in children:
            for i in range(len(children[x.parent]) - 1):
                if children[x.parent][i] == x:
                    for j in range(len(bones_buffer)):
                        if bones_buffer[j] == children[x.parent][i+1]: sibling = j
        
        for i in range (len(bones_buffer)):
            if bones_buffer[i] == x.parent: parent = i
            elif x.children and bones_buffer[i] == x.children[0]: child = i
                
        relations = (parent, child, sibling)
        
        (X,Y,Z) = x.head_local
        if x.parent:
            X -= x.parent.head_local[0]
            Y -= x.parent.head_local[1]
            Z -= x.parent.head_local[2]
        
        head = (-X,Z,Y)
        
        Write_Str_Ch(x.name,b)
        b.write_int32(relations)
        b.pad(4)
        b.write_float(head)
        b.write_float(rotscale)
        
    bone_count = len(bones_buffer)
    
    for i in range(len(bones_buffer)): bones_buffer[i] = bones_buffer[i].name
    bones_buffer = tuple(bones_buffer)

    if bones_buffer[-3] != "skin":
        fix_armature = True
        bone_count += 3

    ### nodes

    obj_index = 0
    
    for obj in objs:
        
        if obj.type == "ARMATURE": HCB_Write_Exp_Data(directory,obj)

        else:
            name = obj.name
            if name[0] == "v" and name[2] == "_": name = name[3:]
            filepath = "{}v{}_{}.cth"
            f = open(filepath.format(directory, obj_index, name) , 'wb')
            obj_index += 1
            
            if fix_armature:

                Write_Str_Ch("skin",b_skin)
                b_skin.write_int32(-1)
                b_skin.write_int32(len(bones_buffer) + 1)
                b_skin.write_int32(-1)
                b_skin.pad(4)
                b_skin.write_float((0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0))

                Write_Str_Ch("l",b_skin)
                b_skin.write_int32(len(bones_buffer))
                b_skin.write_int32(len(bones_buffer) + 2)
                b_skin.write_int32(-1)
                b_skin.pad(4)
                b_skin.write_float((0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0))
            
                Write_Str_Ch(obj.name,b_skin)
                b_skin.write_int32(len(bones_buffer) + 1)
                b_skin.write_int32((-1,-1))
                b_skin.pad(4)
                b_skin.write_float((0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0))
            
            
            b.extend(b_skin.buffer())
            
            
            mesh = obj.to_mesh(preserve_all_data_layers = True)
            mesh.calc_tangents()
            props = mesh.cth_prop_grp
            origin = mathutils.Vector((props.origin_X,props.origin_Y))
            input_row = props.row_count
            input_column = props.column_count
            angle = []
            vertices = []
            mesh_row = []
            sorted_buffer = []

            groups = [i for i in range(len(obj.vertex_groups))]
            for group in obj.vertex_groups: groups[group.index] = group.name
            groups = tuple(groups)
            
            groups_indexed = []
            
            for group in groups:
                if group in bones_buffer: groups_indexed.append(bones_buffer.index(group))
                else: groups_indexed.append(-1)
            
            u = 0
            
            for x in mesh.vertices:
                vertex = []
                physic = (255,255,255)
                weights = []
                weights_i = []
                (X,Y,Z) = x.co
                pos = (-X,Z,Y)
                vertex.append(pos)
                
                
                for z in x.groups:
                    bone_index = groups_indexed[z.group]
                    
                    if bone_index == 0: physic = (int((1 - z.weight) * 255),int((1 - z.weight) * 255),int((1 - z.weight) * 255))
                    elif bone_index > 0: weights.append((z.weight, bone_index))
                    
                weights.sort()
                for i in range(len(weights) - 4): weights.pop(0)
                
                weights_removed = []
                
                for i in range(len(weights)):
                    if weights[i][0] > 0:
                        weights_removed.append(weights[i][0])
                        weights_i.append(weights[i][1])
                        
                normalized_weights = [float(i)/sum(weights_removed) for i in weights_removed]
                    
                vertex.append(physic)
                vertex.append(len(normalized_weights))
                vertex.append(normalized_weights)
                vertex.append(weights_i)
                vertices.append(vertex)
                mesh_row.append((Z,u))
                angle.append((origin.angle_signed(mathutils.Vector((X,Y))),u))
                
                u += 1

        ###############UV !!!

            index = []
            for x in mesh.polygons:
                for z in x.vertices: index.append(z)
                

            uv = []
            
            for x in mesh.uv_layers[0].uv:
                UV = (x.vector[0], 1 - x.vector[1])
                uv.append(UV)

            i = 0
            for x in mesh.uv_layers[0].uv:
                if len(vertices[index[i]]) < 8: vertices[index[i]].append(uv[i])
                i += 1

            ########## SORRING ALOGORITHM #####################################################################
            ##  idk ##

            resorted_buffer = []

            ### {AUTO}[BY_VERTICES] By Height
            ### deprecated
            '''
            if props.sort_mode == 2:

                mesh_row.sort(reverse=True)

                for i in range(len(mesh_row)): mesh_row[i] = mesh_row[i][1]

                for i in range(input_row):
                    row_sort = []
                    for u in range(input_column):
                        row_sort.append(angle[mesh_row[u + i * input_column]])
                    row_sort.sort(reverse = True)
                    
                    for u in range(len(row_sort)): sorted_buffer.append(row_sort[u][1])

                for i in range(input_column):
                    for u in range(input_row): resorted_buffer.append(sorted_buffer[u * input_column + i])

                first_row = sorted_buffer[:input_column]
            '''

            ### {AUTO}[BY_EDGES] By Height
            #elif props.sort_mode == 1:
            if props.sort_mode == 0:
                mesh_row.sort(reverse = True)
                for i in range(len(mesh_row)): mesh_row[i] = mesh_row[i][1]

                sorted = []
                for i in range(input_column): sorted.append(angle[mesh_row[i]])
                    
                sorted.sort(reverse = True)
                
                first_row = sorted
                
                for i in range(input_column): sorted[i] = sorted[i][1]

                for u in range(input_column):
                    start = sorted[u]
                    resorted_buffer.append(start)
                    for i in range(input_row - 1):
                        possibilities = []
                        for x in mesh.edges:
                            if x.vertices[0] == start and x.vertices[1] not in resorted_buffer: possibilities.append(x.vertices[1])
                            elif x.vertices[1] == start and x.vertices[0] not in resorted_buffer:possibilities.append(x.vertices[0])
                            
                        for l in range(len(possibilities)):
                            first_ver = mathutils.Vector(mesh.vertices[start].co[:2])
                            second_ver = mathutils.Vector(mesh.vertices[possibilities[l]].co[:2])
                            possibilities[l] = (first_ver.angle(second_ver),possibilities[l])
                            
                        possibilities.sort()
                        if len(possibilities) > 0:
                            start = possibilities[0][1]
                            resorted_buffer.append(possibilities[0][1])

            else: # if props.sort mode == 1:
                first_row = []
                for i in range (input_column):
                    first_row.append(i * input_row)

                resorted_buffer = [i for i in range(input_column * input_row)]

            
            ### {AUTO}[BY_VERTICES] By Angle ### shit method, doesn't work with normals
            ### deprecated
            '''
            elif props.sort_mode == 3:
                angle.sort(reverse = True)
                for i in range(len(angle)): angle[i] = angle[i][1]

                for i in range(input_row):
                    row_sort = []
                    for u in range(input_column):
                        row_sort.append(mesh_row[angle[u + i * input_column]])
                    row_sort.sort(reverse = True)
                    
                    for u in range(len(row_sort)): resorted_buffer.append(row_sort[u][1])
                    # ^^^ this works on dante i think. not on majima though.
            '''

            ###################################################################################################

            w = BinaryReader()
            w.set_endian(True)

            for z in resorted_buffer:
                x = vertices[z]
                w.write_float(x[0])
                w.pad(12)
                w.write_uint8(x[1])
                w.write_uint8(255)
                w.write_uint32(x[2])
                
                for i in range(x[2]):
                    w.write_float(x[3][i])
                    w.write_uint32(x[4][i])
                    
                for i in range(4 - x[2]): w.pad(8)
                    
                for i in range(5,len(x)):
                    w.write_float(x[i])
                    w.pad(24)
                    
                for r in range(9 - len(x)):
                    w.write_float(x[5])
                    w.pad(24)
                    
                    
            ### material ### credits again to TheTurboTurnip for yakuza materials
            ### in case of incompatibility with different versions of gmd addon, errors will always/only be caused by the materials. rest is exclusive to cth addon
            
            m = BinaryReader()
            m.set_endian(True)
            
            mat = obj.material_slots[0].material
            textures = {}
            tex_names = []
            
            for x in mat.node_tree.links:
                tex_slot = x.to_socket.name
                if "texture" in tex_slot and x.from_node.image:
                    tex_name = x.from_node.image.name
                    if "." in tex_name[-4:]: tex_name = tex_name[:tex_name.rindex(".")]
                    
                    if tex_name not in tex_names: tex_names.append(tex_name)
                    
                    textures[tex_slot] = tex_names.index(tex_name)
                        
            tex_count = len(tex_names)
            
            Write_Str_Ch(mat.yakuza_data.shader_name,m)
            
            m.write_uint16((TexToID(textures,"texture_diffuse"),TexToID(textures,"texture_refl"),TexToID(textures,"texture_multi"),TexToID(textures,"texture_unk1"),TexToID(textures,"texture_rs"),TexToID(textures,"texture_normal"),TexToID(textures,"texture_rt"),TexToID(textures,"texture_rd")))

            data_json = json.loads(mat.yakuza_data.material_json)
            
            m.write_uint8(tuple(data_json["unk1"] + data_json["specular"] + [data_json["padding"]] + data_json["diffuse"] + [data_json["opacity"]] + data_json["unk2"]))
            m.write_float(mat.yakuza_data.attribute_set_floats)
            m.write_float(mat.yakuza_data.unk12[:16])
            
            for x in tex_names: Write_Str_Ch(x,m)
            
            ### normals, tangents
            ### they are only stored for the highest row of vertices apparently
            ### check if there is a way to make it read more rows
            ### i still dont understand what they are but they are seemingly exported with same numbers as vanilla
            
            shblend = BinaryReader()
            shblend.set_endian(True)
            
            
            if len(mesh.loops) > 0 and first_row:
                for x in first_row:
                    (X,Y,Z) = tuple(mesh.vertices[x].normal)
                    shblend.write_float((-X,Z,Y,0))

                i = 0
                while i < len(first_row):
                    for x in mesh.loops:
                        if i >= len(first_row): break;
                        if x.vertex_index == first_row[i]:
                            (X,Y,Z) = x.tangent
                            shblend.write_float((-X,Z,Y,0))
                            i += 1

            else:
                for i in range(input_column * 2):
                    blend_values_placeholder = (1.0,1.0,1.0,0.0)
                    shblend.write_float(blend_values_placeholder)
            
            ####
            
            tex_pointer = 256
            node_count = bone_count
            node_pointer = tex_pointer + tex_count * 32
            vertex_pointer = node_pointer + b.size()
            blend1_pointer = vertex_pointer + input_row * input_column * 192
            blend2_pointer = blend1_pointer + input_column * 16
            size = blend2_pointer + input_column * 16

            ### h is after ALL blocks (header)
            h = BinaryReader()
            h.set_endian(True)
            
            h.write_str("CTH1")
            h.write_bytes(b'\x02\x01\x00\x00\x00\x00\x00\x03')
            h.write_uint32(size)
            h.write_uint8(255 - props.stiffness)
            h.write_uint8(props.ismesh_closed)
            h.pad(2)
            h.write_uint16(input_column)
            h.write_uint16(input_row)
            h.write_uint32(tex_count)
            h.write_uint32(tex_pointer)
            h.write_uint32(node_count)
            h.write_uint32(node_pointer)
            h.write_uint32(input_column * input_row)
            h.write_uint32(vertex_pointer)
            h.write_uint32(input_column) ### may be supported to have different amounts
            h.write_uint32(blend1_pointer)
            h.write_uint32(input_column) ### may be supported to have different amounts
            h.write_uint32(blend2_pointer)
            
            ###
            
            w.extend(shblend.buffer())
            
            f.write(h.buffer())
            f.write(m.buffer())
            f.write(b.buffer())
            f.write(w.buffer())

            f.close()