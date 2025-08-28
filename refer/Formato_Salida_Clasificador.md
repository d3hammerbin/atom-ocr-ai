# Formato de salida del clasificador (API FastAPI)

Este documento describe **el contrato de respuesta** del endpoint `/classify`. Todas las imágenes se clasifican por **lado** (front/back) y por **tipo** (t1/t2/t3). Cuando la evidencia no es suficiente, la clase será `unknown`.

---

## Esquema JSON (respuesta)

```json
{
  "side": "front|back",
  "tipo": "t1|t2|t3|unknown",
  "method": "rules+ssim|rules+cnn|svm|proto",
  "score": 0.0,
  "rasgos": {"t1_back.QRdoble":0.93,"t1_back.QRchico":0.88,"t1_back.roseta":0.67},
  "top2": [["t1",0.86],["t2",0.58]]
}
```

> **Notas generales**
> - Todos los puntajes están normalizados a **[0,1]** (mientras mayor, mejor).
> - La respuesta **siempre** incluye `side`, `tipo`, `method`, `score` y `top2`.  
> - El campo `rasgos` se incluye cuando el método usa **verificación por rasgos** (Opción 1 u Opción 2; también como *post-check* en CNN/SVM si está activado).

---

## Campos

### `side` (string)
- Valores: `"front"` | `"back"`
- Cómo se obtiene:
  - Si el cliente lo envía como parámetro, el clasificador usa ese lado.
  - Si no, se estima automáticamente: se evalúan reglas rápidas y/o se calculan scores para ambos lados y se elige el de mayor confianza.
- Uso: permite al cliente saber **qué máscara** y **reglas** se aplicaron.

### `tipo` (string)
- Valores: `"t1" | "t2" | "t3" | "unknown"`
- Lógica:
  - Es la **clase ganadora** del método especificado en `method` **después** de aplicar umbrales de confianza.
  - `unknown` se utiliza cuando:  
    - `score < threshold` global del método, o  
    - no se cumplen suficientes rasgos obligatorios del tipo ganador, o  
    - hay conflicto entre métodos (si se usa ensamble) y la confianza combinada es baja.

### `method` (string)
- Indica el **método principal** utilizado en la decisión final:
  - `"rules+ssim"` → Prototipos enmascarados **SSIM/NCC** + verificación por rasgos.
  - `"rules+cnn"`  → CNN ligera (ResNet/MobileNet) + verificación por rasgos.
  - `"svm"`        → SVM/HOG.
  - `"proto"`      → Embeddings prototípicos (distancia coseno a centros).
- En ensambles, se reporta el **método decisor**; si primero se filtra por reglas, esto ya está implícito en `rules+*`.

### `score` (number in [0,1])
- Confianza **principal** de la predicción.
- Interpretación por método:
  - `rules+ssim`: `score = SSIM_max` (o combinación ponderada SSIM/NCC normalizada).  
  - `rules+cnn`: `score = p_max` (probabilidad de la clase ganadora tras *softmax* y *temperature scaling*).  
  - `svm`: `score = σ(margen)` donde `σ` es una normalización del margen a [0,1].  
  - `proto`: `score = 1 - d_coseno_min` (distancia coseno invertida).
- **Umbral** típico para aceptar (ajustable en configuración):
  - `rules+ssim` ≥ 0.60; `rules` por rasgo ≥ 0.65  
  - `rules+cnn`  ≥ 0.80  
  - `svm`        ≥ 0.50 (depende de la normalización)  
  - `proto`      ≥ 0.80 (equivalente a `dist_cos ≤ 0.20`)

