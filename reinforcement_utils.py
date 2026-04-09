"""
Rebar factory for deck and piers.
"""

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax2, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound
import math

class RebarFactory:
    """Factory for creating reinforcement cages and grids."""

    @staticmethod
    def _cylinder_along_x(diameter, length, origin_pnt):
        radius = diameter / 2.0
        ax = gp_Ax2(origin_pnt, gp_Dir(1, 0, 0))
        return BRepPrimAPI_MakeCylinder(ax, radius, length).Shape()

    @staticmethod
    def _cylinder_along_y(diameter, length, origin_pnt):
        radius = diameter / 2.0
        ax = gp_Ax2(origin_pnt, gp_Dir(0, 1, 0))
        return BRepPrimAPI_MakeCylinder(ax, radius, length).Shape()

    @staticmethod
    def _cylinder_along_z(diameter, length, origin_pnt):
        radius = diameter / 2.0
        ax = gp_Ax2(origin_pnt, gp_Dir(0, 0, 1))
        return BRepPrimAPI_MakeCylinder(ax, radius, length).Shape()

    @staticmethod
    def _cylinder_along_vec(diameter, length, origin_pnt, direction_dir):
        radius = diameter / 2.0
        ax = gp_Ax2(origin_pnt, direction_dir)
        return BRepPrimAPI_MakeCylinder(ax, radius, length).Shape()

    @staticmethod
    def create_rebar_grid_for_deck(deck_width, span_length, cover, diam, spacing, thickness=200.0):
        """Creates a double-layer grid of rebar for the deck slab."""
        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        
        # Longitudinal bars (X direction)
        n_long = int((deck_width - 2 * cover) / spacing) + 1
        x_bars_start_y = -deck_width / 2.0 + cover
        
        # Transverse bars (Y direction)
        n_trans = int((span_length - 2 * cover) / spacing) + 1
        y_bars_start_x = -span_length / 2.0 + cover
        
        # We create double layer: bottom (at cover) and top (at thickness - cover)
        for layer_z in [cover, thickness - cover]:
            # Longitudinal bars
            for i in range(n_long):
                y = x_bars_start_y + i * spacing
                # Bar goes from -L/2 + cover to L/2 - cover
                p1 = gp_Pnt(-span_length/2.0 + cover, y, layer_z)
                p2 = gp_Pnt(span_length/2.0 - cover, y, layer_z)
                bar = BRepPrimAPI_MakeCylinder(gp_Ax2(p1, gp_Dir(1, 0, 0)), diam/2.0, span_length - 2*cover).Shape()
                builder.Add(compound, bar)
                
            # Transverse bars
            for j in range(n_trans):
                x = y_bars_start_x + j * spacing
                # Bar goes from -W/2 + cover to W/2 - cover
                p1 = gp_Pnt(x, -deck_width/2.0 + cover, layer_z + diam) # offset by diam to avoid overlap
                p2 = gp_Pnt(x, deck_width/2.0 - cover, layer_z + diam)
                bar = BRepPrimAPI_MakeCylinder(gp_Ax2(p1, gp_Dir(0, 1, 0)), diam/2.0, deck_width - 2*cover).Shape()
                builder.Add(compound, bar)
                
        return compound
    @staticmethod
    def create_column_reinforcement(diameter, height, cover, main_diam, stirrup_diam, num_main_bars, stirrup_spacing):
        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        cage_radius = (diameter / 2.0) - cover - stirrup_diam - (main_diam / 2.0)
        for i in range(num_main_bars):
            angle = (2.0 * math.pi * i) / num_main_bars
            x = cage_radius * math.cos(angle)
            y = cage_radius * math.sin(angle)
            bar_height = height - 2 * cover
            bar = RebarFactory._cylinder_along_z(main_diam, bar_height, gp_Pnt(x, y, cover))
            builder.Add(compound, bar)
        if stirrup_diam > 0:
            hoop_radius = (diameter / 2.0) - cover - (stirrup_diam / 2.0)
            num_stirrups = int((height - 2 * cover) / stirrup_spacing) + 1
            num_seg = 16
            for j in range(num_stirrups):
                z_hoop = cover + j * stirrup_spacing
                if z_hoop > height - cover: break
                for s in range(num_seg):
                    a1 = (2.0 * math.pi * s) / num_seg
                    a2 = (2.0 * math.pi * (s + 1)) / num_seg
                    p1 = gp_Pnt(hoop_radius * math.cos(a1), hoop_radius * math.sin(a1), z_hoop)
                    p2 = gp_Pnt(hoop_radius * math.cos(a2), hoop_radius * math.sin(a2), z_hoop)
                    seg_vec = gp_Vec(p1, p2)
                    seg_len = seg_vec.Magnitude()
                    if seg_len < 1e-6: continue
                    seg = RebarFactory._cylinder_along_vec(stirrup_diam, seg_len, p1, gp_Dir(seg_vec))
                    builder.Add(compound, seg)
        return compound
