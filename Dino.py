import cv2 # Biblioteca para procesamiento de imágenes
import mediapipe as mp # Biblioteca para detección de manos
import math # Biblioteca para cálculos matemáticos
import time # Biblioteca para manejo de tiempo
import pyautogui # Biblioteca para control de teclado

# Inicializar la cámara
camara = cv2.VideoCapture(1)
camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camara.set(cv2.CAP_PROP_FPS, 60)

# Herramientas de MediaPipe para dibujar y detectar manos
utilidades_dibujo = mp.solutions.drawing_utils # Herramientas de dibujo
solucion_manos = mp.solutions.hands # Herramienta para detección de manos

# Optimizar MediaPipe para mayor velocidad
detector_manos = solucion_manos.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1
)

# Variables para calcular FPS
tiempo_anterior = 0

# Variables de control para evitar múltiples pulsaciones
ultimo_salto = 0
cooldown_salto = 0.2  # Tiempo mínimo entre saltos (segundos)

# Estado del agachado
esta_agachado = False

# Umbrales de distancia
DISTANCIA_SALTO = 100  # Distancia mínima para saltar (dedos alejados)
DISTANCIA_AGACHADA = 45  # Distancia máxima para agacharse (dedos cerca)

# Colores para los diferentes estados (BGR)
COLOR_SALTO = (255, 255, 0)  # Cian
COLOR_AGACHADO = (0, 165, 255)  # Naranja
COLOR_NORMAL = (255, 255, 255)  # Blanco

while True:
    captura_exitosa, fotograma = camara.read()
    if captura_exitosa:
        fotograma = cv2.flip(fotograma, 1)  # Efecto espejo

        # Obtener dimensiones del fotograma
        altura, ancho, canales = fotograma.shape

        # Calcular FPS
        tiempo_actual = time.time()
        fps = 1 / (tiempo_actual - tiempo_anterior)
        tiempo_anterior = tiempo_actual

        # Convertir a RGB para MediaPipe
        fotograma_rgb = cv2.cvtColor(fotograma, cv2.COLOR_BGR2RGB)
        resultado_deteccion = detector_manos.process(fotograma_rgb)

        # Mostrar FPS en pantalla
        cv2.putText(fotograma, f"FPS: {int(fps)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if resultado_deteccion.multi_hand_landmarks:
            puntos_mano = resultado_deteccion.multi_hand_landmarks[0]  # primera mano
            utilidades_dibujo.draw_landmarks(fotograma, puntos_mano, solucion_manos.HAND_CONNECTIONS)

            # Obtener coordenadas del pulgar (4) y meñique (20)
            punta_pulgar = puntos_mano.landmark[4]
            punta_menique = puntos_mano.landmark[20]

            # Convertir a coordenadas de píxeles
            pulgar_x = int(punta_pulgar.x * ancho)
            pulgar_y = int(punta_pulgar.y * altura)
            menique_x = int(punta_menique.x * ancho)
            menique_y = int(punta_menique.y * altura)

            # Calcular distancia entre dedos
            distancia_dedos = math.sqrt((pulgar_x - menique_x) ** 2 +
                                        (pulgar_y - menique_y) ** 2)

            # Determinar el color y estado según la distancia
            if distancia_dedos > DISTANCIA_SALTO:
                color_estado = COLOR_SALTO
                texto_estado = "SALTANDO!"
                grosor_linea = 4

                # Soltar la tecla down si estaba agachado
                if esta_agachado:
                    pyautogui.keyUp('down')
                    esta_agachado = False

                # Saltar
                if time.time() - ultimo_salto > cooldown_salto:
                    pyautogui.press('space')
                    ultimo_salto = time.time()

            elif distancia_dedos < DISTANCIA_AGACHADA:
                color_estado = COLOR_AGACHADO
                texto_estado = "AGACHADO!"
                grosor_linea = 4

                # Si no estaba agachado, agacharse
                if not esta_agachado:
                    pyautogui.keyDown('down')
                    esta_agachado = True

            else:
                color_estado = COLOR_NORMAL
                texto_estado = "NORMAL"
                grosor_linea = 3

                # Soltar la tecla down si estaba agachado
                if esta_agachado:
                    pyautogui.keyUp('down')
                    esta_agachado = False

            # Mostrar distancia con el color del estado
            cv2.putText(fotograma, f"Distancia: {int(distancia_dedos)}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, color_estado, 2)

            # Dibujar línea entre dedos con el color del estado
            cv2.line(fotograma, (pulgar_x, pulgar_y), (menique_x, menique_y),
                     color_estado, grosor_linea)

            # Mostrar estado actual
            cv2.putText(fotograma, texto_estado, (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color_estado, 3)

            # Visualizar los puntos del pulgar y meñique
            # Pulgar
            cv2.circle(fotograma, (pulgar_x, pulgar_y), 8, color_estado, -1)
            cv2.circle(fotograma, (pulgar_x, pulgar_y), 10, color_estado, 2)

            # Meñique
            cv2.circle(fotograma, (menique_x, menique_y), 8, color_estado, -1)
            cv2.circle(fotograma, (menique_x, menique_y), 10, color_estado, 2)

        else:
            # Si no se detecta la mano y estaba agachado, soltar tecla
            if esta_agachado:
                pyautogui.keyUp('down')
                esta_agachado = False

        # Instrucciones en pantalla 
        overlay = fotograma.copy()
        cv2.rectangle(overlay, (5, altura - 75), (400, altura - 5), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, fotograma, 0.5, 0, fotograma)

        cv2.putText(fotograma, "Aleja dedos = SALTAR", (10, altura - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_SALTO, 2)
        cv2.putText(fotograma, "Junta dedos = AGACHARSE", (10, altura - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_AGACHADO, 2)

        cv2.imshow("Control Dinosaurio", fotograma)

        # Presiona 'q' para salir
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('q'):
            break

# Asegurarse de soltar la tecla al salir
if esta_agachado:
    pyautogui.keyUp('down')

camara.release()
cv2.destroyAllWindows()