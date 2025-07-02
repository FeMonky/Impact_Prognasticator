import gradio as gr
from impact_analyzer import analyze_gcode, calculate_resistance_score, MATERIALS, IMPACT_FORCES
import re
import os
from datetime import datetime
import csv
import time

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

#status_indicator .gradio-textbox {
    border: none !important;
    background: none !important;
    box-shadow: none !important;
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
    color: var(--dark-wood) !importan

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

    # --- Log to CSV ---
    log_file = os.path.join(os.path.dirname(__file__), 'impact_log.csv')
    log_header = [
        'Timestamp', 'File', 'Material', 'Impact Level', 'Infill Density', 
        'Wall Count', 'Layer Height', 'Infill Pattern', 'Resistance Score', 'Impact Force', 'Verdict'
    ]
    log_data = {
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'File': os.path.basename(gcode_file.name),
        'Material': material,
        'Impact Level': impact_level,
        'Infill Density': f"{gcode_params['infill_density']:.0%}",
        'Wall Count': gcode_params['wall_count'],
        'Layer Height': gcode_params['layer_height'],
        'Infill Pattern': gcode_params['infill_pattern'],
        'Resistance Score': f"{resistance_score:.2f}",
        'Impact Force': impact_force,
        'Verdict': verdict.split(' - ')[0]
    }

    file_exists = os.path.isfile(log_file)
    try:
        with open(log_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=log_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_data)
    except IOError as e:
        print(f"Error writing to log file: {e}")

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

def update_status():
    """Creates a blinking effect for the status indicator."""
    on_char = "<h3 style='color:#2E7D32; text-align: right; font-family: \"IM Fell English SC\", serif;'>● SYSTEM OPERATIONAL</h3>"
    off_char = "<h3 style='color:#555; text-align: right; font-family: \"IM Fell English SC\", serif;'>○ SYSTEM STANDBY</h3>"
    while True:
        # Blink off for a short period every few seconds
        yield off_char if int(time.time()) % 10 < 2 else on_char
        time.sleep(1)

# --- UI Layout ---
with gr.Blocks(css=steampunk_css) as iface:
    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown(
                """
                # ⚙️ The Aetheric Impact Prognosticator ⚙️
                Present your G-code schematics, select the material composition and the anticipated kinetic force to receive a calculated prognosis of structural integrity.
                """
            )
        with gr.Column(scale=1):
            status_indicator = gr.HTML()

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
    iface.load(
        fn=update_status,
        inputs=None,
        outputs=[status_indicator]
    )

    analyze_button.click(
        fn=run_analysis,
        inputs=[gcode_uploader, material_dropdown, impact_dropdown],
        outputs=[params_output, results_output, verdict_output]
    )

if __name__ == "__main__":
    iface.launch()
