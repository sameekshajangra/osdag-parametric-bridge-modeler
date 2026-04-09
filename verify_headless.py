"""
Verification script for headless runs.
Prints BOM and exports STEP.
"""
import sys
# Fake the display module to prevent import errors in headless mode
from unittest.mock import MagicMock
sys.modules['OCC.Display'] = MagicMock()
sys.modules['OCC.Display.SimpleGui'] = MagicMock()

from bridge_model import OsdagBridgeModeler
from engineering_utils import EngineeringUtils

def verify():
    print("--- HEADLESS VERIFICATION START ---")
    modeler = OsdagBridgeModeler()
    
    # 1. Assemble Bridge (including all advanced features)
    print("Assembling Bridge...")
    modeler.assemble_bridge()
    
    # 4. Generate QTO Report
    print("Generating BOM...")
    report = EngineeringUtils.generate_bom_report(modeler.components)
    print(report)
    
    # 5. Export to STEP
    print("Exporting to bridge_verify.step...")
    status = EngineeringUtils.export_to_step(modeler.assembly, "bridge_verify.step")
    print(f"Export Status: {'SUCCESS' if status == 1 else 'FAILED'}")
    
    print("--- HEADLESS VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify()
