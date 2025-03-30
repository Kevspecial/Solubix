import logging
from flask import Flask, render_template, request, jsonify
import plotly.graph_objects as go
import numpy as np
import math
from data.solvents import SOLVENTS
from data.solutes import SOLUTES

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# API Endpoints --------------------------------------------------------------
@app.route('/api/SOLVENTS')
def get_solvents():
    """Return JSON data of all available solvents"""
    return jsonify(SOLVENTS)

@app.route('/api/SOLUTES')
def get_solutes():
    """Return JSON data of all available solutes"""
    return jsonify(SOLUTES)

@app.route("/api/search_solvents", methods=["GET"])
def search_solvents():
    """Search solvents by name"""
    query = request.args.get("q", "").lower()
    logger.debug("Search solvents query: '%s'", query)
    results = [{"name": name} for name in SOLVENTS if query in name.lower()]
    return jsonify(results)

@app.route("/api/calculate", methods=["POST"])
def calculate():
    """Main calculation endpoint"""
    try:
        data = request.get_json()
        logger.debug("Received calculation request: %s", data)
        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Get and validate solute parameters
        try:
            solute = get_solute_from_request(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if solute["ro"] <= 0:
            return jsonify({"error": "Ro must be positive"}), 400

        # Get and validate solvents
        selected_solvents = data.get("solvents", [])
        if not selected_solvents:
            return jsonify({"error": "No solvents selected"}), 400

        # Get temperature parameter
        temperature = float(data.get('temperature', 25.0))

        # Process calculations
        results = {}
        plot_data = {"solvents": [], "d_values": [], "p_values": [], "h_values": [], "colors": []}
        temp_data = {"temperatures": np.linspace(0, 100, 101).tolist(), "solubilities": {}}

        for solvent_name in selected_solvents:
            solvent = SOLVENTS.get(solvent_name)
            if not solvent:
                logger.warning("Solvent %s not found", solvent_name)
                continue

            # Calculate base solubility parameters
            ra = calculate_distance(solute, solvent)
            red = ra / solute["ro"]
            solubility, color = get_solubility_status(red)
            
            # Apply temperature correction
            base_solubility = 1/red  # Inverse relationship between RED and solubility
            temp_corrected_solubility = base_solubility * (1 + 0.02 * (temperature - 25))
            
            # Store results
            results[solvent_name] = {
                "d": solvent["d"],
                "p": solvent["p"],
                "h": solvent["h"],
                "ra": round(ra, 2),
                "red": round(red, 2),
                "solubility": solubility,
                "temp_corrected_solubility": round(temp_corrected_solubility, 4)
            }

            # Store temperature-dependent values
            temp_data["solubilities"][solvent_name] = [
                base_solubility * (1 + 0.02 * (t - 25)) 
                for t in temp_data["temperatures"]
            ]

            # Collect plot data
            plot_data["solvents"].append(solvent_name)
            plot_data["d_values"].append(solvent["d"])
            plot_data["p_values"].append(solvent["p"])
            plot_data["h_values"].append(solvent["h"])
            plot_data["colors"].append(color)

        # Generate 3D plot
        plot_json = create_3d_plot(plot_data, solute)
        
        return jsonify({
            "results": results, 
            "plot_json": plot_json,
            "temp_data": temp_data
        })

    except Exception as e:
        logger.error("Error in calculate: %s", str(e))
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500

# Helper Functions -----------------------------------------------------------
def calculate_distance(solute, solvent):
    """Calculate Hansen solubility distance (Ra)"""
    try:
        return math.sqrt(
            4 * (solute["d"] - solvent["d"])**2 +
            (solute["p"] - solvent["p"])**2 +
            (solute["h"] - solvent["h"])**2
        )
    except KeyError as e:
        raise ValueError(f"Missing HSP parameter: {e}")

def get_solute_from_request(data):
    """Validate and retrieve solute parameters"""
    solute_name = data.get("solute_name")
    if solute_name and solute_name in SOLUTES:
        return SOLUTES[solute_name]
    
    try:
        return {
            "d": float(data["solute_d"]),
            "p": float(data["solute_p"]),
            "h": float(data["solute_h"]),
            "ro": float(data["solute_ro"])
        }
    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid solute parameters: {str(e)}")

def get_solubility_status(red_value):
    """Determine solubility status from RED value"""
    if red_value <= 1: return "Soluble", "green"
    if red_value <= 1.5: return "Partially Soluble", "orange"
    return "Insoluble", "red"

def create_3d_plot(plot_data, solute=None):
    """Generate 3D plot using Plotly"""
    fig = go.Figure()

    # Add solvent points
    fig.add_trace(go.Scatter3d(
        x=plot_data["d_values"],
        y=plot_data["p_values"],
        z=plot_data["h_values"],
        mode="markers+text",
        marker=dict(size=10, color=plot_data["colors"], colorscale="Viridis"),
        text=plot_data["solvents"],
        hovertext=[f"{name}: δD={d:.1f}, δP={p:.1f}, δH={h:.1f}"
                   for name, d, p, h in zip(plot_data["solvents"], 
                                          plot_data["d_values"],
                                          plot_data["p_values"],
                                          plot_data["h_values"])],
        name="Solvents"
    ))

    # Add solute visualization if provided
    if solute:
        add_solute_to_plot(fig, solute)

    fig.update_layout(
        scene=dict(
            xaxis_title="δD (Dispersion)",
            yaxis_title="δP (Polar)",
            zaxis_title="δH (Hydrogen Bonding)",
            aspectmode='cube',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=600
    )
    
    return fig.to_json()

def add_solute_to_plot(fig, solute):
    """Add solute and solubility sphere to plot"""
    fig.add_trace(go.Scatter3d(
        x=[solute["d"]], y=[solute["p"]], z=[solute["h"]],
        mode="markers+text",
        marker=dict(size=14, color="blue", symbol="diamond"),
        text=["Solute"],
        hovertext=f"Solute: δD={solute['d']:.1f}, δP={solute['p']:.1f}, δH={solute['h']:.1f}",
        name="Solute"
    ))

    if "ro" in solute:
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = solute["ro"] * np.cos(u)*np.sin(v) + solute["d"]
        y = solute["ro"] * np.sin(u)*np.sin(v) + solute["p"]
        z = solute["ro"] * np.cos(v) + solute["h"]
        
        fig.add_trace(go.Surface(
            x=x, y=y, z=z, opacity=0.2,
            colorscale=[[0, 'blue'], [1, 'blue']],
            showscale=False,
            name="Solubility Sphere"
        ))

# Main Routes -----------------------------------------------------------------
@app.route("/")
def index():
    """Serve main application page"""
    return render_template("index.html", 
                         solvents=sorted(SOLVENTS.keys()),
                         solutes=SOLUTES)

if __name__ == "__main__":
    app.run(debug=True)