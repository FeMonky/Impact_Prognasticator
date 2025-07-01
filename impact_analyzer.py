import argparse
import re
import csv
import os
from datetime import datetime

# --- Material Properties Database ---
# A simplified database of material properties.
# Values are illustrative. In a real-world scenario, these would be more detailed.
# Tensile Strength (MPa), Impact Strength (kJ/m^2)
MATERIALS = {
    "PLA": {"tensile_strength": 50, "impact_strength": 5},
    "PETG": {"tensile_strength": 45, "impact_strength": 8},
    "ABS": {"tensile_strength": 40, "impact_strength": 10},
    "TPU": {"tensile_strength": 35, "impact_strength": 30}, # Flexible, high impact resistance
}

# --- Impact Force Presets ---
# Estimated impact energy in Joules. These are simplified for the model.
IMPACT_FORCES = {
    # General Impacts
    "LOW (DROP)": 10,          # Dropping from a table
    "MEDIUM (STRIKE)": 50,     # A solid, deliberate strike
    
    # HEMA Sword Impacts
    "FEDER (LIGHT_TAP)": 30,   # A light, controlled tap
    "FEDER (FULL_STRIKE)": 150, # A powerful, committed feder strike
    "SABER (LIGHT_CUT)": 40,   # A quick, precise cut
    "SABER (HEAVY_CUT)": 120,  # A strong, forceful cut

    # Crush/Compression
    "CRUSH (MODERATE)": 200,   # Significant, steady pressure
}

