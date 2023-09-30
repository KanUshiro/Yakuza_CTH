Yakuza_CTH_preset = '''import bpy
cloth = bpy.context.cloth

cloth.settings.quality = 80
cloth.settings.mass = 0.30000001192092896
cloth.settings.air_damping = 1.0
cloth.settings.bending_model = 'ANGULAR'
cloth.settings.tension_stiffness = 15.0
cloth.settings.compression_stiffness = 15.0
cloth.settings.shear_stiffness = 5.0
cloth.settings.bending_stiffness = 0.5
cloth.settings.tension_damping = 5.0
cloth.settings.compression_damping = 5.0
cloth.settings.shear_damping = 5.0
cloth.settings.bending_damping = 0.5
'''