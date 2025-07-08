from flask import Flask, render_template
from api.methods import metodo_grafico
from flask import request, jsonify

methods_available = {
    "Graphical Method": "Graphical Method",
    "Simplex Method": "Simplex Method",
}

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/resolver', methods=['POST'])
def resolver():
    print("Content-Type recibido:", request.content_type)

    data = request.get_json()
    type_of_method = data.get("method")
    objective_function = data.get("objectiveFunction")
    constraints = data.get("constraints")
    type_of_problem = data.get("problemType")
    boolean_type = None

    print("Type of method:", type_of_method)
    print("Objective function:", objective_function)
    print("Constraints:", constraints)
    print("Type of problem:", type_of_problem)

    if type_of_problem == "max":
        boolean_type = True
    else:
        boolean_type = False

    print("Boolean type:", boolean_type)

    return jsonify({"message": "Datos recibidos correctamente"}), 200
        
if __name__ == '__main__':
    app.run(debug=True)