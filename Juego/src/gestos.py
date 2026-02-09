# gestos.py

import math

DEDOS = [
    (6, 8),   # índice
    (10, 12), # medio
    (14, 16), # anular
    (18, 20)  # meñique
]

def mano_abierta(hand):
    abiertos = 0
    for base, punta in DEDOS:
        if hand.landmark[punta].y < hand.landmark[base].y:
            abiertos += 1
    return abiertos >= 3


def mano_girada_izquierda(hand):
    wrist = hand.landmark[0]
    thumb = hand.landmark[4]
    return thumb.x < wrist.x


def mano_girada_derecha(hand):
    wrist = hand.landmark[0]
    thumb = hand.landmark[4]
    return thumb.x > wrist.x


def pulgar_cerrado(hand):
    tip = hand.landmark[4]
    # Centro de la palma: promedio de 0,5,9,13,17
    palm_x = (hand.landmark[0].x + hand.landmark[5].x + hand.landmark[9].x + hand.landmark[13].x + hand.landmark[17].x) / 5
    palm_y = (hand.landmark[0].y + hand.landmark[5].y + hand.landmark[9].y + hand.landmark[13].y + hand.landmark[17].y) / 5
    dist = math.sqrt((tip.x - palm_x)**2 + (tip.y - palm_y)**2)
    return dist < 0.2 and tip.y > palm_y


def detectar_gestos_manos(manos, handedness):
    if len(manos) < 2:
        return ["NONE"]

    izquierda_abierta = False
    derecha_abierta = False
    izquierda_pulgar_cerrado = False
    derecha_pulgar_cerrado = False
    hay_puno = False

    for i, hand in enumerate(manos):
        abierta = mano_abierta(hand)
        pulgar_cerrado_val = pulgar_cerrado(hand)
        tipo = handedness[i].classification[0].label  # Left / Right

        if not abierta:
            hay_puno = True

        if abierta:
            if tipo == "Left":
                izquierda_abierta = True
            elif tipo == "Right":
                derecha_abierta = True

        if pulgar_cerrado_val:
            if tipo == "Left":
                izquierda_pulgar_cerrado = True
            elif tipo == "Right":
                derecha_pulgar_cerrado = True

    gestos = []
    if hay_puno:
        gestos.append("STOP")
    if izquierda_abierta and derecha_abierta:
        gestos.append("ACCEL")
    if izquierda_pulgar_cerrado:
        gestos.append("LEFT")
    if derecha_pulgar_cerrado:
        gestos.append("RIGHT")
    if not gestos:
        gestos.append("NONE")
    return gestos
