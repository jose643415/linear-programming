import numpy as np
import plotly.graph_objs as go
from scipy.optimize import linprog
from plotly.io import to_html
import pandas as pd
from IPython.display import display, clear_output
import time

def metodo_grafico(objetivo, restricciones, limites=(0,10,0,10), maximizar=True):
    x_min, x_max, y_min, y_max = limites
    x = np.linspace(x_min, x_max, 400)
    y = np.linspace(y_min, y_max, 400)
    X, Y = np.meshgrid(x, y)

    # Crear máscara para la región factible
    mascara = np.ones_like(X, dtype=bool)
    for a, b, cst, sentido in restricciones:
        if sentido == '<=':
            mascara &= (a * X + b * Y <= cst)
        elif sentido == '>=':
            mascara &= (a * X + b * Y >= cst)
        elif sentido == '=':
            mascara &= np.isclose(a * X + b * Y, cst, atol=1e-3)

    fig = go.Figure()
    
    # Dibujar las líneas de restricción CORREGIDO
    for i, (a, b, cst, sentido) in enumerate(restricciones):
        if b != 0:  # Línea no vertical
            # Calcular y para los límites de x
            y_start = (cst - a * x_min) / b
            y_end = (cst - a * x_max) / b
            
            # Encontrar los puntos de intersección con los límites del gráfico
            puntos_interseccion = []
            
            # Intersección con x = x_min
            y_at_xmin = (cst - a * x_min) / b
            if y_min <= y_at_xmin <= y_max:
                puntos_interseccion.append((x_min, y_at_xmin))
            
            # Intersección con x = x_max
            y_at_xmax = (cst - a * x_max) / b
            if y_min <= y_at_xmax <= y_max:
                puntos_interseccion.append((x_max, y_at_xmax))
            
            # Intersección con y = y_min
            if a != 0:
                x_at_ymin = (cst - b * y_min) / a
                if x_min <= x_at_ymin <= x_max:
                    puntos_interseccion.append((x_at_ymin, y_min))
            
            # Intersección con y = y_max
            if a != 0:
                x_at_ymax = (cst - b * y_max) / a
                if x_min <= x_at_ymax <= x_max:
                    puntos_interseccion.append((x_at_ymax, y_max))
            
            # Eliminar duplicados y ordenar
            puntos_interseccion = list(set(puntos_interseccion))
            
            if len(puntos_interseccion) >= 2:
                # Tomar solo los primeros 2 puntos para dibujar la línea
                puntos_interseccion = sorted(puntos_interseccion)[:2]
                x_vals = [p[0] for p in puntos_interseccion]
                y_vals = [p[1] for p in puntos_interseccion]
                
                estilo = 'dash' if sentido != '=' else 'solid'
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, mode='lines',
                    name=f"{a}x + {b}y {sentido} {cst}",
                    line=dict(dash=estilo, width=2)
                ))
        
        else:  # Línea vertical (b = 0)
            if a != 0:
                x_val = cst / a
                if x_min <= x_val <= x_max:
                    estilo = 'dash' if sentido != '=' else 'solid'
                    fig.add_trace(go.Scatter(
                        x=[x_val, x_val], y=[y_min, y_max], mode='lines',
                        name=f"x = {x_val}",
                        line=dict(dash=estilo, width=2)
                    ))

    # Añadir la región factible
    fig.add_trace(go.Contour(
        x=x, y=y, z=mascara.astype(int),
        showscale=False, opacity=0.5, 
        colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'lightgreen']],
        hoverinfo='skip', name='Región factible',
        contours=dict(coloring='fill', showlines=False)
    ))

    # Resolver el problema de optimización
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
        
        # Añadir punto óptimo
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
            legend=dict(x=0.01, y=0.99),
            xaxis=dict(range=[x_min, x_max]),
            yaxis=dict(range=[y_min, y_max])
        )
        
        plot_html = to_html(fig, full_html=False)
        return {
            "plot_html": plot_html,
            "solucion": (x_opt, y_opt),
            "valor_optimo": valor_opt,
            "restricciones": restricciones,
            "objetivo": objetivo
        }
    else:
        fig.update_layout(
            title='Programación Lineal (Método Gráfico)',
            xaxis_title='x',
            yaxis_title='y',
            legend=dict(x=0.01, y=0.99),
            xaxis=dict(range=[x_min, x_max]),
            yaxis=dict(range=[y_min, y_max])
        )
        
        plot_html = to_html(fig, full_html=False)
        return {
            "plot_html": plot_html,
            "solucion": None,
            "valor_optimo": None,
            "restricciones": restricciones,
            "objetivo": objetivo
        }

def mostrar_tableau(tableau, var_names, basic_vars, iteration, pivot_row=None, pivot_col=None, pause_time=2):
    clear_output(wait=True)
    print(f"\n--- Iteración {iteration} ---\n")
    df = pd.DataFrame(tableau)
    df.columns = var_names + ['Solución']
    df.index = [f"BV_{var_names[i]}" for i in basic_vars] + ['Z']

    def highlight_table_full(data):
        styles = pd.DataFrame('', index=data.index, columns=data.columns)
        if pivot_row is not None and pivot_col is not None:
            styles.iloc[pivot_row, :] = 'background-color: lightyellow'
            styles.iloc[:, pivot_col] = 'background-color: lightblue'
            styles.iloc[pivot_row, pivot_col] = 'background-color: green; color: white'
        return styles

    styled = df.style.apply(highlight_table_full, axis=None)
    display(styled.set_caption("Tableau Simplex"))
    time.sleep(pause_time)

