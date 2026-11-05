"""Genera assets/metodo_grafico_preview.png: vista fija del método gráfico.

Usa los mismos datos del modelo que la página interactiva. Los vértices de la
región factible se calculan (intersecciones de pares de rectas + filtro de
factibilidad), no se escriben a mano.

Uso:  python scripts/generar_vista_previa.py
"""
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Modelo: max 280.000 x1 + 210.000 x2  s.a.  a·x1 + b·x2 <= capacidad
MARGEN = (280_000, 210_000)
RESTRICCIONES = [  # nombre, a, b, capacidad, color, estilo
    ("Análisis", 1.6, 1.0, 40, "#2a78d6", "-"),
    ("Validación", 2.4, 1.2, 48, "#eb6834", "--"),
    ("Cierre", 0.8, 1.8, 36, "#1baf7a", ":"),
]
X1_MAX, X2_MAX, EPS = 30, 42, 1e-9


def factible(x1, x2):
    return x1 >= -EPS and x2 >= -EPS and all(a * x1 + b * x2 <= c + EPS for _, a, b, c, *_ in RESTRICCIONES)


def es(v, dec=2):
    """Número en formato español: punto de miles y coma decimal."""
    return f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Rectas a·x1 + b·x2 = c: las tres restricciones y los dos ejes
rectas = [(a, b, c) for _, a, b, c, *_ in RESTRICCIONES] + [(1, 0, 0), (0, 1, 0)]
vertices = []
for (a1, b1, c1), (a2, b2, c2) in combinations(rectas, 2):
    det = a1 * b2 - a2 * b1
    if abs(det) < EPS:
        continue
    p = ((c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det)
    if factible(*p) and not any(np.hypot(p[0] - q[0], p[1] - q[1]) < 1e-7 for q in vertices):
        vertices.append(p)
cx, cy = np.mean(vertices, axis=0)
vertices.sort(key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))
z = lambda p: MARGEN[0] * p[0] + MARGEN[1] * p[1]
opt = max(vertices, key=z)
enteros = [(i, j) for i in range(X1_MAX + 1) for j in range(X2_MAX + 1) if factible(i, j)]
opt_ent = max(enteros, key=z)

fig, ax = plt.subplots(figsize=(9, 6.6), dpi=150)
ax.fill(*zip(*vertices), color="#6250d6", alpha=0.13, label="Región factible")
ax.scatter(*zip(*enteros), s=5, color="#898781", zorder=2)
x = np.linspace(0, X1_MAX, 400)
for nombre, a, b, c, color, estilo in RESTRICCIONES:
    ax.plot(x, (c - a * x) / b, estilo, color=color, lw=2.4, label=f"{nombre}: {es(a,1)}·x₁ + {es(b,1)}·x₂ ≤ {c}")
ax.plot(x, (z(opt) - MARGEN[0] * x) / MARGEN[1], color="#52514e", lw=1.2, ls=(0, (5, 4)), label="Isomargen Z = $6.600.000")
ax.scatter(*opt, s=90, color="#0b0b0b", zorder=5, edgecolor="white", linewidth=2)
caja = dict(boxstyle="round,pad=0.35", fc="white", ec="#d3d1c7", alpha=0.95)
flecha = dict(arrowstyle="-", color="#888780", lw=1)
ax.annotate(f"Óptimo continuo ({es(opt[0])}; {es(opt[1])})\nZ = ${es(z(opt),0)}", opt, xytext=(19, 21),
            fontsize=10, fontweight="bold", bbox=caja, arrowprops=flecha)
ax.scatter(*opt_ent, s=70, marker="s", color="#6250d6", zorder=6, edgecolor="white", linewidth=1.5)
ax.annotate(f"Óptimo entero ({opt_ent[0]}; {opt_ent[1]})\nZ = ${es(z(opt_ent),0)} (antes del costo fijo)", opt_ent,
            xytext=(1.2, 7.5), fontsize=9.5, color="#6250d6", bbox=caja, arrowprops=flecha)
ax.scatter([13], [15], s=70, facecolor="white", edgecolor="#d03b3b", linewidth=2, zorder=6)
ax.annotate("(13; 15) no factible:\nse pasa en Validación y Cierre", (13, 15), xytext=(14.5, 27.5),
            fontsize=9, color="#d03b3b", bbox=caja, arrowprops=flecha)
ax.set(xlim=(0, X1_MAX), ylim=(0, X2_MAX), xlabel="x₁ = solicitudes Estándar por día",
       ylabel="x₂ = solicitudes Prioritarias por día", title="Método gráfico · Centro de Procesamiento de Servicios")
ax.grid(color="#e1e0d9", lw=0.8)
ax.set_axisbelow(True)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
ax.legend(loc="upper right", fontsize=8.5, frameon=False)
fig.tight_layout()
salida = Path(__file__).resolve().parent.parent / "assets" / "metodo_grafico_preview.png"
salida.parent.mkdir(exist_ok=True)
fig.savefig(salida)
print(f"Vértices: {[(round(a, 3), round(b, 3)) for a, b in vertices]}")
print(f"Óptimo continuo: {opt} · Z = {z(opt):,.0f}")
print(f"Óptimo entero: {opt_ent} · Z = {z(opt_ent):,.0f}")
print(f"Imagen guardada en {salida}")
