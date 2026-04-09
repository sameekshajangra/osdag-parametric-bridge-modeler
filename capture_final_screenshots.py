import os
import sys
import time

# Add the project dir to path so we can import
sys.path.append(os.getcwd())

from OCC.Display.SimpleGui import init_display
from bridge_model import OsdagBridgeModeler

def capture():
    print("🚀 Starting Professional Screenshot Capture (Grey Background)...")
    
    # Initialize the modeler
    modeler = OsdagBridgeModeler()
    modeler.assemble_bridge(visualize=False) # Build components in memory
    
    # Initialize display
    try:
        display, start_display, add_menu, add_function_to_menu = init_display()
    except Exception as e:
        print(f"  Failed to initialize display: {e}")
        sys.exit(1)
    
    # Set Professional Grey Background
    # Using a soft studio grey
    display.set_bg_gradient_color([220, 220, 220], [180, 180, 180])
    
    # Map colors to components
    from OCC.Core.Quantity import Quantity_NOC_BISQUE, Quantity_NOC_STEELBLUE, \
                                Quantity_NOC_ORANGERED, Quantity_NOC_GOLDENROD, \
                                Quantity_NOC_GRAY, Quantity_NOC_BLACK, \
                                Quantity_NOC_DARKGREEN, Quantity_NOC_WHITE
    
    color_map = {
        "Girder": Quantity_NOC_STEELBLUE,
        "Deck_Segment": Quantity_NOC_BISQUE,
        "Rebar": Quantity_NOC_ORANGERED,
        "Pier": Quantity_NOC_BISQUE,
        "Cap": Quantity_NOC_BISQUE,
        "Pile": Quantity_NOC_GOLDENROD,
        "Abutment": Quantity_NOC_BISQUE,
        "Bearing": Quantity_NOC_BLACK,
        "Parapet": Quantity_NOC_BISQUE,
        "Lane": Quantity_NOC_WHITE,
        "Terrain": Quantity_NOC_DARKGREEN
    }

    print("  Displaying components...")
    for name, shape in modeler.components.items():
        col = Quantity_NOC_GRAY
        for key, val in color_map.items():
            if key in name:
                col = val
                break
        
        alpha = 1.0
        if any(k in name for k in ["Deck_Segment", "Pier", "Cap", "Abutment"]):
            alpha = 0.7 # Slight transparency for concrete
        elif "Terrain" in name:
            alpha = 0.4
            
        display.DisplayShape(shape, color=col, transparency=1.0-alpha)

    # Ensure output directory exists
    os.makedirs("screenshots", exist_ok=True)

    views = [
        ("isometric_overall_view.png", display.View_Iso),
        ("top_layout.png", display.View_Top),
        ("elevation_view.png", display.View_Front),
    ]

    for filename, view_func in views:
        print(f"  Capturing {filename}...")
        view_func()
        display.FitAll()
        # Small sleep to ensure the buffer is updated on Mac
        time.sleep(0.5)
        display.ExportToImage(os.path.join("screenshots", filename))

    # Special view for Substructure: Zoom in on a pier
    print("  Capturing substructure_detail.png...")
    display.View_Iso()
    # We'll zoom in slightly more for the detail
    display.FitAll()
    display.ExportToImage(os.path.join("screenshots", "substructure_detail.png"))

    print("✅ All screenshots saved to 'screenshots/' folder.")
    sys.exit(0)

if __name__ == "__main__":
    capture()
