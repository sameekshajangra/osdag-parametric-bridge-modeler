"""
Component factories for bridge parts.
Generating 3D solids.
"""

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax2, gp_Dir, gp_Ax1
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace

# Import external primitives as required
from draw_i_section import create_i_section as oc_create_i_section
from draw_rectangular_prism import create_rectangular_prism as oc_create_rectangular_prism



class BridgeComponentFactory:
    """Factory containing reusable methods for bridge parts."""

    @staticmethod
    def create_i_section(d, bf, tf, tw, length):
        """Steel girder I-beam using external primitive logic."""
        return oc_create_i_section(d, bf, tf, tw, length)


    @staticmethod
    def create_deck_slab(length, width, thickness):
        """Creates a rectangular prism for the concrete deck."""
        deck = BRepPrimAPI_MakeBox(length, width, thickness).Shape()
        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(0, -width/2, 0))
        return BRepBuilderAPI_Transform(deck, trsf, True).Shape()

    @staticmethod
    def create_circular_pier(diameter, height):
        """Creates a cylindrical pier column."""
        radius = diameter / 2.0
        return BRepPrimAPI_MakeCylinder(radius, height).Shape()

    @staticmethod
    def create_rectangular_prism(dx, dy, dz):
        """Creates a rectangular prism solid using external primitive logic."""
        return oc_create_rectangular_prism(dx, dy, dz)


    @staticmethod
    def create_trapezoidal_pier_cap(length, width_top, width_bottom, depth_center, depth_end=None):
        """Tapered hammerhead cap."""
        if depth_end is None: depth_end = depth_center
        
        # Profile points for single cross-section
        poly = BRepBuilderAPI_MakePolygon()
        poly.Add(gp_Pnt(0, -width_bottom/2.0, 0))
        poly.Add(gp_Pnt(0, width_bottom/2.0, 0))
        poly.Add(gp_Pnt(0, width_top/2.0, depth_center))
        poly.Add(gp_Pnt(0, -width_top/2.0, depth_center))
        poly.Close()
        
        wire = poly.Wire()
        face = BRepBuilderAPI_MakeFace(wire).Shape()
        cap_solid = BRepPrimAPI_MakePrism(face, gp_Vec(length, 0, 0)).Shape()
        
        # Centering along length
        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(-length/2.0, 0, 0))
        return BRepBuilderAPI_Transform(cap_solid, trsf, True).Shape()

    @staticmethod
    def create_abutment(width, height, depth, wing_length, wing_angle=45):
        """Bridge abutment with sloped wings. Centered on Y=0."""
        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        
        # Breast wall (Centered in Y)
        stem = BRepPrimAPI_MakeBox(depth, width, height).Shape()
        trsf_stem = gp_Trsf()
        trsf_stem.SetTranslation(gp_Vec(0, -width/2.0, 0))
        stem = BRepBuilderAPI_Transform(stem, trsf_stem, True).Shape()
        builder.Add(compound, stem)
        
        # Sloped wing walls
        w_thickness = depth * 0.8
        for side in [-1, 1]:
            # Wing box
            wing = BRepPrimAPI_MakeBox(wing_length, w_thickness, height).Shape()
            
            trsf = gp_Trsf()
            angle_rad = (wing_angle if side > 0 else -wing_angle) * (3.14159/180.0)
            trsf.SetRotation(gp_Ax1(gp_Pnt(0,0,0), gp_Dir(0,0,1)), angle_rad)
            
            y_offset = (width/2.0 - w_thickness/2.0) if side > 0 else (-width/2.0 + w_thickness/2.0)
            trsf.SetTranslationPart(gp_Vec(0, y_offset, 0))
            
            placed_wing = BRepBuilderAPI_Transform(wing, trsf, True).Shape()
            builder.Add(compound, placed_wing)
            
        return compound

    @staticmethod
    def create_bearing(length, width, thickness):
        """Creates an elastomeric bearing pad prism."""
        return BRepPrimAPI_MakeBox(length, width, thickness).Shape()

    @staticmethod
    def create_cross_frame(d, bf, tf, tw, length):
        """Creates a smaller I-section for cross-frames/diaphragms."""
        return BridgeComponentFactory.create_i_section(d, bf, tf, tw, length)

    @staticmethod
    def create_pile_cap(length, width, depth):
        """Rectangular pile cap."""
        cap = BRepPrimAPI_MakeBox(length, width, depth).Shape()
        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(-length/2, -width/2, 0))
        return BRepBuilderAPI_Transform(cap, trsf, True).Shape()

    @staticmethod
    def create_pile(diameter, length):
        """Circular foundation pile."""
        radius = diameter / 2.0
        pile = BRepPrimAPI_MakeCylinder(radius, length).Shape()
        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(0, 0, -length))
        return BRepBuilderAPI_Transform(pile, trsf, True).Shape()
