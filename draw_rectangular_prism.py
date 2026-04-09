"""
draw_rectangular_prism.py - Provided helper file.
"""
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Display.SimpleGui import init_display

def create_rectangular_prism(length, breadth, height):
    return BRepPrimAPI_MakeBox(length, breadth, height).Shape()

if __name__ == "__main__":
    box = create_rectangular_prism(40.0, 20.0, 100.0)
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape(box, update=True)
    start_display()
