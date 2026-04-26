# Hand Gesture Controller

Sistema HCI per macOS che controlla mouse, scroll e volume tramite gesti della mano usando webcam + MediaPipe.

## Requisiti
- macOS 12+ (Monterey o superiore)
- Python 3.11+
- Webcam integrata o esterna
- Permessi Accessibilità (obbligatori per controllo mouse)

## Installazione

```bash
git clone ...
cd hand-gesture-controller
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Permessi macOS (OBBLIGATORIO)

Per permettere all’app di muovere il cursore e cliccare:

1. Apri **Preferenze di Sistema**
2. Vai su **Privacy e Sicurezza → Accessibilità**
3. Abilita e/o aggiungi **Terminal** (o iTerm2 / il tuo IDE)
4. Riavvia il terminale/IDE se necessario

Senza questi permessi, il mouse potrebbe non muoversi.

## Gesti disponibili

| GestureType | Gesto fisico | Azione |
|---|---|---|
| REST | Mano non visibile o palmo non verso camera | Nessuna azione (reset controller) |
| NAVIGATE | Solo indice alzato | Muove il cursore seguendo l’indice |
| CLICK | Pinch pollice + indice (rilascio) | Click sinistro (al rilascio del pinch) |
| SCROLL | Indice + medio alzati | Scroll verticale in base al movimento |
| VOLUME | Pinch pollice + medio | Controllo volume (0–100%) |

## Avvio

```bash
python main.py
```

Al primo avvio MediaPipe Tasks scarica automaticamente il modello in `models/hand_landmarker.task` (~25MB).

## Configurazione

I parametri principali in `config.py` che potresti voler modificare:

- `MouseConfig.SMOOTHING_FACTOR`: smoothing del cursore (0=nessuno, 1=massimo)
- `TrackingConfig.PINCH_THRESHOLD`: soglia pinch (più basso = più “stretta”)
- `MouseConfig.SPEED_MULTIPLIER`: moltiplicatore velocità mapping (se desideri più rapidità/ampiezza)

