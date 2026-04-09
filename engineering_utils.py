"""
BOM and STEP export helper.
"""

from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static

class EngineeringUtils:
    """Utilities for engineering calculations and file output."""

    @staticmethod
    def calculate_volume(shape):
        """Calculates the volume of a TopoDS_Shape."""
        props = GProp_GProps()
        brepgprop_VolumeProperties(shape, props)
        return props.Mass()

    @staticmethod
    def export_to_step(shape, filename):
        """Exports a shape to a STEP file."""
        writer = STEPControl_Writer()
        Interface_Static.SetCVal("write.step.schema", "AP203")
        writer.Transfer(shape, STEPControl_AsIs)
        status = writer.Write(filename)
        return status

    @staticmethod
    def generate_bom_report(components_dict, steel_density=7850e-9, concrete_density=2400e-9):
        report = []
        report.append("="*40)
        report.append("  BRIDGE QUANTITY TAKE-OFF (BOM) REPORT")
        report.append("="*40)
        total_concrete_vol = 0
        total_steel_vol = 0
        for name, shape in components_dict.items():
            vol = EngineeringUtils.calculate_volume(shape)
            if "girder" in name.lower() or "rebar" in name.lower():
                mass = vol * steel_density
                total_steel_vol += vol
                report.append(f"{name:.<25} Vol: {vol:>10.2f} mm3 | Mass: {mass:>8.2f} kg")
            else:
                mass = vol * concrete_density
                total_concrete_vol += vol
                report.append(f"{name:.<25} Vol: {vol:>10.2f} mm3 | Mass: {mass:>8.2f} kg")
        report.append("-"*40)
        report.append(f"TOTAL CONCRETE VOLUME: {total_concrete_vol:12.2f} mm3")
        report.append(f"TOTAL STEEL VOLUME:    {total_steel_vol:12.2f} mm3")
        report.append(f"TOTAL STEEL WEIGHT:    {total_steel_vol * steel_density:12.2f} kg")
        report.append("="*40)
        return "\n".join(report)
