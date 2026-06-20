# CobraIQ – Motor de Decisión de Cobranza Inteligente

Proyecto desarrollado para el **IAthon Ulima x Mibanco**.

CobraIQ es un motor de decisión que optimiza la gestión de cobranza seleccionando el canal, horario y acción más adecuados para cada cliente, reduciendo costos operativos y evitando la sobregestión.

## Archivos

| Archivo | Descripción |
|---|---|
| `generar_dataset_cobraiq.py` | Script que genera el dataset simulado de 500 clientes |
| `cobraiq_dataset.csv` | Dataset generado en formato CSV |
| `cobraiq_dataset.xlsx` | Dataset en Excel con 4 hojas (completo, resúmenes y diccionario) |

## Dataset

El dataset incluye **500 clientes ficticios** con 36 variables que cubren:

- **Identificación**: zona geográfica, segmento de negocio, antigüedad
- **Perfil digital**: canal favorito, horario de respuesta, tasa de apertura de mensajes
- **Perfil crediticio**: tramo de mora, score de riesgo, montos
- **Historial de contactos**: contactos efectivos, último canal usado
- **Comportamiento de pago**: pagos puntuales, propensión de pago espontáneo
- **Decisión CobraIQ**: canal recomendado, horario, acción y razón

## Lógica de decisión

El motor aplica 6 reglas en cascada:

1. **Freno de sobregestión** – no contactar si ya pagó o fue contactado recientemente con respuesta
2. **Alta propensión espontánea** (≥75) – solo recordatorio suave o monitoreo
3. **Tramo preventivo** – recordatorio por SMS o llamada según perfil digital
4. **0 días mora** – recordatorio con link de pago vía WhatsApp o llamada
5. **Mora temprana 1-30 días** – bot + oferta de refinanciamiento o escalado a llamada
6. **Mora media/avanzada** – llamada urgente o visita presencial

## Distribución de mora (según datos Mibanco)

| Tramo | Proporción |
|---|---|
| Preventiva | 28% |
| 0 días | 24% |
| 1-30 días | 20% |
| 31-60 días | 15% |
| +60 días | 13% |

## Requisitos

```bash
pip install pandas numpy openpyxl
```

## Uso

```bash
python generar_dataset_cobraiq.py
```

Los archivos se guardan en el directorio configurado en `output_dir` (línea 362 del script).
