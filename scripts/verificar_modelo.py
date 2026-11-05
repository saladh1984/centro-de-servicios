"""Verifica con scipy.optimize.linprog (método HiGHS) lo que muestran los gráficos.

Comprueba: óptimo continuo ≈ (12,857; 14,286) con Z = 6.600.000; precios sombra
Validación = 100.000, Cierre = 50.000, Análisis = 0; óptimo entero (13; 14) con
Z = 6.580.000.

Uso:  python scripts/verificar_modelo.py
"""
import numpy as np
from scipy.optimize import linprog

c = np.array([280_000, 210_000])          # margen por solicitud (COP)
A = np.array([[1.6, 1.0],                 # Análisis
              [2.4, 1.2],                 # Validación
              [0.8, 1.8]])                # Cierre
b = np.array([40, 48, 36])                # horas-equipo por día
etapas = ["Análisis", "Validación", "Cierre"]

# linprog minimiza: se maximiza Z minimizando -Z
lp = linprog(-c, A_ub=A, b_ub=b, bounds=[(0, None)] * 2, method="highs")
x, z = lp.x, -lp.fun
precios = -lp.ineqlin.marginals           # cambio de signo por la minimización

# Óptimo entero: mismo modelo con variables enteras
ent = linprog(-c, A_ub=A, b_ub=b, bounds=[(0, None)] * 2, method="highs", integrality=[1, 1])
xe, ze = np.round(ent.x).astype(int), -ent.fun

print(f"Óptimo continuo: x1 = {x[0]:.3f}, x2 = {x[1]:.3f}, Z = {z:,.0f}")
for e, p, u in zip(etapas, precios, A @ x):
    print(f"  {e:<11} usa {u:6.2f} de {b[etapas.index(e)]} h · precio sombra {p:,.0f}")
print(f"Óptimo entero:   x1 = {xe[0]}, x2 = {xe[1]}, Z = {ze:,.0f}")

esperado = dict(x=(90 / 7, 100 / 7), z=6_600_000, precios=(0, 100_000, 50_000), xe=(13, 14), ze=6_580_000)
assert np.allclose(x, esperado["x"], atol=1e-6), "El óptimo continuo no coincide"
assert abs(z - esperado["z"]) < 1e-3, "Z continuo no coincide"
assert np.allclose(precios, esperado["precios"], atol=1e-3), "Los precios sombra no coinciden"
assert tuple(xe) == esperado["xe"] and abs(ze - esperado["ze"]) < 1e-3, "El óptimo entero no coincide"
print("✓ Todo coincide con lo dibujado en los gráficos.")
