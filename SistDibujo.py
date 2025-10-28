import cv2
import mediapipe as mp
import math
import time

# Inicializar la cámara
camara = cv2.VideoCapture(1)
camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camara.set(cv2.CAP_PROP_FPS, 60)  # Solicitar 60 FPS a la cámara

# Herramientas de MediaPipe para dibujar y detectar manos
utilidades_dibujo = mp.solutions.drawing_utils 
solucion_manos = mp.solutions.hands 

# Optimizar MediaPipe para mayor velocidad
detector_manos = solucion_manos.Hands(
    static_image_mode=False,  # Modo video
    max_num_hands=2,  # Detectar 2 manos 
    model_complexity=1  # Modelo (0=ligero, 1=completo)
)

# Lista para guardar los puntos del dibujo
puntos_dibujo = []

# Variables para calcular FPS
tiempo_anterior = 0

while True:
    captura_exitosa, fotograma = camara.read()
    if captura_exitosa:
        fotograma = cv2.flip(fotograma, 1)  # Efecto espejo
        
        # Calcular FPS
        tiempo_actual = time.time()
        fps = 1 / (tiempo_actual - tiempo_anterior)
        tiempo_anterior = tiempo_actual
        
        # Convertir a RGB para MediaPipe
        fotograma_rgb = cv2.cvtColor(fotograma, cv2.COLOR_BGR2RGB)
        resultado_deteccion = detector_manos.process(fotograma_rgb) # Procesar el fotograma
        
        # Mostrar FPS en pantalla
        cv2.putText(fotograma, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if resultado_deteccion.multi_hand_landmarks: # Si se detectan manos
            for puntos_mano in resultado_deteccion.multi_hand_landmarks: # Para cada punto en la mano detectada
                utilidades_dibujo.draw_landmarks(fotograma, puntos_mano, solucion_manos.HAND_CONNECTIONS) # Dibujar landmarks
                
                # Obtener dimensiones del fotograma
                altura, ancho, canales = fotograma.shape
                
                # Obtener coordenadas del pulgar (4), índice (8) y anular (16)
                punta_pulgar = puntos_mano.landmark[4]
                punta_indice = puntos_mano.landmark[8]
                punta_anular = puntos_mano.landmark[16]
                
                # Convertir a coordenadas de píxeles
                pulgar_x = int(punta_pulgar.x * ancho)
                pulgar_y = int(punta_pulgar.y * altura)
                indice_x = int(punta_indice.x * ancho)
                indice_y = int(punta_indice.y * altura)
                anular_x = int(punta_anular.x * ancho)
                anular_y = int(punta_anular.y * altura)
                
                # Calcular distancia entre dedos
                distancia_dedos = math.sqrt((pulgar_x - indice_x)**2 + (pulgar_y - indice_y)**2) 
                distancia_anular_pulgar = math.sqrt((pulgar_x - anular_x)**2 + (pulgar_y - anular_y)**2)

                # Si la distancia entre pulgar e índice es menor a 25 píxeles, están juntos
                if distancia_dedos < 25:
                    # Calcular punto medio entre los dedos
                    punto_medio_x = (pulgar_x + indice_x) // 2
                    punto_medio_y = (pulgar_y + indice_y) // 2
                    # Dibujar círculo verde en el punto medio
                    cv2.circle(fotograma, (punto_medio_x, punto_medio_y), 5, (0, 255, 0), -1)
                    puntos_dibujo.append((punto_medio_x, punto_medio_y))
                elif distancia_anular_pulgar < 30:  # Si pulgar y anular están juntos
                    # Dibujar círculo negro para borrar
                    punto_medio_x = (pulgar_x + anular_x) // 2
                    punto_medio_y = (pulgar_y + anular_y) // 2
                    cv2.circle(fotograma, (punto_medio_x, punto_medio_y), 20, (0, 0, 0), 2)

                    # Borrar puntos dentro del radio
                    for punto in puntos_dibujo[:]:  # Iterar sobre una copia de la lista
                        if punto is not None:
                            if (punto[0] >= pulgar_x - 20 and punto[0] <= pulgar_x + 20 and
                                punto[1] >= pulgar_y - 20 and punto[1] <= pulgar_y + 20):
                                puntos_dibujo.remove(punto)

                else:
                    if len(puntos_dibujo) > 0:
                        puntos_dibujo.append(None)  # Separador para líneas discontinuas
                
                # Visualizar los puntos del índice y pulgar
                cv2.circle(fotograma, (pulgar_x, pulgar_y), 5, (255, 0, 0), -1)  # Azul
                cv2.circle(fotograma, (indice_x, indice_y), 5, (0, 0, 255), -1)  # Rojo
                cv2.circle(fotograma, (anular_x, anular_y), 5, (255, 255, 0), -1)  # Cyan
        
        # Dibujar todas las líneas guardadas
        for i in range(1, len(puntos_dibujo)):
            if puntos_dibujo[i] is not None and puntos_dibujo[i-1] is not None:
                cv2.line(fotograma, puntos_dibujo[i-1], puntos_dibujo[i], (0, 255, 0), 3)
        
        cv2.imshow("Webcam", fotograma)
        
        # Presiona 'q' para salir, 'c' para limpiar el dibujo
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('q'):
            break
        elif tecla == ord('c'):
            puntos_dibujo = []

camara.release()
cv2.destroyAllWindows()

