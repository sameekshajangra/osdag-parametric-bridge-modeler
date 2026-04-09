from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

def create_rectangular_prism(dx, dy, dz):
    """
    Creates a 3D model of a rectangular prism.
    Arguments: dx, dy, dz are dimensions along X, Y, Z axes.
    """
    return BRepPrimAPI_MakeBox(dx, dy, dz).Shape()

if __name__ == "__main__":
    from OCC.Display.SimpleGui import init_display
    display, start_display, add_menu, add_function_to_menu = init_display()
    shape = create_rectangular_prism(100, 200, 300)
    display.DisplayShape(shape, update=True)
    start_display()
