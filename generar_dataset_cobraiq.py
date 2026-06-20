"""
CobraIQ – Generador de Dataset Simulado
Mibanco x IAthon Ulima
==============================================
Genera 500 clientes ficticios con todas las variables
necesarias para el motor de decisión de cobranza inteligente.
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

N = 500

# ─────────────────────────────────────────────
# 1. IDENTIFICACIÓN DEL CLIENTE
# ─────────────────────────────────────────────
prefijos = ["DNI", "RUC"]
cliente_ids = [f"MB-{str(i).zfill(5)}" for i in range(1, N + 1)]

nombres = [
    "Carlos","Ana","Luis","María","José","Rosa","Miguel","Carmen",
    "Pedro","Elena","Jorge","Patricia","Roberto","Diana","Alberto",
    "Sandra","Eduardo","Lucía","Fernando","Claudia","Ricardo","Mónica",
    "Andrés","Valeria","Óscar","Gabriela","Héctor","Isabel","Raúl","Sofía"
]
apellidos = [
    "García","López","Martínez","Rodríguez","Pérez","Sánchez","Torres",
    "Flores","Rivera","Castro","Vargas","Mendoza","Quispe","Mamani",
    "Huanca","Condori","Ramos","Cruz","Medina","Rojas","Morales","Reyes",
    "Jiménez","Herrera","Alvarado","Paredes","Chávez","Espinoza","Vera","Díaz"
]

nombre_cliente = [f"{random.choice(nombres)} {random.choice(apellidos)} {random.choice(apellidos)}" for _ in range(N)]

zonas = ["Lima Norte", "Lima Sur", "Lima Este", "Lima Centro", "Callao",
         "Arequipa", "Trujillo", "Chiclayo", "Piura", "Cusco"]
zona_geografica = np.random.choice(zonas, N, p=[0.20, 0.15, 0.15, 0.10, 0.08, 0.08, 0.07, 0.07, 0.05, 0.05])

segmentos = ["Microempresa", "Pequeña empresa", "Emprendedor independiente", "Negocio familiar"]
segmento_negocio = np.random.choice(segmentos, N, p=[0.45, 0.20, 0.25, 0.10])

antiguedad_meses = np.random.choice(range(1, 73), N)  # 1 a 72 meses como cliente

# ─────────────────────────────────────────────
# 2. PERFIL DIGITAL
# ─────────────────────────────────────────────
# 80% digital, 20% no digital (según datos de Mibanco)
es_digital = np.random.choice([1, 0], N, p=[0.80, 0.20])

# App activa solo si es digital
tiene_app_activa = np.where(es_digital == 1, np.random.choice([1, 0], N, p=[0.65, 0.35]), 0)

# Canal favorito histórico
def asignar_canal_favorito(digital):
    if digital == 1:
        return np.random.choice(["WhatsApp", "SMS", "Llamada"], p=[0.55, 0.25, 0.20])
    else:
        return np.random.choice(["Llamada", "SMS", "Campo"], p=[0.60, 0.25, 0.15])

canal_favorito_historico = [asignar_canal_favorito(d) for d in es_digital]

# Horario de mejor respuesta
franjas = ["07:00-09:00", "09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-20:00"]
horario_mejor_respuesta = np.random.choice(franjas, N, p=[0.15, 0.30, 0.20, 0.25, 0.10])

# Tasa de apertura de mensajes digitales (0-100%)
tasa_apertura_mensajes = np.where(
    es_digital == 1,
    np.clip(np.random.normal(65, 20, N), 10, 100),
    np.clip(np.random.normal(30, 15, N), 5, 70)
).round(1)

# ─────────────────────────────────────────────
# 3. PERFIL CREDITICIO Y MORA
# ─────────────────────────────────────────────
# Distribución por días mora (según slide de Mibanco)
# Preventiva 28%, 0 días 24%, 01-30 20%, 31-60 15%, +60 13%
tramos = ["Preventiva", "0 dias", "01-30 dias", "31-60 dias", "+60 dias"]
tramo_mora = np.random.choice(tramos, N, p=[0.28, 0.24, 0.20, 0.15, 0.13])

# Días de mora según tramo
def dias_mora_por_tramo(tramo):
    if tramo == "Preventiva":
        return 0
    elif tramo == "0 dias":
        return 0
    elif tramo == "01-30 dias":
        return random.randint(1, 30)
    elif tramo == "31-60 dias":
        return random.randint(31, 60)
    else:
        return random.randint(61, 120)

dias_mora = np.array([dias_mora_por_tramo(t) for t in tramo_mora])

# Monto del crédito (cartera <35K es 80% del portafolio)
monto_credito = np.where(
    np.random.random(N) < 0.80,
    np.random.randint(1000, 35000, N),
    np.random.randint(35001, 100000, N)
)

monto_deuda_actual = (monto_credito * np.random.uniform(0.05, 0.40, N)).astype(int)
cuota_mensual = (monto_credito / np.random.randint(6, 36, N)).astype(int)

# Score de riesgo (1-1000, mayor = menos riesgo)
tramo_mora_arr = np.array(tramo_mora)
score_riesgo_base = np.where(
    tramo_mora_arr == "Preventiva", np.random.randint(600, 950, N),
    np.where(tramo_mora_arr == "0 dias", np.random.randint(500, 800, N),
    np.where(tramo_mora_arr == "01-30 dias", np.random.randint(350, 650, N),
    np.where(tramo_mora_arr == "31-60 dias", np.random.randint(200, 450, N),
    np.random.randint(100, 300, N)
)))).astype(int)

# Número de veces en mora en últimos 12 meses
veces_en_mora_12m = np.where(
    tramo_mora_arr == "Preventiva", np.random.randint(0, 2, N),
    np.where(tramo_mora_arr == "0 dias", np.random.randint(0, 3, N),
    np.random.randint(1, 6, N))
).astype(int)

# ─────────────────────────────────────────────
# 4. HISTORIAL DE CONTACTOS PREVIOS
# ─────────────────────────────────────────────
contactos_ultimos_30d = np.random.randint(0, 8, N)
contactos_efectivos_30d = np.clip(
    (contactos_ultimos_30d * np.random.uniform(0.2, 0.8, N)).astype(int),
    0, contactos_ultimos_30d
)

# Último canal usado
ultimo_canal_usado = [random.choice(["WhatsApp", "SMS", "Llamada", "Campo", "Ninguno"])
                      for _ in range(N)]

# Días desde último contacto
dias_desde_ultimo_contacto = np.random.randint(0, 30, N)
dias_desde_ultimo_contacto = np.where(
    np.array(ultimo_canal_usado) == "Ninguno", 999, dias_desde_ultimo_contacto
)

# ¿Respondió al último contacto?
respondio_ultimo_contacto = np.where(
    np.array(ultimo_canal_usado) == "Ninguno", 0,
    np.random.choice([1, 0], N, p=[0.55, 0.45])
)

# ─────────────────────────────────────────────
# 5. COMPORTAMIENTO DE PAGO
# ─────────────────────────────────────────────
pagos_puntuales_12m = np.random.randint(0, 12, N)
pagos_con_recordatorio_12m = np.clip(
    12 - pagos_puntuales_12m - np.random.randint(0, 4, N), 0, 12
)
pagos_tardios_12m = np.clip(12 - pagos_puntuales_12m - pagos_con_recordatorio_12m, 0, 12)

# ¿Pagó solo (sin contacto) en los últimos 3 meses?
pago_espontaneo_3m = np.where(
    pagos_puntuales_12m >= 9,
    np.random.choice([1, 0], N, p=[0.75, 0.25]),
    np.random.choice([1, 0], N, p=[0.20, 0.80])
)

# Propensión de pago espontáneo (variable clave del modelo)
# Calculada como función de variables históricas
propension_pago_espontaneo = np.clip(
    (pagos_puntuales_12m / 12 * 40) +
    (score_riesgo_base / 1000 * 35) +
    (es_digital * 10) +
    (pago_espontaneo_3m * 15) -
    (veces_en_mora_12m * 5) -
    (dias_mora / 120 * 20) +
    np.random.normal(0, 5, N),
    0, 100
).round(1)

# ─────────────────────────────────────────────
# 6. VARIABLES DE SOBREGESTIÓN
# ─────────────────────────────────────────────
fue_contactado_esta_semana = np.where(
    dias_desde_ultimo_contacto <= 7, 1, 0
)
fue_contactado_esta_semana = np.where(
    np.array(ultimo_canal_usado) == "Ninguno", 0, fue_contactado_esta_semana
)

ya_pago_este_mes = np.where(
    np.array(tramo_mora) == "Preventiva",
    np.random.choice([1, 0], N, p=[0.70, 0.30]),
    np.random.choice([1, 0], N, p=[0.15, 0.85])
)

# ─────────────────────────────────────────────
# 7. OUTPUT DEL MOTOR CobraIQ (etiquetas supervisadas)
# ─────────────────────────────────────────────

def decidir_canal_cobraiq(row):
    """
    Lógica de decisión del motor CobraIQ.
    Retorna: canal, horario, accion, razon
    """
    # REGLA 0: Freno de sobregestión
    if row["ya_pago_este_mes"] == 1:
        return "Sin contacto", "N/A", "No contactar", "Ya realizó su pago este mes"

    if row["fue_contactado_esta_semana"] == 1 and row["respondio_ultimo_contacto"] == 1:
        return "Sin contacto", "N/A", "No contactar", "Contacto reciente efectivo, esperar respuesta"

    # REGLA 1: Alta propensión de pago espontáneo
    if row["propension_pago_espontaneo"] >= 75:
        if row["es_digital"] == 1:
            return "SMS", row["horario_mejor_respuesta"], "Recordatorio suave", "Alta propensión: solo recordatorio leve"
        else:
            return "Sin contacto", "N/A", "Monitorear", "Alta propensión de pago sin contacto"

    # REGLA 2: Tramo preventivo
    if row["tramo_mora"] == "Preventiva":
        if row["es_digital"] == 1:
            return "SMS", "09:00-12:00", "Recordatorio preventivo", "Tramo preventivo cliente digital"
        else:
            return "Llamada", "09:00-12:00", "Recordatorio preventivo", "Tramo preventivo cliente no digital"

    # REGLA 3: 0 días mora
    if row["tramo_mora"] == "0 dias":
        if row["es_digital"] == 1 and row["canal_favorito_historico"] == "WhatsApp":
            return "WhatsApp", row["horario_mejor_respuesta"], "Recordatorio con link de pago", "Mora 0d, cliente digital WhatsApp"
        elif row["es_digital"] == 1:
            return "WhatsApp", row["horario_mejor_respuesta"], "Bot de cobranza empática", "Mora 0d, cliente digital"
        else:
            return "Llamada", row["horario_mejor_respuesta"], "Llamada recordatoria", "Mora 0d, cliente no digital"

    # REGLA 4: Mora temprana 1-30 días
    if row["tramo_mora"] == "01-30 dias":
        if row["es_digital"] == 1:
            if row["respondio_ultimo_contacto"] == 0 and row["contactos_ultimos_30d"] >= 3:
                return "Llamada", row["horario_mejor_respuesta"], "Llamada de seguimiento", "Digital no responde, escalar a llamada"
            return "WhatsApp", row["horario_mejor_respuesta"], "Bot + oferta de refinanciamiento", "Mora temprana cliente digital"
        else:
            return "Llamada", row["horario_mejor_respuesta"], "Llamada de negociación", "Mora temprana cliente no digital"

    # REGLA 5: Mora media 31-60 días
    if row["tramo_mora"] == "31-60 dias":
        if row["es_digital"] == 1:
            return "Llamada", row["horario_mejor_respuesta"], "Llamada + WhatsApp combinado", "Mora media, intensificar contacto"
        else:
            return "Llamada", row["horario_mejor_respuesta"], "Llamada urgente", "Mora media cliente no digital"

    # REGLA 6: Mora avanzada +60 días
    if row["tramo_mora"] == "+60 dias":
        return "Campo", "09:00-12:00", "Visita presencial de cobranza", "Mora avanzada, requiere presencia física"

    return "SMS", row["horario_mejor_respuesta"], "Recordatorio general", "Caso no clasificado"


def resultado_pago_simulado(row):
    """
    Simula si el cliente pagó dado el canal y sus variables.
    Para entrenar el modelo supervisado.
    """
    base = row["propension_pago_espontaneo"] / 100

    bonus_canal = {
        "WhatsApp": 0.15,
        "SMS": 0.05,
        "Llamada": 0.10,
        "Campo": 0.08,
        "Sin contacto": 0.0
    }.get(row["canal_recomendado"], 0)

    penalizacion_mora = min(row["dias_mora"] / 120 * 0.30, 0.30)
    prob_pago = min(base + bonus_canal - penalizacion_mora + random.uniform(-0.05, 0.05), 1.0)
    return 1 if random.random() < prob_pago else 0


# ─────────────────────────────────────────────
# 8. CONSTRUCCIÓN DEL DATAFRAME
# ─────────────────────────────────────────────

df = pd.DataFrame({
    # Identificación
    "cliente_id": cliente_ids,
    "nombre_cliente": nombre_cliente,
    "zona_geografica": zona_geografica,
    "segmento_negocio": segmento_negocio,
    "antiguedad_meses": antiguedad_meses,

    # Perfil digital
    "es_digital": es_digital,
    "tiene_app_activa": tiene_app_activa,
    "canal_favorito_historico": canal_favorito_historico,
    "horario_mejor_respuesta": horario_mejor_respuesta,
    "tasa_apertura_mensajes_pct": tasa_apertura_mensajes,

    # Perfil crediticio
    "tramo_mora": tramo_mora,
    "dias_mora": dias_mora,
    "monto_credito_sol": monto_credito,
    "monto_deuda_actual_sol": monto_deuda_actual,
    "cuota_mensual_sol": cuota_mensual,
    "score_riesgo": score_riesgo_base,
    "veces_en_mora_12m": veces_en_mora_12m,

    # Historial contactos
    "contactos_ultimos_30d": contactos_ultimos_30d,
    "contactos_efectivos_30d": contactos_efectivos_30d,
    "ultimo_canal_usado": ultimo_canal_usado,
    "dias_desde_ultimo_contacto": dias_desde_ultimo_contacto,
    "respondio_ultimo_contacto": respondio_ultimo_contacto,

    # Comportamiento de pago
    "pagos_puntuales_12m": pagos_puntuales_12m,
    "pagos_con_recordatorio_12m": pagos_con_recordatorio_12m,
    "pagos_tardios_12m": pagos_tardios_12m,
    "pago_espontaneo_3m": pago_espontaneo_3m,
    "propension_pago_espontaneo": propension_pago_espontaneo,

    # Sobregestión
    "fue_contactado_esta_semana": fue_contactado_esta_semana,
    "ya_pago_este_mes": ya_pago_este_mes,
})

# Aplicar motor CobraIQ
decisiones = df.apply(decidir_canal_cobraiq, axis=1)
df["canal_recomendado"]   = [d[0] for d in decisiones]
df["horario_recomendado"] = [d[1] for d in decisiones]
df["accion_recomendada"]  = [d[2] for d in decisiones]
df["razon_decision"]      = [d[3] for d in decisiones]

# Simular resultado de pago
df["resultado_pago_simulado"] = df.apply(resultado_pago_simulado, axis=1)

# Costo estimado por contacto (en soles)
costo_canal = {
    "WhatsApp": 0.10,
    "SMS": 0.05,
    "Llamada": 2.50,
    "Campo": 45.00,
    "Sin contacto": 0.00
}
df["costo_contacto_sol"] = df["canal_recomendado"].map(costo_canal)

# Prioridad de gestión (1=urgente, 2=normal, 3=baja)
def calcular_prioridad(row):
    if row["tramo_mora"] in ["+60 dias", "31-60 dias"]:
        return 1
    elif row["tramo_mora"] == "01-30 dias":
        return 2
    else:
        return 3

df["prioridad_gestion"] = df.apply(calcular_prioridad, axis=1)

# ─────────────────────────────────────────────
# 9. GUARDAR ARCHIVOS
# ─────────────────────────────────────────────
output_dir = "/mnt/user-data/outputs"
os.makedirs(output_dir, exist_ok=True)

# CSV principal
csv_path = f"{output_dir}/cobraiq_dataset.csv"
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

# Excel con múltiples hojas
excel_path = f"{output_dir}/cobraiq_dataset.xlsx"
with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Dataset completo", index=False)

    # Hoja resumen por tramo
    resumen_tramo = df.groupby("tramo_mora").agg(
        clientes=("cliente_id", "count"),
        pct_digital=("es_digital", "mean"),
        propension_promedio=("propension_pago_espontaneo", "mean"),
        tasa_pago_simulada=("resultado_pago_simulado", "mean"),
        costo_promedio=("costo_contacto_sol", "mean")
    ).round(2).reset_index()
    resumen_tramo.to_excel(writer, sheet_name="Resumen por tramo", index=False)

    # Hoja resumen por canal recomendado
    resumen_canal = df.groupby("canal_recomendado").agg(
        clientes=("cliente_id", "count"),
        tasa_pago=("resultado_pago_simulado", "mean"),
        costo_total=("costo_contacto_sol", "sum"),
        propension_promedio=("propension_pago_espontaneo", "mean")
    ).round(2).reset_index()
    resumen_canal.to_excel(writer, sheet_name="Resumen por canal", index=False)

    # Hoja diccionario de variables
    diccionario = pd.DataFrame({
        "Variable": df.columns,
        "Tipo": df.dtypes.astype(str).values,
        "Descripcion": [
            "ID único del cliente en Mibanco",
            "Nombre completo del cliente",
            "Zona geográfica del cliente",
            "Tipo de negocio del cliente",
            "Meses como cliente de Mibanco",
            "1=cliente digital (app/WhatsApp), 0=no digital",
            "1=tiene app Mibanco activa",
            "Canal de contacto con mayor historial de respuesta",
            "Franja horaria en que suele responder contactos",
            "% de mensajes digitales que abre/lee",
            "Tramo de mora actual del cliente",
            "Días exactos en mora",
            "Monto total del crédito en soles",
            "Monto de deuda pendiente actual en soles",
            "Cuota mensual del crédito en soles",
            "Score de riesgo crediticio (1-1000, mayor=menos riesgo)",
            "Veces que cayó en mora en los últimos 12 meses",
            "Total de contactos de cobranza en últimos 30 días",
            "Contactos que resultaron en comunicación efectiva",
            "Último canal de cobranza utilizado",
            "Días desde el último intento de contacto",
            "1=respondió al último contacto realizado",
            "Pagos realizados a tiempo sin recordatorio (últimos 12m)",
            "Pagos realizados solo tras recibir recordatorio (12m)",
            "Pagos realizados con retraso (12m)",
            "1=pagó al menos una vez sin contacto en últimos 3 meses",
            "Score 0-100 de probabilidad de pago sin contacto (variable target principal)",
            "1=fue contactado en los últimos 7 días",
            "1=ya realizó el pago del mes actual",
            "Canal de contacto recomendado por CobraIQ",
            "Horario óptimo de contacto recomendado",
            "Tipo de acción a ejecutar",
            "Explicación de por qué se tomó esa decisión",
            "1=realizó el pago en la simulación (variable target supervisada)",
            "Costo estimado del contacto en soles",
            "Nivel de prioridad (1=urgente, 2=normal, 3=baja)"
        ]
    })
    diccionario.to_excel(writer, sheet_name="Diccionario de variables", index=False)

# ─────────────────────────────────────────────
# 10. ESTADÍSTICAS DE VALIDACIÓN
# ─────────────────────────────────────────────
print("=" * 55)
print("  CobraIQ – Dataset generado exitosamente")
print("=" * 55)
print(f"\n  Total clientes: {len(df)}")
print(f"  Variables:      {len(df.columns)}")

print("\n── Distribución por tramo de mora ──")
tramo_counts = df["tramo_mora"].value_counts()
for tramo, count in tramo_counts.items():
    pct = count / N * 100
    print(f"  {tramo:<20} {count:>4} clientes  ({pct:.1f}%)")

print("\n── Perfil digital ──")
print(f"  Clientes digitales:     {df['es_digital'].sum()} ({df['es_digital'].mean()*100:.1f}%)")
print(f"  Con app activa:         {df['tiene_app_activa'].sum()}")

print("\n── Canales recomendados por CobraIQ ──")
canal_counts = df["canal_recomendado"].value_counts()
for canal, count in canal_counts.items():
    pct = count / N * 100
    costo = df[df["canal_recomendado"]==canal]["costo_contacto_sol"].sum()
    print(f"  {canal:<18} {count:>4} ({pct:.1f}%)  Costo total: S/ {costo:.2f}")

print(f"\n── Impacto estimado CobraIQ ──")
# Costo tradicional: todos contactados por llamada (excluyendo ya pagados)
clientes_a_gestionar = N - df["ya_pago_este_mes"].sum()
costo_tradicional = clientes_a_gestionar * 2.50
# Costo CobraIQ: excluir campo (mismo en ambos escenarios) para comparación justa
costo_cobraiq_sin_campo = df[df["canal_recomendado"] != "Campo"]["costo_contacto_sol"].sum()
costo_campo = df[df["canal_recomendado"] == "Campo"]["costo_contacto_sol"].sum()
costo_total_cobraiq = costo_cobraiq_sin_campo + costo_campo
# Comparación: tradicional también tendría campo para mora avanzada
costo_campo_trad = df[df["tramo_mora"] == "+60 dias"].shape[0] * 45.0
costo_tradicional_total = (clientes_a_gestionar - df[df["tramo_mora"] == "+60 dias"].shape[0]) * 2.50 + costo_campo_trad
ahorro = costo_tradicional_total - costo_total_cobraiq
print(f"  Costo tradicional estimado:          S/ {costo_tradicional_total:,.2f}")
print(f"  Costo CobraIQ (mix optimizado):      S/ {costo_total_cobraiq:,.2f}")
print(f"  Ahorro estimado:                     S/ {ahorro:,.2f}  ({ahorro/costo_tradicional_total*100:.1f}%)")
print(f"  Tasa de pago simulada:               {df['resultado_pago_simulado'].mean()*100:.1f}%")
print(f"  Clientes sin contacto innecesario:   {(df['canal_recomendado']=='Sin contacto').sum()}")

print(f"\n  Archivos guardados:")
print(f"  CSV   → cobraiq_dataset.csv")
print(f"  Excel → cobraiq_dataset.xlsx  (4 hojas)")
print("=" * 55)
