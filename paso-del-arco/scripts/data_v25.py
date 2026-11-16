# -*- coding: utf-8 -*-
"""v2.5: codificación ampliada para rutas regionales y binacionales (Icalma, Melipeuco) y productos asociados (HIP)."""
from data_v24 import *

TERRITORIOS = HR["territorios"]

REGLAS_RUTAS = [
 ("Punto en el campo", "ZONA-TIPO-NN (zona de 1 letra)", "O-BAS-01 Base 1 Inicio"),
 ("Punto fuera del campo", "TERRITORIO-TIPO-NN (territorio de 3 letras: A=Argentina / C=Chile + lugar)", "CIC-GAS-01 almuerzo en Icalma (Chile)"),
 ("Lectura rápida", "Empieza con A o C → fuera del campo; la primera letra dice el país", "APE-FRO-01 (control argentino) · CIC-FRO-01 (control chileno)"),
 ("Tramo", "PUNTO>PUNTO", "R-ACC-01>APE-FRO-01"),
 ("Ruta o circuito de un día", "RUT-ÁMBITO-NN · ámbito: PDA (solo campo), AR (Argentina), CL (Chile), BI (cruza la frontera)", "RUT-BI-01"),
 ("Travesía de varios días", "TRV-ÁMBITO-NN", "TRV-BI-01"),
 ("Día de una travesía", "TRV-…-NN.Dn = una RUT", "TRV-BI-01.D3 = RUT-BI-02"),
 ("Pernocte", "Punto ALO o BAS donde termina el día", "CME-ALO-01 · O-BAS-01"),
 ("Variante / versión", "Letra al final / v1, v2", "RUT-BI-01b · RUT-BI-01 v2"),
 ("Regla del ámbito", "Sale de los puntos: solo zonas de 1 letra → PDA; solo A.. → AR; solo C.. → CL; mezcla con C.. y campo o A.. → BI", ""),
 ("Bases futuras fuera del campo", "Llevan el territorio: no se confunden con las bases del campo", "CIC-BAS-01 · CME-BAS-01"),
]
EJEMPLOS_RUTAS = [
 ("RUT-BI-01", "Día binacional: frontera Icalma con almuerzo de cocina chilena y regreso",
  "O-BAS-01 > R-ACC-01 > APE-FRO-01 > CIC-FRO-01 > CIC-GAS-01 > CIC-FRO-01 > APE-FRO-01 > R-ACC-01 > O-BAS-01",
  "Los puntos APE-FRO-01, CIC-FRO-01 y CIC-GAS-01 se dan de alta en el relevamiento."),
 ("RUT-AR-01", "Borde Icalma sin cruzar: miradores del lado argentino y regreso",
  "O-BAS-01 > R-ACC-01 > APE-MIR-01 > APE-LIM-01 > R-ACC-01 > O-BAS-01", "Para clientes sin documentación de cruce."),
 ("TRV-BI-01", "Travesía 4 días: 2 en el campo + 2 en Chile con alojamiento en Chile",
  "D1 RUT-PDA-01 (noche O-BAS-01) · D2 RUT-PDA-02 (noche O-BAS-01) · D3 RUT-BI-02 campo → Paso Icalma → Melipeuco (noche CME-ALO-01) · D4 RUT-BI-03 Melipeuco → Icalma → campo",
  "El pernocte en el campo supone alojamiento que hoy no existe (Etapa 4) o un aliado cercano."),
 ("TRV-CL-01", "Travesía en Chile con base en Icalma o Melipeuco (futuro)",
  "D1 … Dn con salida y regreso a CME-BAS-01 o CIC-BAS-01", "Depende de un socio o base en Chile."),
]

PORTAFOLIO = PORTAFOLIO + [
 ("P13", "Día de frontera: Icalma y cocina chilena", "Excursión binacional de día",
  "Recorrido hasta el Paso Icalma, cruce y almuerzo típico chileno en Icalma; regreso en el día.",
  "Visitantes de Villa Pehuenia–Moquehue con documentación para cruzar; grupos privados.",
  "Ruta escénica, trámites de frontera guiados, almuerzo con un prestador chileno, regreso.",
  "Vehículo y conductor habilitados para transporte internacional, aliado gastronómico en Chile, seguros con cobertura en Chile.",
  "O-BAS-01 → CIC-GAS-01", "Combustible, guía, seguro internacional, almuerzo (pago en Chile), tiempos de frontera.",
  "Tiempo de frontera, cupo del aliado, tipo de cambio.", "Alojamientos de la zona, venta directa, operador chileno aliado.",
  "Demoras o cierre del paso, requisitos documentales del cliente, controles sanitarios (alimentos), tipo de cambio.",
  "Requisitos binacionales (D32); acuerdo con un prestador gastronómico chileno; prueba de tiempos.",
  "Etapa 3", "RUT-BI-01 (a relevar)"),
 ("P14", "Travesía binacional 4 días (2 campo + 2 Chile)", "Travesía de varios días",
  "Dos días de circuitos en el campo y dos días en Chile (Icalma–Melipeuco) con alojamiento en Chile.",
  "Viajeros de aventura nacionales e internacionales, clubes 4x4, grupos privados.",
  "Producto insignia de largo plazo: campo + volcanes y lagos de la Araucanía.",
  "Alojamiento en el campo (no existe) o aliado; alojamiento y operador en Chile; logística de dos países.",
  "O-BAS-01 → CME-ALO-01", "Por persona/día: alojamiento, comidas, vehículos, guías, seguros, permisos.",
  "Duración, tamaño del grupo, nivel de servicio.", "Operadores receptivos de ambos países, clubes, venta directa.",
  "Regulatorio binacional, coordinación con terceros, clima en el paso.",
  "Prefactibilidad específica; socio en Chile; demanda probada con P13.",
  "Etapa 3–4", "TRV-BI-01"),
]
RIESGOS = RIESGOS + [("R16", "Binacional", "Productos que cruzan a Chile: requisitos de transporte internacional de pasajeros, documentación de clientes y vehículos, seguros con cobertura en Chile, controles sanitarios de alimentos en frontera, horarios y cierres invernales del Paso Icalma, cobros en dos monedas.",
                      "Media", "Alto", "No vender sin requisitos confirmados por escrito; operar con un socio chileno habilitado; producto alternativo sin cruce (RUT-AR-01).", "Dirección", "Etapa 3")]
FALTANTES = FALTANTES + [
 ("D32", "Binacional", "Requisitos para operar excursiones y travesías Argentina–Chile por el Paso Icalma", "P13, P14", "Organismos de frontera y de transporte de ambos países; asesor especializado", "Alta (para Etapa 3)"),
 ("D33", "Binacional", "Aliados en Chile: gastronomía en Icalma, alojamiento en Melipeuco/Icalma, operador local", "P13, P14", "Relevamiento con puntos CIC/CME y entrevistas", "Media"),
]
