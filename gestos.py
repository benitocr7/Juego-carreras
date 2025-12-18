# gestos.py

# Guardamos la posición inicial (neutra)
posicion_inicial = None

def detectar_gesto(hand):
    global posicion_inicial

    # Landmark 0 = muñeca
    wrist = hand.landmark[0]

    x = wrist.x
    y = wrist.y

    # Guardar posición inicial
    if posicion_inicial is None:
        posicion_inicial = (x, y)
        return "NONE"

    x0, y0 = posicion_inicial

    # Diferencias
    dx = x - x0
    dy = y - y0

    # Umbrales (ajustables)
    THRESHOLD_X = 0.05
    THRESHOLD_Y = 0.05

    # Prioridad vertical si es más fuerte
    if abs(dy) > abs(dx):
        if dy < -THRESHOLD_Y:
            return "UP"
        elif dy > THRESHOLD_Y:
            return "DOWN"
    else:
        if dx < -THRESHOLD_X:
            return "LEFT"
        elif dx > THRESHOLD_X:
            return "RIGHT"

    return "STRAIGHT"
