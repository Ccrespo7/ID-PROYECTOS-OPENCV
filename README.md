# Control Dinosaurio (detección de manos)

Descripción
- Script en Python que controla acciones (saltar / agacharse) usando MediaPipe + OpenCV detectando distancia entre pulgar y meñique. Simula teclas con pyautogui.

Requisitos
- Python 3.11
- Cámara USB o integrada
- Sistema con interfaz gráfica (Windows recomendado)

Dependencias (requirements.txt)
- opencv-python
- mediapipe
- pyautogui

Instalación (Windows)
1. Instalar dependencias:
   pip install -r requirements.txt

2. Crear Entorno Virtual(SI TIENES OTRA VERSION DE PYTHON)
    Dentro del vscode aprietas CTRL + SHIFT + P
    Buscas Python: Select Interpreter y seleccionas la version 3.11.0
    Ejecutas

Ejecución
- Ejecutar el script principal:
  python Dino.py

Notas importantes
- El script usa por defecto VideoCapture(1). Si tu webcam es la principal cambia a 0 en el archivo:
  camara = cv2.VideoCapture(1)  ->  camara = cv2.VideoCapture(0)
- Ajusta DISTANCIA_SALTO y DISTANCIA_AGACHADA según la distancia cámara-usuario para evitar falsos positivos.
- Asegúrate de que la ventana del juego (o la aplicación que recibe teclas) tenga foco; pyautogui envía eventos a nivel de sistema pero la aplicación destino debe aceptar entradas.
- Presionar 'q' en la ventana para salir. El script libera la tecla "down" si se quedó pulsada al cerrar.

