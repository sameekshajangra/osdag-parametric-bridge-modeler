# Osdag Parametric Bridge Modeler
**FOSSEE Summer Fellowship 2026 - Screening Task Submission**

## 🏗️ Project Overview
This project presents a fully parametric 3D bridge modeler developed as part of the FOSSEE screening task. It leverages `pythonocc-core` (Open Cascade) to generate a complete bridge assembly, featuring complex geometries, reinforced concrete components, and structural steel elements.

### ✨ Key Features
- **Parametric Design**: Fully adjustable geometry including span length, deck width, girder counts, and substructure dimensions.
- **Precision Alignment**: Mathematical synchronization of all components centered at a global (0,0,0) origin.
- **Automated BOM**: Integrated engineering utility for calculating total concrete volume, steel volume, and total mass.
- **Structural Integrity**: Includes detailed reinforcement (circular column cages and 3D deck grids) and standard bridge components like tapered pier caps and elastomeric bearings.
- **CAD Interoperability**: Automatic export functionality for Industry-standard STEP and BREP formats.

## 🎞️ Gallery
![Isometric Overall View](screenshots/isometric_overall_view.png)
*Full assembly showing the steel-girder superstructure and reinforced concrete substructure.*

![Top Layout](screenshots/top_layout.png)
*Plan layout highlighting the modular deck segments and lane demarcations.*

![Substructure Detail](screenshots/substructure_detail.png)
*Close-up detail of the bearings, tapered pier cap, and circular column.*

![Elevation View](screenshots/elevation_view.png)
*Longitudinal elevation showing the foundation pilling and abutment walls.*

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- `pythonocc-core` 7.7.1+
- `pyside2` 

### Installation & Execution
1. Create and activate a conda environment with the required dependencies.
2. Clone the repository and navigate to the project directory.
3. Run the main assembly script:
   ```bash
   python bridge_model.py
   ```
   *Note: On MacOS, the script automatically handles graphics buffer synchronization for the 3D viewer.*
---
*Submitted by Sameeksha Sharma for the FOSSEE Summer Fellowship 2026.*
