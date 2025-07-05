import numpy as np
import plotly.graph_objs as go
from scipy.optimize import linprog

def metodo_grafico(objetivo, restricciones, limites, maximizar=True):
    x_min, x_max, y_min, y_max = limites
    x = np.linspace(x_min, x_max, 400)
    y = np.linspace(y_min, y_max, 400)
    X, Y = np.meshgrid(x, y)

    # Máscara de la región factible
    mascara = np.ones_like(X, dtype=bool)
    for a, b, cst, sentido in restricciones:
        if sentido == '<=':
            mascara &= (a * X + b * Y <= cst)
        elif sentido == '>=':
            mascara &= (a * X + b * Y >= cst)
        elif sentido == '=':
            mascara &= np.isclose(a * X + b * Y, cst, atol=1e-3)

    # Graficar restricciones (trazos más cortos)
    fig = go.Figure()
    for a, b, cst, sentido in restricciones:
        if b != 0:
            y_vals = (cst - a * x) / b
            mask = (y_vals >= y_min) & (y_vals <= y_max)
            estilo = 'dash' if sentido != '=' else 'solid'
            fig.add_trace(go.Scatter(
                x=x[mask], y=y_vals[mask], mode='lines',
                name=f"{a}x + {b}y {sentido} {cst}",
                line=dict(dash=estilo)
            ))
        else:
            x_val = cst / a
            if x_min <= x_val <= x_max:
                estilo = 'dash' if sentido != '=' else 'solid'
                fig.add_trace(go.Scatter(
                    x=[x_val, x_val], y=[y_min, y_max], mode='lines',
                    name=f"x = {x_val}",
                    line=dict(dash=estilo)
                ))

    # Graficar región factible
    fig.add_trace(go.Contour(
        x=x, y=y, z=mascara.astype(int),
        showscale=False, opacity=0.3, colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'lightgreen']],
        hoverinfo='skip', name='Región factible'
    ))

    # Preparar restricciones para linprog
    c = np.array(objetivo)
    if maximizar:
        c = -c
    A_ub = []
    b_ub = []
    A_eq = []
    b_eq = []
    for a, b, cst, sentido in restricciones:
        if sentido == '<=':
            A_ub.append([a, b])
            b_ub.append(cst)
        elif sentido == '>=':
            A_ub.append([-a, -b])
            b_ub.append(-cst)
        elif sentido == '=':
            A_eq.append([a, b])
            b_eq.append(cst)
    res = linprog(c, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None,
                  A_eq=A_eq if A_eq else None, b_eq=b_eq if b_eq else None,
                  bounds=[(x_min, x_max), (y_min, y_max)])
    if res.success:
        x_opt, y_opt = res.x
        valor_opt = np.dot(objetivo, res.x)
        fig.add_trace(go.Scatter(
            x=[x_opt], y=[y_opt], mode='markers+text',
            marker=dict(color='red', size=12),
            text=[f"Óptimo ({x_opt:.2f}, {y_opt:.2f})<br>Valor: {valor_opt:.2f}"],
            textposition="top right",
            name='Solución óptima'
        ))
        fig.update_layout(
            title='Programación Lineal (Método Gráfico)',
            xaxis_title='x',
            yaxis_title='y',
            legend=dict(x=0.01, y=0.99)
        )
        fig.show()
        print(f"Punto óptimo: x = {x_opt:.2f}, y = {y_opt:.2f}")
        print(f"Valor óptimo: {valor_opt:.2f}")
        return (x_opt, y_opt), valor_opt
    else:
        fig.update_layout(
            title='Programación Lineal (Método Gráfico)',
            xaxis_title='x',
            yaxis_title='y',
            legend=dict(x=0.01, y=0.99)
        )
        fig.show()
        print("No se encontró solución factible.")
        return None, None
