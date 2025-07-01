import gradio as gr
import re
import os
from datetime import datetime
import csv

# --- Core Analysis Logic (copied from impact_analyzer.py) ---

# Material Properties Database
MATERIALS = {
    "PLA": {"tensile_strength": 50, "impact_strength": 5},
    "PETG": {"tensile_strength": 45, "impact_strength": 8},
    "ABS": {"tensile_strength": 40, "impact_strength": 10},
    "TPU": {"tensile_strength": 35, "impact_strength": 30},
}

# Impact Force Presets
IMPACT_FORCES = {
    "LOW (DROP)": 10,
    "MEDIUM (STRIKE)": 50,
    "FEDER (LIGHT_TAP)": 30,
    "FEDER (FULL_STRIKE)": 150,
    "SABER (LIGHT_CUT)": 40,
    "SABER (HEAVY_CUT)": 120,
    "CRUSH (MODERATE)": 200,
}

def analyze_gcode(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (FileNotFoundError, TypeError):
        return None

    infill_density = 0.20
    wall_count = 2
    layer_height = 0.2
    infill_pattern_name = "GRID"

    infill_pattern = re.compile(r";\s*infill_percentage\s*=\s*(\d+\.?\d*)")
    wall_pattern = re.compile(r";\s*wall_line_count\s*=\s*(\d+)")
    layer_height_pattern = re.compile(r";\s*layer_height\s*=\s*(\d+\.?\d*)")
    infill_type_pattern = re.compile(r";\s*infill_pattern\s*=\s*(\w+)")

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
    if not gcode_params or not material_props:
        return 0

    infill_strength_multipliers = {
        "GRID": 1.0, "LINES": 0.8, "TRIANGLES": 1.2,
        "CUBIC": 1.1, "GYROID": 1.3, "DEFAULT": 1.0
    }
    infill_pattern = gcode_params.get("infill_pattern", "DEFAULT")
    strength_multiplier = infill_strength_multipliers.get(infill_pattern, 1.0)

    infill_weight = 0.4
    wall_weight = 0.5
    layer_adhesion_weight = 0.1

    layer_adhesion_factor = 1 - (gcode_params['layer_height'] / 0.5)

    structural_score = (
        (gcode_params['infill_density'] * infill_weight) +
        ((gcode_params['wall_count'] / 5.0) * wall_weight) +
        (layer_adhesion_factor * layer_adhesion_weight)
    )

    resistance_score = structural_score * material_props['tensile_strength'] * material_props['impact_strength'] * strength_multiplier
    return resistance_score

# --- Steampunk Theming ---

steampunk_css = """
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&display=swap');

:root {
    --bronze: #8B4513;
    --copper: #B87333;
    --brass: #D4AF37;
    --dark-wood: #3A241D;
    --off-white: #F5F5DC;
}

.gradio-container { 
    background-color: var(--dark-wood);
    font-family: 'IM Fell English SC', serif;
}

h2 {
    font-family: 'IM Fell English SC', serif !important;
    color: var(--off-white) !important;
    font-size: 1.8em !important; /* Slightly larger for main headings */
}

h3 {
    font-family: 'IM Fell English SC', serif !important;
    color: var(--off-white) !important;
    font-size: 1.4em !important; /* Slightly larger for subheadings */
}

.gr-button, .gr-dropdown, .gr-file {
    font-family: 'IM Fell English SC', serif !important;
    color: var(--off-white) !important;
    font-size: 1.1em !important; /* Slightly larger for input elements */
}

/* Adjust font size for list items in the output */
.gradio-container ul li {
    font-size: 1.1em !important;
}

.gr-button {
    background-color: var(--bronze) !important;
    border: 2px solid var(--copper) !important;
    box-shadow: 3px 3px 5px rgba(0,0,0,0.5);
}

.gr-button:hover {
    background-color: var(--copper) !important;
    border-color: var(--brass) !important;
}

.gr-panel {
    background-color: #4a302a !important;
    border: 2px solid var(--bronze) !important;
}

.gr-input, .gr-dropdown, .gr-file-label {
    background-color: var(--off-white) !important;
    color: var(--dark-wood) !important;
    border: 1px solid var(--bronze) !important;
}

"""

# --- Gradio Interface Logic ---

def run_analysis(gcode_file, material, impact_level):
    """Processes the inputs from the Gradio interface and returns formatted output."""
    if gcode_file is None:
        return "<p style='color:red;font-family:sans-serif;''>Please upload a G-code file.</p>", "", ""

    gcode_params = analyze_gcode(gcode_file.name)
    if not gcode_params:
        return "<p style='color:red;font-family:sans-serif;''>Could not parse the G-code file. Make sure it contains standard slicer settings in comments.</p>", "", ""

    material_props = MATERIALS.get(material)
    impact_force = IMPACT_FORCES.get(impact_level)
    resistance_score = calculate_resistance_score(gcode_params, material_props)

    # Determine verdict and color
    if resistance_score > impact_force * 1.5:
        verdict = "ROBUST - LIKELY TO SURVIVE"
        verdict_bg = "#2E4638"
    elif resistance_score > impact_force * 0.8:
        verdict = "DAMAGED - LIKELY TO BE COMPROMISED"
        verdict_bg = "#5A4D2B"
    else:
        verdict = "FRAGILE - LIKELY TO SHATTER"
        verdict_bg = "#5A2B2B"

    # --- Create Steampunk HTML output ---
    params_html = f"""
    <div style='background-color: #4a302a; border: 3px solid #8B4513; padding: 15px; border-radius: 5px; box-shadow: 5px 5px 10px rgba(0,0,0,0.5); margin-bottom: 20px;'>
        <h3 style='color:#F5F5DC; text-align:center; border-bottom: 2px solid #8B4513; padding-bottom: 5px;'>Cogitator's Analysis</h3>
        <ul style='list-style-type: none; padding-left: 0; color: #F5F5DC;'>
            <li style='margin-bottom: 10px;'><strong>Infill Density:</strong> {gcode_params['infill_density']:.0%}</li>
            <li style='margin-bottom: 10px;'><strong>Wall Perimeters:</strong> {gcode_params['wall_count']}</li>
            <li style='margin-bottom: 10px;'><strong>Layer Strata:</strong> {gcode_params['layer_height']}mm</li>
            <li><strong>Infill Configuration:</strong> {gcode_params['infill_pattern']}</li>
        </ul>
    </div>
    """

    results_html = f"""
    <div style='background-color: #4a302a; border: 3px solid #8B4513; padding: 15px; border-radius: 5px; box-shadow: 5px 5px 10px rgba(0,0,0,0.5);'>
        <h3 style='color:#F5F5DC; text-align:center; border-bottom: 2px solid #8B4513; padding-bottom: 5px;'>Calculated Prognosis</h3>
        <ul style='list-style-type: none; padding-left: 0; color: #F5F5DC;'>
            <li style='margin-bottom: 10px;'><strong>Resistance Quotient:</strong> {resistance_score:.2f}</li>
            <li><strong>Anticipated Impact Force:</strong> {impact_force}</li>
        </ul>
    </div>
    """

    verdict_html = f"""
    <div style='background-color: {verdict_bg}; border: 5px solid #D4AF37; text-align:center; padding: 20px; border-radius: 10px; box-shadow: inset 0 0 15px rgba(0,0,0,0.7); margin-top: 20px;'>
        <h2 style='color:#F5F5DC; margin:0; text-shadow: 2px 2px 4px #000;'>{verdict}</h2>
    </div>
    """

    return params_html, results_html, verdict_html

# --- UI Layout ---
with gr.Blocks(css=steampunk_css) as iface:
    gr.Markdown(
        """
        # ⚙️ The Aetheric Impact Prognosticator ⚙️
        Present your G-code schematics, select the material composition and the anticipated kinetic force to receive a calculated prognosis of structural integrity.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            gcode_uploader = gr.File(label="Upload G-code File", file_types=['.gcode'])
            material_dropdown = gr.Dropdown(label="Material", choices=list(MATERIALS.keys()), value="PLA")
            impact_dropdown = gr.Dropdown(label="Impact Level", choices=list(IMPACT_FORCES.keys()), value="MEDIUM (STRIKE)")
            analyze_button = gr.Button("Analyze Impact Resistance", variant="primary")

        with gr.Column(scale=2):
            gr.Markdown("### Analysis Output")
            verdict_output = gr.HTML()
            with gr.Row():
                params_output = gr.HTML()
                results_output = gr.HTML()
    
    gr.Markdown("**Disclaimer:** This is a simplified model and not a substitute for real-world testing or professional engineering analysis (FEA).")

    # --- Event Handling ---
    analyze_button.click(
        fn=run_analysis,
        inputs=[gcode_uploader, material_dropdown, impact_dropdown],
        outputs=[params_output, results_output, verdict_output]
    )

if __name__ == "__main__":
    iface.launch()