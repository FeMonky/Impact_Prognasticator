# ⚙️ The Aetheric Impact Prognosticator ⚙️

## Overview

The Aetheric Impact Prognosticator is a Python application designed to provide a simplified estimation of a 3D printed object's impact resistance. It analyzes G-code files, considers material properties, and assesses against various impact forces to predict whether a print is likely to survive, be damaged, or shatter.

## The Vibe-Coded Journey

This application was developed through an iterative, "vibe-coded" process, evolving from a simple command-line tool to a visually engaging steampunk-themed graphical interface. Key enhancements include:

*   **G-code Analysis:** Initial parsing of infill density, wall count, and layer height.
*   **Material Properties:** Integration of a basic material database (PLA, PETG, ABS, TPU).
*   **Impact Force Presets:** Refined and expanded impact scenarios, including specific HEMA sword strikes and crush forces.
*   **Advanced G-code Parameters:** Incorporation of infill pattern analysis (e.g., Gyroid, Cubic) for more accurate resistance scoring.
*   **CSV Logging:** Automatic recording of all analysis results to a `impact_log.csv` file for data collection and future analysis.
*   **Gradio Graphical User Interface (GUI):** A user-friendly web interface with file upload, dropdowns for parameters, and a visually distinct steampunk aesthetic for output presentation.

## Installation

To set up and run the Aetheric Impact Prognosticator, follow these steps:

1.  **Navigate to the Project Directory:**
    Open your terminal or command prompt and change to the `Impact_Analyzer` directory:
    ```bash
    cd D:\Impact_Analyzer
    ```

2.  **Create a Python Virtual Environment (Recommended):**
    A virtual environment isolates your project's dependencies from your system's Python installation.
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    *   **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    (You'll know it's active when `(venv)` appears at the beginning of your terminal prompt.)

4.  **Install Dependencies:**
    Install the required Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The Aetheric Impact Prognosticator can be used via both a Command-Line Interface (CLI) and a Graphical User Interface (GUI).

### Command-Line Interface (CLI)

The CLI tool (`impact_analyzer.py`) is useful for quick analyses or scripting.

**Basic Usage:**

```bash
python impact_analyzer.py --file <path_to_your_gcode_file> --material <MATERIAL> --impact <IMPACT_LEVEL>
```

**Arguments:**

*   `--file`: (Required) The absolute path to the `.gcode` file you want to analyze.
*   `--material`: (Required) The printing material.
    *   **Choices:** `PLA`, `PETG`, `ABS`, `TPU`
*   `--impact`: (Optional) The anticipated impact level. Defaults to `MEDIUM (STRIKE)`.
    *   **Choices:** `LOW (DROP)`, `MEDIUM (STRIKE)`, `FEDER (LIGHT_TAP)`, `FEDER (FULL_STRIKE)`, `SABER (LIGHT_CUT)`, `SABER (HEAVY_CUT)`, `CRUSH (MODERATE)`

**Examples:**

```bash
# Analyze a sample G-code with PLA and a full feder strike
python impact_analyzer.py --file "D:\Impact_Analyzer\sample_benchy.gcode" --material PLA --impact "FEDER (FULL_STRIKE)"

# Analyze a stronger print with PETG and a moderate crush force
python impact_analyzer.py --file "D:\Impact_Analyzer\strong_benchy.gcode" --material PETG --impact "CRUSH (MODERATE)"
```

**Viewing Help:**

To see all available options and their descriptions, use the help flag:

```bash
python impact_analyzer.py -?
# or
python impact_analyzer.py --help
```

### Graphical User Interface (GUI)

The Gradio-based GUI (`impact_ui.py`) provides an interactive web interface for easier use.

**To Launch the GUI:**

1.  Ensure your virtual environment is activated (as described in the Installation section).
2.  Run the GUI script:
    ```bash
    python impact_ui.py
    ```
3.  A local web server will start, and you will see a URL in your terminal (e.g., `http://127.0.0.1:7860`). Open this URL in your web browser.

**Using the GUI:**

*   **Upload G-code File:** Click the "Upload G-code File" box to select your `.gcode` file.
*   **Select Material:** Choose your printing material from the "Material" dropdown.
*   **Select Impact Level:** Choose the desired impact scenario from the "Impact Level" dropdown.
*   **Analyze:** Click the "Analyze Impact Resistance" button to get the prognosis.

## Disclaimer

This is a simplified heuristic model and is **not** a substitute for real-world physical testing or professional Finite Element Analysis (FEA). The results are intended to be used for comparative purposes (e.g., is this print likely to be stronger than another?) and not as a guarantee of performance.

## Data Sources

The values used in the `MATERIALS` and `IMPACT_FORCES` databases are simplified, illustrative estimates intended for this model. They are based on generally accepted ranges found in publicly available material datasheets and physics discussions.

### Material Properties

The tensile strength (MPa) and impact strength (kJ/m²) values are based on typical data ranges found in filament manufacturer datasheets and material science resources.

*   **General Filament Properties:** [Ultimaker - Material Properties](https://ultimaker.com/materials/materials-library)
*   **PLA, PETG, ABS Comparison:** [Instructables - PLA vs ABS vs PETG](https://www.instructables.com/PLA-vs-ABS-vs-PETG/)
*   **TPU Properties:** [MatterHackers - TPU](https://www.matterhackers.com/store/c/3d-printer-filament/tpu-thermoplastic-polyurethane)

### Impact Forces

The impact force presets (Joules) are estimates for the simulation. The HEMA-related values are inspired by discussions and articles regarding the physics of sword impacts.

*   **Sword Impact Energy:** [Thearma.org - The Measure of Blows](http://thearma.org/essays/measureofblows.htm)
*   **General Impact Physics:** [Wikipedia - Impact Force](https://en.wikipedia.org/wiki/Impact_force)
