from yakuza_cth.BinaryReader.binary_reader import BinaryReader
from yakuza_cth.cth.importer import *
from yakuza_cth.hcb.importer import *
import os

def CTH_Import_File(filepath):
    file = open(filepath,"rb")
    filename = os.path.basename(filepath)
    filedir = filepath[:len(filename)]
    filename = filename[:filename.rindex(".")]
    r = BinaryReader(file.read())
    r.set_endian(True)
    file.close()

    magic = r.read_str(4)

    if magic == "CTH1":
        CTH_Write_Imp_Data(filename, filedir, r)
    
    elif magic == "hitc":
        HCB_Write_Imp_Data(filename, filedir, r)
    
    else:
        raise Exception("File format unrecognized.")

def CTH_Export_File(filepath):
    pass