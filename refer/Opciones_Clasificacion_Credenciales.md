# Clasificación de credenciales (t1/t2/t3) — Opciones y guía técnica

**Contexto**  
- Imágenes **alineadas** a **790×490 (ancho×alto)** en **escala de grises**.  
- Disponemos de **máscaras** por tipo/lado: el área válida (no descartable) es donde se debe computar.  
- Tenemos **rasgos visuales** por tipo y lado (fragmentos característicos) y **muestras de referencia**.

---

## Supuestos de entrada
- `img` ∈ ℝ^(490×790) normalizada a [0,1].  
- Máscaras binarias 0/1 por clase/lado: `M_{t1_front}, M_{t1_back}, …, M_{t3_back}` reamostradas a 790×490 (**nearest**).  
- Se aplican siempre: `img_masked = img * M`.  
- Opcional: **erode(1 px)** a la máscara para limpiar bordes y conservar 100% dentro de la zona válida.

---

## Rasgos distintivos (resumen)
**t1 front:** escudo+grecas sup. izq, encabezado “INSTITUTO NACIONAL ELECTORAL”, leyenda “FECHA DE NACIMIENTO | SECCIÓN”, mapa de México inf. der.  
**t1 back:** dos **QR** grandes contiguos + **QR** pequeño a la derecha + roseta/insignia.  
**t2 front:** escudo+grecas, encabezado “INSTITUTO NACIONAL ELECTORAL”, mapa MX, etiquetas **ESTADO/MUNICIPIO/SECCIÓN**.  
**t2 back:** panel de **firma** (rectángulo claro) + **línea base** inferior + **un** QR grande derecho + roseta.  
**t3 front:** escudo circular “ESTADOS UNIDOS MEXICANOS” + **logo del águila** + encabezado “INSTITUTO FEDERAL ELECTORAL” + etiquetas **EDAD/SEXO** apiladas.  
**t3 back:** columna **numerada** vertical izquierda + línea horizontal inferior + panel firma + línea base + celdas/segmentos inferiores.

> Estos rasgos se comprobarán **solo** dentro de las zonas válidas de su máscara correspondiente.

---

## Opción 1 — Reglas + plantillas de rasgos (Template Matching) ✅ 100% explicable
**Idea:** Buscar cada rasgo en su ROI con **NCC** (o **SSIM** para texto/paneles) y sumar puntuaciones por clase.

**Pasos**
1. Definir **ROIs relativos** (x,y,w,h) por rasgo y por lado en el lienzo 790×490.  
2. Crear **plantillas** (patches) a partir de tus recortes representativos.  
3. Calcular `score_i = NCC( img ⊙ M_roi , plantilla_i )`.  
4. **Score de clase** = suma ponderada de sus rasgos.  
5. Predicción = clase con `score_max`; si `score_max < τ_rule` ⇒ **unknown**.

**Pros:** muy rápido, trazable y auditable.  
**Contras:** más sensible a variaciones de impresión/textura.

---

## Opción 2 — Prototipos enmascarados (SSIM/NCC) + verificación de rasgos
**Idea:** Primero similitud global (enmascarada), después confirmar rasgos “firmados” de la clase ganadora.

**Pasos**
1. Construir prototipos por clase/lado: `P_{t,side} = mean( imgs_train ⊙ M_{t,side} )`.  
2. Clasificar por `SSIM( img ⊙ M_{t,side} , P_{t,side} ⊙ M_{t,side} )` o **NCC**.  
3. Verificar rasgos clave (p. ej., **dos QR** en t1 back). Si < umbral, **anular** predicción.

**Pros:** simple y preciso si las máscaras son buenas.  
**Contras:** algo sensible a ruido fuerte (compensado por la verificación).

---

## Opción 3 — SVM/HOG con máscara (clásico y liviano)
**Idea:** Extraer **HOG** en la zona válida y entrenar **SVM** para 6 clases (`t1_f … t3_b`).

**Pasos**
1. `x = HOG( img ⊙ M_side )` (celdas 16×16, bloques 2×2, 9 bins).  
2. Entrenar **SVM lineal** (o RBF si hiciera falta).  
3. Predicción por margen; si margen < `τ_svm` ⇒ **unknown**.  
4. (Opcional) Verificación fina de rasgos de la clase predicha.

**Pros:** CPU-friendly, modelo pequeño.  
**Contras:** menos flexible que CNN ante cambios de dominio.

---

## Opción 4 — CNN ligera (MobileNetV3/ResNet-18) sobre gris enmascarado
**Idea:** Red pequeña con entrada `img ⊙ M`, clases: 6 (`t1_f…t3_b`) o pipeline 2 etapas (lado → tipo).

