"""
Bridge assembly script - FOSSEE Screening 2026.
Main logic for parametric girder bridge.

import os
# Mac-specific fix for pythonocc-core Segfault
os.environ['QT_MAC_WANTS_LAYER'] = '1'

Coordinate System:
    X -> Longitudinal (along span)
    Y -> Transverse (across deck width)
    Z -> Vertical
Origin: Bottom of girder at the left abutment.
"""

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Dir, gp_Ax1, gp_Ax2
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Display.SimpleGui import init_display
from OCC.Core.Quantity import (
    Quantity_NOC_GRAY, Quantity_NOC_STEELBLUE, Quantity_NOC_RED,
    Quantity_NOC_TAN, Quantity_NOC_GOLD, Quantity_NOC_WHITE
)

# Local module imports
from component_factories import BridgeComponentFactory as Factory
from reinforcement_utils import RebarFactory
from engineering_utils import EngineeringUtils

# ==========================================
# PARAMETERS (Adjustable by User)
# ==========================================

# 1. Geometry & Layout
UNITS = "mm"                         # "mm" or "m"
SPAN_LENGTH_L = 12000.0              # Total clear span
N_GIRDERS = 3                        # ≥ 3
GIRDER_CENTROID_SPACING = 3000.0     # Transverse spacing
GIRDER_OFFSET_FROM_EDGE = 500.0      # Overhang distance
DECK_WIDTH = 7000.0                  # Total width
DECK_THICKNESS = 200.0               # Concrete slab depth
DECK_OVERHANG = 500.0                # Overhang beyond outer girders
DECK_SLAB_SEGMENT_LENGTH = 3000.0    # Longitudinal segment size
EXPANSION_GAP = 25.0                 # Gap between deck and abutment
N_LANES = 2                          # Optional demarcation
LANE_WIDTH = 3500.0                  # Standard lane width

# 2. Main Girder (I-Section)
GIRDER_LENGTH = 12000.0              # SPAN_LENGTH_L ± end conditions
GIRDER_SECTION_D = 900.0
GIRDER_SECTION_BF = 300.0
GIRDER_SECTION_TF = 16.0
GIRDER_SECTION_TW = 10.0
GIRDER_MATERIAL = "Steel S355"       # Material label

# 3. Cross-Frames (Intermediate Diaphragms)
N_CROSS_FRAMES = 3 
CROSS_FRAME_SECTION_D = 400.0
CROSS_FRAME_SECTION_BF = 150.0
CROSS_FRAME_SECTION_TF = 10.0
CROSS_FRAME_SECTION_TW = 8.0

# 4. Substructure (Pier & Cap)
PIER_DIAMETER = 800.0
PIER_HEIGHT = 3000.0
PIER_CAP_TOP_WIDTH = 3000.0
PIER_CAP_BOTTOM_WIDTH = 1200.0
PIER_CAP_DEPTH = 600.0
PIER_CAP_LONG_WIDTH = 800.0          # Longitudinal thickness of cap
PIER_CAP_ELEVATION = 0.0             # Vertical offset from pier top
PIER_CAP_TAPER_RATIO = 0.7           # Depth at ends relative to center
PIER_LOCATIONS = [0.0]               # Shifted away from abutments

# 5. Foundations (Pile & Cap)
N_PILES_PER_CAP = 4 
PILE_DIAMETER = 400.0
PILE_LENGTH = 5000.0
PILE_CAP_LENGTH = 2200.0
PILE_CAP_WIDTH = 1200.0
PILE_CAP_DEPTH = 600.0
PILE_SPACING = 600.0
PILE_CAP_ELEVATION = 0.0             # relative to ground

# 6. Abutments & Bearings
ABUTMENT_DEPTH = 1000.0              # Thickness of breast wall
ABUTMENT_HEIGHT = 2500.0             # Vertical height
WING_LENGTH = 3000.0                 # Length of sloped wing walls
WING_ANGLE = 30.0                    # Outer flare angle
BEARING_THICKNESS = 100.0            # Elastomeric pad height
BEARING_SIZE = 400.0                 # Pad width/length