class SimplexBigM:
    def __init__(self, objetivo, restricciones, maximizar=True, M=1e5):
        self.objetivo = np.array(objetivo, dtype=float)
        self.restricciones = restricciones
        self.maximizar = maximizar
        self.M = M
        self.var_names = [f"x{i+1}" for i in range(len(objetivo))]
        self.basic_vars = []
        self.tableau = None

    def setup(self):
        n_original = len(self.objetivo)
        A_rows = []
        b = []
        signos = []

        slack_count = 0
        surplus_count = 0
        artificial_count = 0
        row_types = []

        for restr in self.restricciones:
            signo = restr[-1]
            if signo == '<=':
                slack_count += 1
                row_types.append('slack')
            elif signo == '>=':
                surplus_count += 1
                artificial_count += 1
                row_types.append('surplus_artificial')
            elif signo == '=':
                artificial_count += 1
                row_types.append('artificial')

        total_extra_cols = slack_count + surplus_count + artificial_count
        total_vars = n_original + total_extra_cols

        # Build variable names
        slack_num = surplus_num = artificial_num = 0
        extra_var_names = []
        for typ in row_types:
            if typ == 'slack':
                slack_num += 1
                extra_var_names.append(f"s{slack_num}")
            elif typ == 'surplus_artificial':
                surplus_num += 1
                artificial_num += 1
                extra_var_names.append(f"e{surplus_num}")
                extra_var_names.append(f"a{artificial_num}")
            elif typ == 'artificial':
                artificial_num += 1
                extra_var_names.append(f"a{artificial_num}")

        self.var_names += extra_var_names

        # Build A matrix
        slack_num = surplus_num = artificial_num = 0
        basic_var_pos = []
        for idx, restr in enumerate(self.restricciones):
            coefs = list(restr[:-2])
            rhs = restr[-2]
            signo = restr[-1]
            fila = coefs + [0]*total_extra_cols

            if signo == '<=':
                fila[n_original + slack_num] = 1
                basic_var_pos.append(n_original + slack_num)
                slack_num += 1
            elif signo == '>=':
                fila[n_original + slack_num] = -1
                fila[n_original + slack_count + surplus_num] = 1
                basic_var_pos.append(n_original + slack_count + surplus_num)
                slack_num += 1
                surplus_num += 1
            elif signo == '=':
                fila[n_original + slack_count + surplus_count + artificial_num] = 1
                basic_var_pos.append(n_original + slack_count + surplus_count + artificial_num)
                artificial_num += 1

            A_rows.append(fila)
            b.append(rhs)

        A = np.array(A_rows, dtype=float)
        b = np.array(b, dtype=float)

        # Build c with Big M penalties
        c = list(self.objetivo) + [0]*total_extra_cols
        artificial_pos = []
        surplus_num = artificial_num = 0
        for typ in row_types:
            if typ == 'slack':
                pass
            elif typ == 'surplus_artificial':
                artificial_pos.append(n_original + slack_count + surplus_num)
                surplus_num += 1
                artificial_num += 1
            elif typ == 'artificial':
                artificial_pos.append(n_original + slack_count + surplus_count + artificial_num)
                artificial_num += 1

        for idx in artificial_pos:
            if self.maximizar:
                c[idx] = -self.M
            else:
                c[idx] = self.M

        c = np.array(c, dtype=float)
        if self.maximizar:
            c = -c

        last_row = np.append(c, 0)
        tableau = np.hstack((A, b.reshape(-1,1)))
        tableau = np.vstack((tableau, last_row))
        self.tableau = tableau
        self.basic_vars = basic_var_pos

    def solve(self, pause_time=2):
        self.setup()
        iteration = 0

        while True:
            iteration += 1
            mostrar_tableau(self.tableau.copy(), self.var_names, self.basic_vars, iteration, pause_time=pause_time)

            last_row = self.tableau[-1, :-1]
            if (self.maximizar and all(last_row >= -1e-8)) or (not self.maximizar and all(last_row <= 1e-8)):
                break

            if self.maximizar:
                entering = np.argmin(last_row)
            else:
                entering = np.argmax(last_row)

            ratios = []
            for i in range(len(self.tableau)-1):
                col_val = self.tableau[i, entering]
                if col_val > 1e-8:
                    ratios.append(self.tableau[i, -1] / col_val)
                else:
                    ratios.append(np.inf)

            leaving = np.argmin(ratios)
            if ratios[leaving] == np.inf:
                print("¡Problema no acotado!")
                return

            self.basic_vars[leaving] = entering

            # Show tableau with pivot highlighting
            mostrar_tableau(self.tableau.copy(), self.var_names, self.basic_vars, iteration, pivot_row=leaving, pivot_col=entering, pause_time=pause_time)

            pivot = self.tableau[leaving, entering]
            self.tableau[leaving, :] /= pivot
            for i in range(self.tableau.shape[0]):
                if i != leaving:
                    self.tableau[i, :] -= self.tableau[i, entering] * self.tableau[leaving, :]

        mostrar_tableau(self.tableau.copy(), self.var_names, self.basic_vars, iteration+1, pause_time=pause_time)
        z = self.tableau[-1, -1]
        if self.maximizar:
            z = -z

        sol = np.zeros(len(self.var_names))
        for i, var in enumerate(self.basic_vars):
            sol[var] = self.tableau[i, -1]

        print("\n====== RESULTADO FINAL ======")
        print(f"Valor óptimo Z = {z}")
        print("Solución óptima:")
        for i, name in enumerate(self.var_names[:len(self.objetivo)]):
            print(f"{name} = {sol[i]}")