### `rasgos` (objeto string → number in [0,1])
- Solo aparece cuando hay **verificación de rasgos**.  
- Cada **clave** es `"<tipo>_<lado>.<nombre_del_rasgo>"`.  
- Cada **valor** es la **similitud** (NCC/SSIM) del rasgo en su ROI:
  - Ejemplos:
    - `t1_back.QRdoble`  → similitud del patrón de **dos QR grandes contiguos**.
    - `t1_back.QRchico`  → similitud del **QR pequeño** independiente a la derecha.
    - `t1_back.roseta`   → similitud de la **roseta/sello**.
    - `t3_front.ife_header` → similitud del encabezado **INSTITUTO FEDERAL ELECTORAL**.
- **Criterio de aprobación por rasgo**: si `rasgo_i ≥ umbral_i` (por defecto 0.65) cuenta como **detectado**.  
- **Criterio de clase**: se requiere un **mínimo** de rasgos detectados (p.ej., ≥ 2 de 3), o un **score ponderado** ≥ umbral.

### `top2` (array de 2 elementos)
- Lista con los **dos mejores candidatos** y su puntaje **principal** (mismo significado que `score`).
- Formato: `[[<tipo1>, <score1>], [<tipo2>, <score2>]]`
- Uso típico: interfaz de usuario, **auditoría** y fallback (p.ej., re-enviar a revisión manual si `score1 - score2` es pequeño).

---

## Ejemplos prácticos

### 1) T1 — reverso detectado con reglas+ssim (ejemplo dado)
```json
{
  "side": "back",
  "tipo": "t1",
  "method": "rules+ssim",
  "score": 0.83,
  "rasgos": {"t1_back.QRdoble":0.93,"t1_back.QRchico":0.88,"t1_back.roseta":0.67},
  "top2": [["t1",0.83],["t2",0.41]]
}
```
- Interpretación: la imagen parece **t1 back** con alta similitud global y **tres rasgos** superando umbrales.  
- Acción: **aceptar**. Si `score < 0.60` o faltaran rasgos clave, sería `unknown`.

### 2) T2 — frontal con CNN, baja confianza
```json
{
  "side": "front",
  "tipo": "unknown",
  "method": "rules+cnn",
  "score": 0.71,
  "rasgos": {"t2_front.ine_header":0.69,"t2_front.mapa_mx":0.51,"t2_front.etiquetas_em_s":0.64},
  "top2": [["t2",0.71],["t1",0.66]]
}
```
- Interpretación: CNN prefiere `t2`, pero `p_max=0.71` < 0.80 (umbral), y los rasgos no son concluyentes.  
- Acción: **marcar para revisión** o devolver `unknown` al cliente.

### 3) T3 — reverso por embeddings
```json
{
  "side": "back",
  "tipo": "t3",
  "method": "proto",
  "score": 0.86,
  "top2": [["t3",0.86],["t2",0.47]]
}
```
- Interpretación: `1 - dist_coseno_min = 0.86` (distancia coseno ≈ 0.14). Fuerte coincidencia con el centro `t3 back`.

---

## Recomendaciones de consumo (cliente)

- **Decisión binaria**: acepta si `tipo != "unknown"` **y** `score ≥ threshold_cliente`; de lo contrario, solicitar reintento o revisión.  
- **Umbrales por lado**: opcionalmente usar umbrales distintos para `front` y `back`.  
- **Auditoría**: conserva `top2` y `rasgos` para trazabilidad.  
- **Tiempo de vida**: si cambian máscaras o prototipos, invalidar cachés del lado cliente.

---

## Errores y códigos HTTP

- `200 OK` → Respuesta JSON válida con alguno de los métodos.  
- `422 Unprocessable Entity` → Imagen malformada o dimensiones inválidas.  
- `500 Internal Server Error` → Error interno (p.ej., falta de modelos/archivos).

En todos los casos, el cuerpo incluirá un mensaje `detail` adicional cuando aplique.

---

## Cambios futuros del contrato

- Se pueden agregar nuevas claves en `rasgos` y soportar nuevos `method` sin romper compatibilidad.  
- El orden de `top2` siempre es descendente por `score`.

---

**Fin del documento.**
