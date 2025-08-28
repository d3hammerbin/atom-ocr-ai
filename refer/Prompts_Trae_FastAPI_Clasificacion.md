
# Prompts para Trae (VS Code fork) — FastAPI · Clasificación t1/t2/t3 (front/back)

**Contexto fijo del proyecto**
- Imágenes ya llegan **790×490** (W×H), **escala de grises**.
- Máscaras binarias por **tipo** `{t1,t2,t3}` y **lado** `{front,back}` (1 = área válida).  
- Debe existir siempre la clase **`unknown`** cuando los puntajes no superan umbrales.
- Salida JSON estándar:
```json
{
  "side": "front|back",
  "tipo": "t1|t2|t3|unknown",
  "method": "rules|ssim|svm|cnn|proto|rules+ssim",
  "score": 0.0,
  "rasgos": {"<feature>": 0.0},
  "top2": [["t1",0.86],["t2",0.58]]
}
```
- Estructura de carpetas recomendada (ajústala si ya tienes otra):
```
project/
  app/
    main.py            # FastAPI
    deps.py            # carga de modelos, máscaras y config
    config.yaml        # rutas, ROIs, umbrales
    routers/
      classify.py
      admin.py
  models/              # .npz, .pkl, .pt, .onnx
  masks/               # t1_front.png, ..., t3_back.png
  rasgos/              # subcarpetas por tipo/lado con patches
  data/                # train/val por clase si aplica
  scripts/             # utilidades de entrenamiento/build
  tests/
  README.md
```

---

## Prompt maestro (común a cualquier opción)
> Pega este prompt primero para que Trae te genere el **esqueleto FastAPI** y utilidades comunes.

```
Quiero un servicio **FastAPI** en Python 3.10 con:
- Endpoints:
  - GET /health -> {"status":"ok"}
  - POST /classify -> recibe imagen (multipart/form-data o base64 en JSON) + parámetro `side` opcional. Devuelve el JSON estándar de clasificación.
  - POST /admin/reload -> recarga modelos, máscaras y configuración sin reiniciar el server.
- Dependencias mínimas: fastapi, uvicorn[standard], numpy, pydantic, Pillow.
- Estructura modular (routers, deps, config.yaml). Lectura de máscaras (PNG 790x490) como arrays binarios 0/1.
- Utilidades para normalizar imágenes (grises [0..1]), aplicar máscara (`img*mask`) y calcular Top-2 del diccionario de scores.
- Un sistema de configuraciones en **config.yaml** con campos: rutas, umbrales, ROIs por rasgo (x,y,w,h relativos a 790x490), y pesos por rasgo.
- Logging estructurado (uvicorn + logging.getLogger("app")).
- tests/ con al menos un test de /health.
Entrega el esqueleto completo listo para `uvicorn app.main:app --reload`.
```

---

## Opción 1 — **Reglas + plantillas de rasgos (Template Matching)**

