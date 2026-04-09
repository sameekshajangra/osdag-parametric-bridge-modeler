from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

def create_i_section(d, bf, tf, tw, length):
    """
    Creates a 3D model of an I-section beam.
    Coordinates: X is longitudinal (length).
    """
    web_height = d - 2 * tf
    
    # Bottom Flange
    bot_flange = BRepPrimAPI_MakeBox(length, bf, tf).Shape()
    trsf_bot = gp_Trsf()
    trsf_bot.SetTranslation(gp_Vec(0, -bf/2, 0))
    bot_flange = BRepBuilderAPI_Transform(bot_flange, trsf_bot, True).Shape()
    
    # Web
    web = BRepPrimAPI_MakeBox(length, tw, web_height).Shape()
    trsf_web = gp_Trsf()
    trsf_web.SetTranslation(gp_Vec(0, -tw/2, tf))
    web = BRepBuilderAPI_Transform(web, trsf_web, True).Shape()
    
    # Top Flange
    top_flange = BRepPrimAPI_MakeBox(length, bf, tf).Shape()
    trsf_top = gp_Trsf()
    trsf_top.SetTranslation(gp_Vec(0, -bf/2, d - tf))
    top_flange = BRepBuilderAPI_Transform(top_flange, trsf_top, True).Shape()
    
    # Fuse components
    girder = BRepAlgoAPI_Fuse(bot_flange, web).Shape()
    girder = BRepAlgoAPI_Fuse(girder, top_flange).Shape()
    
    return girder

if __name__ == "__main__":
    from OCC.Display.SimpleGui import init_display
    display, start_display, add_menu, add_function_to_menu = init_display()
    shape = create_i_section(900, 300, 16, 10, 5000)
    display.DisplayShape(shape, update=True)
    start_display()
