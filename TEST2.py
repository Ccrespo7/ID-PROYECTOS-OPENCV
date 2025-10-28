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
esta_dibujando = False

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
                
                # Obtener coordenadas del pulgar (4) e índice (8)
                punta_pulgar = puntos_mano.landmark[4]
                punta_indice = puntos_mano.landmark[8]
                
                # Convertir a coordenadas de píxeles
                pulgar_x = int(punta_pulgar.x * ancho)
                pulgar_y = int(punta_pulgar.y * altura)
                indice_x = int(punta_indice.x * ancho)
                indice_y = int(punta_indice.y * altura)
                
                # Calcular distancia entre dedos
                distancia_dedos = math.sqrt((pulgar_x - indice_x)**2 + (pulgar_y - indice_y)**2) 

                # Si la distancia es menor a 25 píxeles, están juntos
                if distancia_dedos < 25:
                    esta_dibujando = True
                    # Calcular punto medio entre los dedos
                    punto_medio_x = (pulgar_x + indice_x) // 2
                    punto_medio_y = (pulgar_y + indice_y) // 2
                    # Dibujar círculo verde en el punto medio
                    cv2.circle(fotograma, (punto_medio_x, punto_medio_y), 5, (0, 255, 0), -1)
                    puntos_dibujo.append((punto_medio_x, punto_medio_y))
                else:
                    esta_dibujando = False
                    if len(puntos_dibujo) > 0:
                        puntos_dibujo.append(None)  # Separador para líneas discontinuas
                
                # Visualizar los puntos del índice y pulgar
                cv2.circle(fotograma, (pulgar_x, pulgar_y), 5, (255, 0, 0), -1)  # Azul
                cv2.circle(fotograma, (indice_x, indice_y), 5, (0, 0, 255), -1)  # Rojo
        
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

