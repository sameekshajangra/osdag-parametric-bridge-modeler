# Technical Report: Osdag Parametric Bridge Modeler
**FOSSEE Summer Fellowship 2026 Submission**

## 1. Introduction
This project provides a parametric 3D CAD modeling script for a steel girder bridge using the `pythonocc-core` library. The goal is to automate the generation of bridge components for structural design and quantity estimation.

## 2. Model Structure
The code is organized into modular factories to handle different parts of the bridge assembly:

*   **Superstructure**: Includes steel I-girders, a segmented concrete deck slab, and intermediate cross-frames for lateral stability.
*   **Substructure**: Features a tapered hammerhead pier cap, circular piers, and abutments with sloped wing walls.
*   **Reinforcement**: Automated generation of rebar grids for the deck and circular cages for the piers based on concrete cover and spacing parameters.
*   **Foundations**: Pile caps with a 2x2 grid of circular piles.

## 3. Key Features
*   **Parametric Design**: Dimensions like span length, number of girders, and pier height can be modified in the constants section.
*   **BOM Reporting**: Automatically calculates volumes and estimated weights for steel and concrete components.
*   **CAD Interoperability**: Supports export to STEP and BREP formats for use in industrial CAD tools.
*   **Visualization**: Includes deck markings, railings, and a simplified terrain context for better presentation.

## 4. Engineering Logic
Component generation follows standard structural patterns:
*   Girders are modeled as standard I-sections fused from plates.
*   Reinforcement logic accounts for concrete cover and longitudinal/transverse spacing.
*   Substructure components are positioned relative to the span center and deck top origin.

## 5. Usage
To run the model, ensure `pythonocc-core` is installed and execute `bridge_model.py`. The generated files and QTO report will be saved in the directory.
