import cv2
import mediapipe as mp
import math
import time
import pyautogui

# Inicializar la cámara
camara = cv2.VideoCapture(1)
camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camara.set(cv2.CAP_PROP_FPS, 60)

# Herramientas de MediaPipe para dibujar y detectar manos
utilidades_dibujo = mp.solutions.drawing_utils 
solucion_manos = mp.solutions.hands 

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
ultima_agachada = 0
cooldown = 0.3  # Tiempo mínimo entre acciones (segundos)

# Umbrales de distancia
DISTANCIA_SALTO = 100  # Distancia mínima para saltar (dedos alejados)
DISTANCIA_AGACHADA = 30  # Distancia máxima para agacharse (dedos cerca)

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
        resultado_deteccion = detector_manos.process(fotograma_rgb)
        
        # Mostrar FPS en pantalla
        cv2.putText(fotograma, f"FPS: {int(fps)}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if resultado_deteccion.multi_hand_landmarks:
            for puntos_mano in resultado_deteccion.multi_hand_landmarks:
                utilidades_dibujo.draw_landmarks(fotograma, puntos_mano, 
                                                solucion_manos.HAND_CONNECTIONS)
                
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
                distancia_dedos = math.sqrt((pulgar_x - indice_x)**2 + 
                                          (pulgar_y - indice_y)**2)
                
                # Mostrar distancia en pantalla
                cv2.putText(fotograma, f"Distancia: {int(distancia_dedos)}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                
                # Línea entre los dedos
                cv2.line(fotograma, (pulgar_x, pulgar_y), (indice_x, indice_y), 
                        (255, 0, 255), 2)
                
                # SALTAR: Dedos alejados
                if distancia_dedos > DISTANCIA_SALTO:
                    if time.time() - ultimo_salto > cooldown:
                        pyautogui.press('space')  # Presionar espacio para saltar
                        ultimo_salto = time.time()
                        cv2.putText(fotograma, "SALTANDO!", (10, 90), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                # AGACHARSE: Dedos juntos
                elif distancia_dedos < DISTANCIA_AGACHADA:
                    if time.time() - ultima_agachada > cooldown:
                        pyautogui.keyDown('down')  # Mantener tecla abajo presionada
                        time.sleep(0.1)
                        pyautogui.keyUp('down')
                        ultima_agachada = time.time()
                        cv2.putText(fotograma, "AGACHADO!", (10, 90), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Visualizar los puntos del índice y pulgar
                cv2.circle(fotograma, (pulgar_x, pulgar_y), 10, (255, 0, 0), -1)  # Azul
                cv2.circle(fotograma, (indice_x, indice_y), 10, (0, 0, 255), -1)  # Rojo
        
        # Instrucciones en pantalla
        cv2.putText(fotograma, "Aleja dedos = SALTAR", (10, altura - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(fotograma, "Junta dedos = AGACHARSE", (10, altura - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Control Dinosaurio", fotograma)
        
        # Presiona 'q' para salir
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('q'):
            break

camara.release()
cv2.destroyAllWindows()