**Pasos**
1. Preparar dataset con `img ⊙ M` (fuera de máscara = 0).  
2. Usar **MobileNetV3-Small** o **ResNet-18** (ajustando `in_channels=1` o duplicando el canal).  
3. *Augmentations* suaves: rot±5°, JPEG/blur, brillo/contraste, banding de escáner.  
4. Entrenar con LR 3e-4, batch 32, 15–30 epochs; *early stopping*.  
5. En inferencia: `p_max < τ_cnn` ⇒ **unknown**.

**Pros:** robusto y rápido; excelente rendimiento.  
**Contras:** requiere un entrenamiento corto.

---

## Opción 5 — Embeddings prototípicos (few-shot, extensible)
**Idea:** Embeddings (256–512D) de `img ⊙ M` y clasificación por **distancia coseno** a centros por clase.

**Pasos**
1. Extraer `z = f(img ⊙ M)` (ResNet-18 congelada o afinada).  
2. Centros: `c_k = mean(z_k)` por clase/lado.  
3. Predicción: `k* = argmin_k dist_cos(z, c_k)`; si `dist_min > τ_proto` ⇒ **unknown**.  
4. (Opcional) Afinar con **Prototypical** o **Triplet loss**.

**Pros:** añade subtipos sin reentrenar completo.  
**Contras:** algo menos explicable que Opción 1.

---

## Ensamble recomendado (simple y fuerte)
1. **Filtro por rasgos firmados** (reglas duras):
   - **t1 back:** dos QR grandes contiguos + QR pequeño.  
   - **t2 back:** panel firma + **un** QR derecho.  
   - **t3 back:** columna numerada izq. + panel firma.  
   - **t3 front:** encabezado IFE + etiquetas **EDAD/SEXO**.  
   - **front t1/t2:** encabezado INE + (t1: “FECHA NAC/SECCIÓN” vs. t2: “ESTADO/MUNICIPIO/SECCIÓN”).  
2. **Clasificador principal:** Opción **2** (SSIM prototipo) **o** **4** (CNN).  
3. **Verificación de rasgos** de la clase ganadora.  
4. **Confianza combinada:**  
   `conf = α·score_principal + (1−α)·(#rasgos_ok / #rasgos_total)` con `α ≈ 0.6–0.7`.  
   Si `conf < τ_final` ⇒ **unknown**.

---

## Estructura de carpetas sugerida
```
data/
  t1/front/*.png   t1/back/*.png
  t2/front/*.png   t2/back/*.png
  t3/front/*.png   t3/back/*.png
masks/
  t1_front.png  t1_back.png  t2_front.png  t2_back.png  t3_front.png  t3_back.png
rasgos/
  t1_front/*.png  t1_back/*.png  t2_front/*.png  t2_back/*.png  t3_front/*.png  t3_back/*.png
```

---

## Salida esperada (JSON)
```json
{
  "side": "front|back",
  "tipo": "t1|t2|t3|unknown",
  "method": "rules|ssim|rules+ssim|svm|cnn|proto",
  "score": 0.0,
  "rasgos": {"t1_back.QRdoble":0.93,"t1_back.QRchico":0.88,"t1_back.roseta":0.67},
  "top2": [["t1",0.86],["t2",0.58]]
}
```

---

## Umbrales iniciales y evaluación
- **NCC rasgos (reglas):** ≥ **0.65** (rasgos “duros” como QR/columna numerada).  
- **SSIM prototipo (Opción 2):** ≥ **0.60 ± 0.05** (calibrar en validación).  
- **SVM margen (Opción 3):** calibrar `τ_svm` por ROC.  
- **CNN `p_max` (Opción 4):** ≥ **0.80** (con *temperature scaling*).  
- **Embeddings (Opción 5):** distancia coseno ≤ **0.20 ± 0.05**.

Métricas: **accuracy**, **balanced accuracy**, **F1 macro**, **confusion matrix** por lado. Registrar también **% rasgos_ok** para explicabilidad.

---

## Roadmap práctico
1) Implementar **Opción 1** (reglas+rasgos) y **Opción 2** (prototipos+SSIM).  
2) Validar y calibrar umbrales.  
3) Si hace falta robustez adicional, activar **Opción 4** (CNN) como clasificador principal y dejar reglas como filtro/verificación.  
4) (Opcional) Añadir **Embeddings** para facilitar incorporación de nuevos subtipos.

---

## Checklist
- [ ] Máscaras binarizadas y reamostradas a 790×490.  
- [ ] ROIs de cada rasgo definidos (coordenadas relativas).  
- [ ] Prototipos por clase/lado generados.  
- [ ] Umbrales calibrados en validación.  
- [ ] Reporte JSON y trazas (mapas de similitud por rasgo).

---

**Notas finales**  
- Todos los cálculos deben limitarse **exclusivamente** a las zonas válidas de la máscara.  
- Mantener una clase **“unknown”** si el score/rasgos no alcanzan los umbrales.  
- Conservar imágenes/rasgos que fallen por poco para **realimentar** la calibración y/o el entrenamiento.