# 6. Reinforcement
REBAR_MAIN_DIAMETER = 16.0
REBAR_TRANSVERSE_DIAMETER = 8.0
REBAR_SPACING_LONGITUDINAL = 150.0 
REBAR_SPACING_TRANSVERSE = 200.0
REBAR_COVER = 40.0
REBAR_VISIBLE = True

# 7. Visualization & Output
CONCRETE_OPACITY = 0.35
BACKGROUND_COLOR = "grey"            # "white" or "grey"
SHOW_AXES = True
SAVE_STEP = True
STEP_FILENAME = "bridge_model.step"
SAVE_BREP = True
BREP_FILENAME = "bridge_model.brep"
RENDER_SIZE = (1920, 1080)           # Screenshot resolution
PARAPET_VISIBLE = True               # Creative addition
TERRAIN_VISIBLE = True               # Contextual terrain
TERRAIN_OPACITY = 0.5
CONCRETE_COLOR = "BISQUE"
STEEL_COLOR = "STEELBLUE"
REBAR_COLOR = "ORANGERED"
TERRAIN_COLOR = "DARKGREEN"
FOUNDATION_COLOR = "GOLDENROD"

# ==========================================
# ASSEMBLY LOGIC
# ==========================================

class OsdagBridgeModeler:
    def __init__(self):
        self.builder = BRep_Builder()
        self.assembly = TopoDS_Compound()
        self.builder.MakeCompound(self.assembly)
        self.components = {} # For BOM tracking

    def build_girders(self):
        """Creates and positions N_GIRDERS longitudinally."""
        start_y = -((N_GIRDERS - 1) * GIRDER_CENTROID_SPACING) / 2.0
        for i in range(N_GIRDERS):
            girder = Factory.create_i_section(GIRDER_SECTION_D, GIRDER_SECTION_BF, GIRDER_SECTION_TF, GIRDER_SECTION_TW, SPAN_LENGTH_L)
            trsf = gp_Trsf()
            y_pos = start_y + i * GIRDER_CENTROID_SPACING
            trsf.SetTranslation(gp_Vec(-SPAN_LENGTH_L/2.0, y_pos, -GIRDER_SECTION_D - DECK_THICKNESS))
            placed_girder = BRepBuilderAPI_Transform(girder, trsf, True).Shape()
            self.builder.Add(self.assembly, placed_girder)
            self.components[f"Girder_{i+1}"] = placed_girder

    def build_deck(self):
        """Building deck segments as per span logic."""
        full_l = SPAN_LENGTH_L
        n_segments = int(full_l / DECK_SLAB_SEGMENT_LENGTH)
        if n_segments < 1: n_segments = 1
        seg_l = full_l / n_segments
        
        for i in range(n_segments):
            # Segment box
            segment = Factory.create_rectangular_prism(DECK_WIDTH, DECK_THICKNESS, seg_l)
            trsf = gp_Trsf()
            # Longitudinal placement
            x_start = -SPAN_LENGTH_L/2.0 + i * seg_l
            trsf.SetTranslation(gp_Vec(x_start, -DECK_WIDTH/2.0, -DECK_THICKNESS))
            placed_seg = BRepBuilderAPI_Transform(segment, trsf, True).Shape()
            self.builder.Add(self.assembly, placed_seg)
            self.components[f"Deck_Segment_{i}"] = placed_seg

        # Rebar grid
        if REBAR_VISIBLE:
            deck_rebar = RebarFactory.create_rebar_grid_for_deck(
                DECK_WIDTH, SPAN_LENGTH_L, REBAR_COVER, REBAR_MAIN_DIAMETER, REBAR_SPACING_LONGITUDINAL, DECK_THICKNESS
            )
            trsf_rebar = gp_Trsf()
            trsf_rebar.SetTranslation(gp_Vec(-SPAN_LENGTH_L/2.0, -DECK_WIDTH/2.0, -DECK_THICKNESS))
            placed_rebar = BRepBuilderAPI_Transform(deck_rebar, trsf_rebar, True).Shape()
            self.builder.Add(self.assembly, placed_rebar)
            self.components["Deck_Rebars"] = placed_rebar

    def build_lanes(self):
        """Adds lane demarcation markings to the deck surface."""
        if N_LANES < 1: return
        stripe_width = 150.0 # Standard marking width
        stripe_depth = 5.0   # Very thin prism
        
        # Center line and lane boundaries
        total_lane_width = N_LANES * LANE_WIDTH
        for i in range(N_LANES + 1):
            y_pos = -total_lane_width/2.0 + i * LANE_WIDTH
            if abs(y_pos) > DECK_WIDTH/2.0: continue
            
            stripe = Factory.create_rectangular_prism(SPAN_LENGTH_L, stripe_width, stripe_depth)
            trsf = gp_Trsf()
            trsf.SetTranslation(gp_Vec(-SPAN_LENGTH_L/2.0, y_pos - stripe_width/2.0, 0))
            placed_stripe = BRepBuilderAPI_Transform(stripe, trsf, True).Shape()
            self.builder.Add(self.assembly, placed_stripe)
            self.components[f"Lane_Marking_{i}"] = placed_stripe

    def build_terrain(self):
        """Adds a contextual 'Valley Terrain' wedge under the bridge."""
        if not TERRAIN_VISIBLE: return
        t_width = DECK_WIDTH * 4.0
        t_length = SPAN_LENGTH_L * 1.5
        t_depth = PIER_HEIGHT * 2.0
        
        # Simple V-wedge using a fused prism or slanted Box
        terrain = Factory.create_rectangular_prism(t_width, t_depth, t_length)
        trsf = gp_Trsf()
        # Position below the pier cap level
        z_pos = -DECK_THICKNESS - GIRDER_SECTION_D - PIER_HEIGHT - PIER_CAP_DEPTH - t_depth/1.5
        trsf.SetTranslation(gp_Vec(-t_length/2.0, -t_width/2.0, z_pos))
        placed_t = BRepBuilderAPI_Transform(terrain, trsf, True).Shape()
        self.builder.Add(self.assembly, placed_t)
        self.components["Valley_Terrain"] = placed_t

    def build_parapets(self):
        """Deck railings."""
        if not PARAPET_VISIBLE: return
        p_height = 800.0
        p_width = 150.0
        
        for y_side in [-DECK_WIDTH/2.0 + p_width/2.0, DECK_WIDTH/2.0 - p_width/2.0]:
            parapet = Factory.create_rectangular_prism(SPAN_LENGTH_L, p_width, p_height)
            trsf = gp_Trsf()
            trsf.SetTranslation(gp_Vec(-SPAN_LENGTH_L/2.0, y_side - p_width/2.0, 0))
            placed_p = BRepBuilderAPI_Transform(parapet, trsf, True).Shape()
            self.builder.Add(self.assembly, placed_p)
            self.components[f"Parapet_{y_side}"] = placed_p

    def build_abutments(self):
        """Substructure foundations at span ends."""
        for side in [-1, 1]:
            abutment = Factory.create_abutment(DECK_WIDTH, ABUTMENT_HEIGHT, ABUTMENT_DEPTH, WING_LENGTH, WING_ANGLE)
            trsf = gp_Trsf()
            
            # Positioned under the main span ends
            x_pos = (SPAN_LENGTH_L/2.0) if side > 0 else (-SPAN_LENGTH_L/2.0 - ABUTMENT_DEPTH)
            z_pos = -DECK_THICKNESS - GIRDER_SECTION_D - ABUTMENT_HEIGHT
            
            trsf.SetTranslation(gp_Vec(x_pos, -DECK_WIDTH/2.0, z_pos))
            placed_a = BRepBuilderAPI_Transform(abutment, trsf, True).Shape()
            self.builder.Add(self.assembly, placed_a)
            self.components[f"Abutment_{side}"] = placed_a

    def build_bearings(self):
        """Support pads between girder and pier/abutment."""
        z_pos = -DECK_THICKNESS - GIRDER_SECTION_D
        
        # At Pier
        for p_loc in PIER_LOCATIONS:
            for g_idx in range(N_GIRDERS):
                y_pos = -((N_GIRDERS-1)*GIRDER_CENTROID_SPACING)/2.0 + g_idx*GIRDER_CENTROID_SPACING
                
                bearing = Factory.create_bearing(BEARING_SIZE, BEARING_SIZE, BEARING_THICKNESS)
                trsf = gp_Trsf()
                trsf.SetTranslation(gp_Vec(p_loc - BEARING_SIZE/2.0, y_pos - BEARING_SIZE/2.0, z_pos))
                placed_b = BRepBuilderAPI_Transform(bearing, trsf, True).Shape()
                self.builder.Add(self.assembly, placed_b)
                self.components[f"Bearing_Pier_{p_loc}_{g_idx}"] = placed_b
                
        # 2. Bearings at Abutments
        for side in [-1, 1]:
            x_pos = (SPAN_LENGTH_L/2.0 - BEARING_SIZE/2.0) if side > 0 else (-SPAN_LENGTH_L/2.0 + BEARING_SIZE/2.0)
            for g_idx in range(N_GIRDERS):
                y_pos = -((N_GIRDERS-1)*GIRDER_CENTROID_SPACING)/2.0 + g_idx*GIRDER_CENTROID_SPACING
                
                bearing = Factory.create_bearing(BEARING_SIZE, BEARING_SIZE, BEARING_THICKNESS)
                trsf = gp_Trsf()
                trsf.SetTranslation(gp_Vec(x_pos - BEARING_SIZE/2.0, y_pos - BEARING_SIZE/2.0, z_pos))
                placed_b = BRepBuilderAPI_Transform(bearing, trsf, True).Shape()
                self.builder.Add(self.assembly, placed_b)
                self.components[f"Bearing_Abutment_{side}_{g_idx}"] = placed_b

    def build_crossframes(self):
        """Creates and positions cross-frames (diaphragms) between girders."""
        if N_CROSS_FRAMES < 1: return
        
        spacing_long = SPAN_LENGTH_L / (N_CROSS_FRAMES + 1)
        start_y = -((N_GIRDERS - 1) * GIRDER_CENTROID_SPACING) / 2.0
        cf_length = GIRDER_CENTROID_SPACING - GIRDER_SECTION_TW
        
        for i in range(N_CROSS_FRAMES):
            # x_pos relative to -L/2
            x_pos = -SPAN_LENGTH_L/2.0 + spacing_long * (i + 1)
            for j in range(N_GIRDERS - 1):
                y_center = start_y + (j + 0.5) * GIRDER_CENTROID_SPACING
                
                cf = Factory.create_cross_frame(
                    CROSS_FRAME_SECTION_D, CROSS_FRAME_SECTION_BF, 
                    CROSS_FRAME_SECTION_TF, CROSS_FRAME_SECTION_TW, cf_length
                )
                
                trsf = gp_Trsf()
                trsf.SetRotation(gp_Ax1(gp_Pnt(0,0,0), gp_Dir(0,0,1)), 3.14159/2.0)
                trsf.SetTranslationPart(gp_Vec(x_pos, y_center - cf_length/2.0, -DECK_THICKNESS - CROSS_FRAME_SECTION_D/2.0 - (GIRDER_SECTION_D-CROSS_FRAME_SECTION_D)/2.0))
                
                placed_cf = BRepBuilderAPI_Transform(cf, trsf, True).Shape()
                self.builder.Add(self.assembly, placed_cf)
                self.components[f"CrossFrame_{i+1}_{j+1}"] = placed_cf

    def build_piers_and_pilecaps(self, x_pos=0.0):
        """Builds pier, pier cap, and foundation centered longitudinally at x_pos."""
        
        # 1. Pier Cap (Trapezoidal / Tapered Hammerhead)
        # Sits under the bearings
        z_cap = -DECK_THICKNESS - GIRDER_SECTION_D - BEARING_THICKNESS - PIER_CAP_DEPTH
        cap = Factory.create_trapezoidal_pier_cap(
            PIER_CAP_LONG_WIDTH, PIER_CAP_TOP_WIDTH, PIER_CAP_BOTTOM_WIDTH, 
            PIER_CAP_DEPTH, PIER_CAP_DEPTH * PIER_CAP_TAPER_RATIO
        )
        trsf_cap = gp_Trsf()
        trsf_cap.SetTranslation(gp_Vec(x_pos, 0, z_cap))
        placed_cap = BRepBuilderAPI_Transform(cap, trsf_cap, True).Shape()
        self.builder.Add(self.assembly, placed_cap)
        self.components[f"Pier_Cap_{x_pos}"] = placed_cap

        # 2. Pier Column (Circular)
        # Starts from Pier Cap bottom
        z_pier = z_cap
        pier = Factory.create_circular_pier(PIER_DIAMETER, PIER_HEIGHT)
        trsf_pier = gp_Trsf()
        # Origin of column is bottom-center
        trsf_pier.SetTranslation(gp_Vec(x_pos, 0, -DECK_THICKNESS - GIRDER_SECTION_D - PIER_CAP_DEPTH - PIER_HEIGHT))
        placed_pier = BRepBuilderAPI_Transform(pier, trsf_pier, True).Shape()
        self.builder.Add(self.assembly, placed_pier)
        self.components[f"Pier_{x_pos}"] = placed_pier
        
        # 3. Pier Rebar
        if REBAR_VISIBLE:
            pier_rebar = RebarFactory.create_column_reinforcement(
                PIER_DIAMETER, PIER_HEIGHT, REBAR_COVER, REBAR_MAIN_DIAMETER, 
                REBAR_TRANSVERSE_DIAMETER, 8, 200.0
            )
            placed_p_rebar = BRepBuilderAPI_Transform(pier_rebar, trsf_pier, True).Shape()
            self.builder.Add(self.assembly, placed_p_rebar)
            self.components[f"Pier_Rebars_{x_pos}"] = placed_p_rebar
            
        # 3. Pile Cap (Rectangular)
        pile_cap_z = -DECK_THICKNESS - GIRDER_SECTION_D - PIER_CAP_DEPTH - PIER_HEIGHT - PILE_CAP_DEPTH
        p_cap = Factory.create_pile_cap(PILE_CAP_LENGTH, PILE_CAP_WIDTH, PILE_CAP_DEPTH)
        trsf_pcap = gp_Trsf()
        trsf_pcap.SetTranslation(gp_Vec(x_pos - PILE_CAP_LENGTH/2.0, -PILE_CAP_WIDTH/2.0, pile_cap_z))
        placed_pcap = BRepBuilderAPI_Transform(p_cap, trsf_pcap, True).Shape()
        self.builder.Add(self.assembly, placed_pcap)
        self.components[f"Pile_Cap_{x_pos}"] = placed_pcap

        # 4. Piles (Arranged in 2x2 grid)
        for dx in [-PILE_SPACING/2, PILE_SPACING/2]:
            for dy in [-PILE_SPACING/2, PILE_SPACING/2]:
                pile = Factory.create_pile(PILE_DIAMETER, PILE_LENGTH)
                trsf_pile = gp_Trsf()
                trsf_pile.SetTranslation(gp_Vec(x_pos + dx, dy, pile_cap_z - PILE_LENGTH))
                placed_pile = BRepBuilderAPI_Transform(pile, trsf_pile, True).Shape()
                self.builder.Add(self.assembly, placed_pile)
                self.components[f"Pile_{x_pos}_{dx}_{dy}"] = placed_pile

    def assemble_bridge(self):
        """Orchestrates the assembly, verification, and output."""
        print("Starting assembly of Osdag Bridge Model...")
        print(f"Origin (0,0,0) set at Center of Span, Deck Top Level.")

        print("[1/4] Building Superstructure...")
        self.build_girders()
        self.build_deck()
        self.build_crossframes()
        self.build_parapets()
        self.build_lanes()
        self.build_bearings()
        self.build_abutments()
        self.build_terrain()

        print("[2/4] Building Substructures at designated locations...")
        for loc in PIER_LOCATIONS:
            self.build_piers_and_pilecaps(x_pos=loc)

    def generate_report(self):
        """Prints the final engineering QTO report."""
        print("\n" + "="*55)
        print("  BRIDGE QUANTITY TAKE-OFF (BOM) REPORT")
        print("="*55)
        print(f"  GIRDER MATERIAL: {GIRDER_MATERIAL}")
        print(f"  UNITS:           {UNITS}")
        print("-"*55)
        report = EngineeringUtils.generate_bom_report(self.components)
        print(report)
        print("="*55 + "\n")

        print("[4/4] Exporting and visualizing...")
        if SAVE_STEP:
            status = EngineeringUtils.export_to_step(self.assembly, STEP_FILENAME)
            print(f"  STEP Export -> '{STEP_FILENAME}': {'OK' if status == 1 else 'FAILED'}")
            
        if SAVE_BREP:
            # Simple BREP export using BRepTools
            from OCC.Core.BRepTools import breptools
            breptools.Write(self.assembly, BREP_FILENAME)
            print(f"  BREP Export -> '{BREP_FILENAME}': OK")

        # --- Visualization ---
        try:
            print("  Initializing 3D Visualizer (backend='pyside2')...")
            display, start_display, add_menu, add_function_to_menu = init_display(backend='pyside2')
        except Exception as e:
            print(f"  Warning: GUI Backend initialization failed ({e}). Attempting default...")
            display, start_display, add_menu, add_function_to_menu = init_display()

        # Define component display styles
        from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_BISQUE, Quantity_NOC_STEELBLUE, \
                                    Quantity_NOC_ORANGERED, Quantity_NOC_GOLDENROD, Quantity_NOC_DARKGREEN, \
                                    Quantity_NOC_WHITE, Quantity_NOC_GRAY, Quantity_NOC_BLACK
        
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
        
        for name, shape in self.components.items():
            # Determine color by name keyword
            col = Quantity_NOC_GRAY
            for key, val in color_map.items():
                if key in name:
                    col = val
                    break
            
            # Apply transparency to concrete and terrain
            alpha = 1.0
            if any(k in name for k in ["Deck_Segment", "Pier", "Cap", "Abutment"]):
                alpha = CONCRETE_OPACITY
            elif "Terrain" in name:
                alpha = TERRAIN_OPACITY
                
            display.DisplayShape(shape, color=col, transparency=1.0-alpha)

        if SHOW_AXES:
            display.display_triedron()
        
        # Auto-snapshot
        print(f"  Saving auto-snapshot to 'bridge_snapshot.png'...")
        display.View_Isometric()
        display.fit_all()
        display.ExportToImage("bridge_snapshot.png")
        print("  Snapshot saved successfully.")

        # Initial camera view
        display.View_Isometric()
        display.fit_all()
        display.View.SetBgGradientStyle(1) # Subtle background gradient
        
        display.StartMessageLoop()

        display.FitAll()
        print("\nVisualization ready. Close the window to exit.")
        start_display()

if __name__ == "__main__":
    modeler = OsdagBridgeModeler()
    modeler.assemble_bridge()
