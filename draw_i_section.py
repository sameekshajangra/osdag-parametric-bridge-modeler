"""
draw_i_section.py - Provided helper file.
"""
from OCC.Core.gp import gp_Vec, gp_Trsf
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Display.SimpleGui import init_display

def create_i_section(length, width, depth, flange_thickness, web_thickness):
    web_height = depth - 2 * flange_thickness
    bottom_flange = BRepPrimAPI_MakeBox(length, width, flange_thickness).Shape()
    top_flange = BRepPrimAPI_MakeBox(length, width, flange_thickness).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 0, depth - flange_thickness))
    top_flange_transform = BRepBuilderAPI_Transform(top_flange, trsf, True).Shape()
    web = BRepPrimAPI_MakeBox(length, web_thickness, web_height).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, (width - web_thickness) / 2, flange_thickness))
    web_transform = BRepBuilderAPI_Transform(web, trsf, True).Shape()
    i_section_solid = BRepAlgoAPI_Fuse(bottom_flange, top_flange_transform).Shape()
    i_section_solid = BRepAlgoAPI_Fuse(i_section_solid, web_transform).Shape()
    return i_section_solid

if __name__ == "__main__":
    i_section = create_i_section(1000.0, 100.0, 200.0, 10.0, 5.0)
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape(i_section, update=True)
    display.FitAll()
    start_display()
