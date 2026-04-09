# Technical Report: Parametric 3D Bridge Modeler
**FOSSEE Summer Fellowship 2026 — Osdag Screening Task**

## 1. Project Overview
This project implements a fully parametric, modular 3D CAD modeling system for a short-span steel girder bridge using `pythonocc-core`. The system is designed to allow structural engineers to automate the geometry creation of bridge assemblies, including superstructure, substructure, and reinforcement, while providing automated Quantity Take-Off (QTO) data.

## 2. Geometric Logic & Architecture
The project is built on a **Factory Pattern** architecture, separating concerns into four specialized modules:

### 2.1 Superstructure (Girder, Deck & Cross-Frames)
- **Steel Girders**: Modeled as standard I-sections. The geometry is created by fusing two flange blocks and one web block.
- **Cross-Frames (Diaphragms)**: Added `build_crossframes()` to create intermediate structural supports between girders.
- **Deck Detailing**: Includes parametric **Lane Demarcations** and **Parapet Railings** for a complete, functional highway bridge visual.

### 2.2 Substructure (Piers & Foundations)
- **Tapered "Hammerhead" Pier Cap**: Upgraded the cap design to a variable-depth profile (tapered longitudinally), standard in high-span highway construction.
- **Abutments with Wing Walls**: Implemented structural end-supports with sloped wing walls to anchor the bridge into soil embankments.
- **Elastomeric Bearings**: Added detailed support pads between the steel girders and concrete substructure to account for thermal expansion and load distribution.
- **Pile Foundations**: A 2×2 grid of circular piles supporting a rectangular pile cap.

### 2.3 Reinforcement (Rebar)
- **Deck Grid**: A double-layer orthogonal grid of cylindrical rebars. The spacing calculation accounts for concrete cover and longitudinal vs. transverse placement.
- **Pier Cage**: Implements IS 13920 conventions. Vertical longitudinal bars are arranged in a circular array, wrapped by polygon-approximated "hoop" stirrups.

## 3. Engineering Utility & Standards
The model applies real-world engineering logic:
- **Quantity Take-Off (QTO)**: Uses `GProp_GProps` to calculate the exact volume of every component. Mass is estimated using standard densities (7850 kg/m³ for steel, 2400 kg/m³ for concrete).
- **CAD Interoperability**: Integrated `STEPControl_Writer` ensures that the model can be exported to industrial CAD software (AutoCAD, MicroStation) for professional drafting.
- **Materials Codes**: Geometry is designed with awareness of IS 456 (Concrete) and ISMB (Steel) section standards.

## 4. How to Use & Extend
The model is controlled via the `bridge_model.py` constants section. By changing a single variable like `SPAN_LENGTH_L`, the entire assembly — including rebar counts and pile placements — updates automatically, maintaining structural coherence.

## 5. Conclusion
This submission demonstrates proficiency in:
- High-level Python programming with Open Cascade.
- Modular software design.
- Structural engineering awareness.
- Advanced CAD visualization (transparency & color mapping).
