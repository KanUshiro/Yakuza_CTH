def Checksum(name):
    checksum = 0
    for x in name.encode('utf-8'): checksum += x
    return checksum

def Write_Str_Ch(name,buffer):
    buffer.write_uint16(Checksum(name))
    buffer.write_str_fixed(name,30)

def TexToID(dict,type):
    if type not in dict: return 0
    else: return dict[type]