```
Sobre el esqueleto FastAPI previo, implementa la **Opción 1** (rules):

- Librerías extra: opencv-python-headless, scikit-image, pyyaml.
- En app/deps.py:
  - Carga máscaras de `masks/*.png` (binarias 0/1).
  - Carga plantillas de rasgos desde `rasgos/<tipo>_<lado>/*.png`.
  - Carga ROIs y pesos desde config.yaml. Los ROIs son relativos (0..1) al canvas 790x490.
- Implementa utilidades:
  - `ncc_score(img_roi, template)`: usa cv2.matchTemplate con método `TM_CCOEFF_NORMED`.
  - `ssim_score(img_roi, template)`: usa skimage.metrics.structural_similarity (solo la zona válida del ROI).
  - `score_feature(img, mask, roi, template, mode="ncc")` -> devuelve score∈[0,1].
  - `score_class(img, side, class_id)` -> suma ponderada de rasgos definidos en config.yaml para esa clase.
- En routers/classify.py:
  - POST /classify: 
      1) decodifica la imagen a (490,790) float32 [0..1].
      2) si no viene `side`, estima por reglas rápidas (p.ej., presencia de rasgos back/front si en config.yaml hay `side_rules`). Si no se puede, intenta ambos lados y quédate con el mejor score.
      3) Calcula score por cada clase del lado correspondiente (t1,t2,t3).
      4) Si `max_score < cfg.thresholds.rules` => `tipo="unknown"`.
      5) Devuelve JSON estándar con `method="rules"` y los scores por rasgo.
- En config.yaml define ejemplo de ROIs por rasgo (placeholders) y pesos.
- Añade script `scripts/build_rois_example.py` que crea un config.yaml de ejemplo.
- Añade tests unitarios de `ncc_score` con arrays sintéticos.
- Dependencias en requirements.txt.
Entrega el código listo para ejecutar.
```

---

## Opción 2 — **Prototipos enmascarados (SSIM/NCC) + verificación de rasgos**

```
Implementa opción **rules+ssim** sobre FastAPI:

- Librerías extra: opencv-python-headless, scikit-image, joblib, pyyaml.
- scripts/build_prototypes.py:
  - Recorre `data/<tipo>/<lado>/*.png`, aplica la máscara correspondiente, acumula y guarda la media por clase en `models/prototypes.npz`.
- app/deps.py:
  - Función `load_prototypes()` que carga el .npz a un dict {("t1","front"): np.ndarray, ...}.
- Clasificación:
  - `ssim_class_score(img, side)` -> calcula SSIM en `img*mask` contra cada prototipo del `side`. Devuelve dict de scores.
  - Gana la clase con mayor SSIM. Si `< cfg.thresholds.ssim`, etiqueta **unknown**.
  - **Verificación de rasgos**: usa las mismas funciones de Opción 1 para validar que los rasgos obligatorios de la clase ganadora superan sus umbrales por-rasgo. Si no, anula a **unknown**.
- /admin/rebuild (POST): ejecuta `build_prototypes.py` desde el server (subproceso) o expón una función Python.
- Configura umbrales: `thresholds: { ssim: 0.60, feature_ncc: 0.65 }` (ajustables).
- tests/: prueba de que `load_prototypes` y `ssim_class_score` funcionan con datos sintéticos.
- Devuelve implementación completa con requirements.txt.
```

---

## Opción 3 — **SVM/HOG con máscara**

```
Implementa entrenamiento e inferencia SVM/HOG (6 clases).

- Librerías extra: scikit-image, scikit-learn, joblib, opencv-python-headless, pyyaml.
- scripts/train_svm.py:
  - Recorre `data/<tipo>/<lado>/*.png`. Para cada imagen:
      * carga, normaliza [0..1], aplica `mask` del `lado` (o específica por clase si config lo indica).
      * extrae HOG: pixels_per_cell=(16,16), cells_per_block=(2,2), orientations=9.
      * guarda (X, y) y entrena `LinearSVC` (o SVC RBF opcional).
      * guarda modelo con joblib en `models/svm_hog.pkl` y normalizador (StandardScaler si aplica).
- app/deps.py:
  - `load_svm()` que carga modelo + scaler.
- routers/classify.py:
  - Si no viene `side`, predice los 6 logits y toma top por lado; opcionalmente usa una cabecera de decisión para `front/back` primero.
  - Si `margin < cfg.thresholds.svm_margin` => unknown.
  - Devuelve JSON con `method="svm"`.
- /admin/train (POST): allow running `scripts/train_svm.py` (opcional).
- Tests con dataset sintético (parches con bordes/texturas) para verificar pipeline.
- Entrega proyecto listo con requirements.txt.
```

---

## Opción 4 — **CNN ligera (MobileNetV3/ResNet-18) con gris enmascarado**

```
Implementa una CNN pequeña para 6 clases, con FastAPI para inferencia.

- Librerías extra: torch, torchvision, opencv-python-headless, pyyaml, numpy; opcional onnxruntime-gpu/onnxruntime.
- scripts/train_cnn.py:
  - Dataset: lee `data/<tipo>/<lado>/*.png`, aplica máscara (fuera de máscara=0), normaliza.
  - Modelos a elegir con flag: `resnet18` (in_channels=1) o `mobilenet_v3_small` (ajusta primera conv a 1 canal).
  - Augmentations ligeros: rot±5°, JPEG artefacts, blur, brightness/contrast, banding.
  - Pérdida: CrossEntropy (opcional FocalLoss); optim: AdamW (lr=3e-4).
  - Early stopping por val F1 macro.
  - Guarda `models/cnn.pt` y opcional `models/cnn.onnx`.
- app/deps.py:
  - Carga torch model en eval; si existe ONNX y `cfg.inference.backend=="onnx"`, usa onnxruntime.
- routers/classify.py:
  - Preprocesa a tensor (1×1×490×790), aplica máscara del lado apropiado.
  - Devuelve `p_max`, `label`, `top2`. Si `p_max < cfg.thresholds.cnn_pmax` => unknown.
- Añade script `scripts/export_onnx.py` para exportar a ONNX.
- Añade tests de inferencia con tensores sintéticos.
- requirements.txt actualizado.
```

---

## Opción 5 — **Embeddings prototípicos (few-shot)**

```
Implementa clasificación por embeddings y centros de clase.

- Librerías extra: torch, torchvision, numpy, joblib, pyyaml, opencv-python-headless.
- scripts/build_embeddings.py:
  - Modelo base: ResNet-18 con primera conv adaptada a 1 canal; elimina la capa final y deja un head de 256D.
  - Para cada `data/<tipo>/<lado>/*.png` -> `img*mask` -> `z∈R^256` -> guarda por clase.
  - Calcula **centros** `c_k` y `var` intra-clase. Persiste en `models/proto_centers.npz`.
- app/deps.py:
  - `load_embed_model()` y `load_proto_centers()`.
- Clasificación en routers/classify.py:
  - `z = f(img*mask)`; `dist_k = 1 - cos(z, c_k)`; `k* = argmin dist_k`.
  - Si `dist_min > cfg.thresholds.proto_cosine` => unknown.
  - Devuelve JSON con `method="proto"` y top2 por distancia invertida.
- /admin/update_centroid (POST):
  - Permite subir nuevas imágenes etiquetadas para recalcular centros de una clase.
- Tests con datos sintéticos para validar distancias.
- requirements.txt actualizado.
```

---

## Snippet de `config.yaml` (ejemplo mínimo)

```yaml
paths:
  masks: "masks"
  rasgos: "rasgos"
  models: "models"
thresholds:
  rules: 0.65
  ssim: 0.60
  feature_ncc: 0.65
  svm_margin: 0.20
  cnn_pmax: 0.80
  proto_cosine: 0.20
weights:
  # pesos por rasgo (placeholders)
  t1_back:
    QRdoble: 0.4
    QRchico: 0.3
    roseta: 0.3
# ROIs relativos (0..1) por rasgo (placeholders)
rois:
  t1_front:
    escudo_grecas: [0.00,0.00,0.20,0.35]
    ine_header:    [0.25,0.02,0.70,0.10]
    fecha_seccion: [0.35,0.68,0.40,0.08]
    mapa_mx:       [0.85,0.85,0.12,0.12]
```

---

## Comandos sugeridos

```bash
# Crear entorno y deps base
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install fastapi "uvicorn[standard]" numpy Pillow pydantic pyyaml

# Según opción
pip install opencv-python-headless scikit-image joblib scikit-learn   # Opción 1–3
pip install torch torchvision onnxruntime                             # Opción 4–5 (ajusta a GPU si aplica)

# Ejecutar servicio
uvicorn app.main:app --reload
```

> Copia el prompt de la opción deseada en Trae para que te genere el código. Puedes encadenar el **Prompt maestro** + la **opción** elegida.