def analyze_gcode(file_path):
    """
    Analyzes a G-code file to extract key printing parameters.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    # --- Default values ---
    infill_density = 0.20 # Default to 20%
    wall_count = 2
    layer_height = 0.2
    infill_pattern_name = "GRID" # Default pattern

    # --- Regex patterns for common slicers ---
    # Cura/PrusaSlicer often leave comments with settings
    infill_pattern = re.compile(r";\s*infill_percentage\s*=\s*(\d+\.?\d*)")
    wall_pattern = re.compile(r";\s*wall_line_count\s*=\s*(\d+)")
    layer_height_pattern = re.compile(r";\s*layer_height\s*=\s*(\d+\.?\d*)")
    infill_type_pattern = re.compile(r";\s*infill_pattern\s*=\s*(\w+)")

    # Search for parameters in the G-code
    infill_match = infill_pattern.search(content)
    if infill_match:
        infill_density = float(infill_match.group(1)) / 100.0

    wall_match = wall_pattern.search(content)
    if wall_match:
        wall_count = int(wall_match.group(1))

    layer_match = layer_height_pattern.search(content)
    if layer_match:
        layer_height = float(layer_match.group(1))

    infill_type_match = infill_type_pattern.search(content)
    if infill_type_match:
        infill_pattern_name = infill_type_match.group(1).upper()

    return {
        "infill_density": infill_density,
        "wall_count": wall_count,
        "layer_height": layer_height,
        "infill_pattern": infill_pattern_name
    }

def calculate_resistance_score(gcode_params, material_props):
    """
    Calculates a simplified impact resistance score.
    This is a heuristic model, not a precise physics simulation.
    """
    if not gcode_params or not material_props:
        return 0

    # --- Infill Pattern Strength Multipliers ---
    # Based on general knowledge of their structural properties.
    infill_strength_multipliers = {
        "GRID": 1.0,
        "LINES": 0.8,
        "TRIANGLES": 1.2,
        "CUBIC": 1.1,
        "GYROID": 1.3, # Known for good strength in all directions
        "DEFAULT": 1.0
    }
    infill_pattern = gcode_params.get("infill_pattern", "DEFAULT")
    strength_multiplier = infill_strength_multipliers.get(infill_pattern, 1.0)

    # Weighting factors for each parameter
    infill_weight = 0.4
    wall_weight = 0.5
    layer_adhesion_weight = 0.1

    # Normalize layer height effect (lower is generally better adhesion)
    layer_adhesion_factor = 1 - (gcode_params['layer_height'] / 0.5) # Assuming 0.5mm is a very high/weak layer height

    # Combine g-code parameters into a structural score
    structural_score = (
        (gcode_params['infill_density'] * infill_weight) +
        ((gcode_params['wall_count'] / 5.0) * wall_weight) + # Normalize against a baseline of 5 walls
        (layer_adhesion_factor * layer_adhesion_weight)
    )

    # Combine structural score with material properties
    resistance_score = structural_score * material_props['tensile_strength'] * material_props['impact_strength'] * strength_multiplier
    return resistance_score

def main():
    """
    Main function to run the impact analyzer.
    """
    parser = argparse.ArgumentParser(
        description="3D Print Impact Resistance Analyzer",
        add_help=False # Disable default help to create a custom one
    )

    # Custom help argument
    parser.add_argument(
        '-h', '-?', '--help',
        action='help',
        default=argparse.SUPPRESS,
        help='Show this help message and exit.'
    )

    # --- Argument Definitions ---
    parser.add_argument("--file", required=True, help="Path to the G-code file.")
    
    material_help = f"Printing material. Choices: {', '.join(MATERIALS.keys())}"
    parser.add_argument("--material", required=True, choices=MATERIALS.keys(), help=material_help)

    impact_help = f"Impact force level. Choices: {', '.join(IMPACT_FORCES.keys())}"
    parser.add_argument("--impact", default="MEDIUM (STRIKE)", choices=IMPACT_FORCES.keys(), help=impact_help)
    args = parser.parse_args()

    print("--- 3D Print Impact Analyzer ---")
    print(f"Analyzing file: {args.file}")
    print(f"Material: {args.material}")
    print(f"Assessing for impact level: {args.impact}")
    print("---------------------------------")

    gcode_params = analyze_gcode(args.file)
    if not gcode_params:
        return

    material_props = MATERIALS.get(args.material)
    impact_force = IMPACT_FORCES.get(args.impact)

    resistance_score = calculate_resistance_score(gcode_params, material_props)

    print(f"G-Code Parameters Found:")
    print(f"  - Infill Density: {gcode_params['infill_density']:.0%}")
    print(f"  - Wall Count: {gcode_params['wall_count']}")
    print(f"  - Layer Height: {gcode_params['layer_height']}mm")
    print(f"  - Infill Pattern: {gcode_params['infill_pattern']}")
    print("---------------------------------")
    print(f"Calculated Resistance Score: {resistance_score:.2f}")
    print(f"Impact Force to Resist: {impact_force}")
    print("---------------------------------")

    # --- Verdict ---
    if resistance_score > impact_force * 1.5:
        verdict = "LIKELY TO SURVIVE"
    elif resistance_score > impact_force * 0.8:
        verdict = "LIKELY TO BE DAMAGED"
    else:
        verdict = "LIKELY TO SHATTER"

    print(f"Verdict: {verdict}")
    print("---------------------------------")

    # --- Log to CSV ---
    log_file = os.path.join(os.path.dirname(__file__), 'impact_log.csv')
    log_header = [
        'Timestamp', 'File', 'Material', 'Impact Level', 'Infill Density', 
        'Wall Count', 'Layer Height', 'Resistance Score', 'Impact Force', 'Verdict'
    ]
    log_data = {
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'File': os.path.basename(args.file),
        'Material': args.material,
        'Impact Level': args.impact,
        'Infill Density': f"{gcode_params['infill_density']:.0%}",
        'Wall Count': gcode_params['wall_count'],
        'Layer Height': gcode_params['layer_height'],
        'Resistance Score': f"{resistance_score:.2f}",
        'Impact Force': impact_force,
        'Verdict': verdict
    }

    file_exists = os.path.isfile(log_file)
    with open(log_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=log_header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_data)
    
    print(f"Results logged to {log_file}")
    print("---------------------------------")

    print("\nDisclaimer: This is a simplified model and not a substitute for real-world testing or professional engineering analysis (FEA).")


if __name__ == "__main__":
    main()
