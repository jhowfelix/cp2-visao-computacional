import cv2
import time
import numpy as np
import math
import pynput
from pynput.keyboard import Controller
import os, sys, os.path

# verde
greenLower = (52, 86, 6)
greenUpper = (87, 255, 255)

# amarelo
yellowLower = (24, 55, 55)
yellowUpper = (50, 255, 255)


def filtro_de_cor(imagem_bgr, low_hsv, high_hsv):
    # Filtrando a imagem capturada para pegar apenas as cores que definimos 
    imagem = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(imagem, low_hsv, high_hsv)
    return mask


def mascara_or(mask1, mask2):
    # Máscara or
    mask = cv2.bitwise_or(mask1, mask2)
    return mask


def mascara_and(mask1, mask2):
    # Máscara and
    mask = cv2.bitwise_and(mask1, mask2)

    return mask


def desenha_cruz(imagem, cX, cY, size, color):
    # fazer a cruz no ponto cx cy
    cv2.line(imagem, (cX - size, cY), (cX + size, cY), color, 5)
    cv2.line(imagem, (cX, cY - size), (cX, cY + size), color, 5)


def mostrar_texto(imagem, text, origem, color):
    # fazer a cruz no ponto cx cy
    # Mostrar o texto, com angulo e centro.
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(imagem, str(text), origem, font, 0.4, color, 1, cv2.LINE_AA)




def controls(angulo, area):
    # Criando um Array com as teclas que serão utilizadas para controlar o carro.
    keys = [
        # Acelerar
        pynput.keyboard.KeyCode.from_char('w'),
        # Ré
        pynput.keyboard.KeyCode.from_char('s'),
        # Virar esquerda
        pynput.keyboard.KeyCode.from_char('a'),
        # Virar direita
        pynput.keyboard.KeyCode.from_char('d'),
    ]
    # Criar a lista fora da função. 
    keyboard = Controller()
    # Sleep de 0.3
    if angulo > 270 and angulo < 340:
        keyboard.press(keys[3])
        print("Pressionando a tecla: ", keys[3])
        time.sleep(0.3)
        keyboard.release(keys[3])
    if angulo < 90 and angulo > 20:
        keyboard.press(keys[2])
        print("Pressionando a tecla: ", keys[2])
        time.sleep(0.3)
        keyboard.release(keys[2])
    if area > 5500:
        keyboard.press(keys[0])
        print("Pressionando a tecla: ", keys[0])
        time.sleep(0.3)
        keyboard.release(keys[0])
    if area < 3500 and angulo > 0:
        keyboard.press(keys[1])
        print("Pressionando a tecla: ", keys[1])
        time.sleep(0.3)
        keyboard.release(keys[1])


def webcam(imagem):
    contorno_da_imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)

    maskGreen = cv2.inRange(contorno_da_imagem, greenLower, greenUpper)
    maskGreen = cv2.erode(maskGreen, None, iterations=2)
    maskGreen = cv2.dilate(maskGreen, None, iterations=2)

    maskYellow = cv2.inRange(contorno_da_imagem, yellowLower, yellowUpper)
    maskYellow = cv2.erode(maskYellow, None, iterations=2)
    maskYellow = cv2.dilate(maskYellow, None, iterations=2)

    # Encontrar contornos da mascara e inicializar a corrente
    # Encontrando os contorno da mascara | Inicializando a corrente.
    cntGreen = cv2.findContours(maskGreen.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
   
    cntYellow = cv2.findContours(maskYellow.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    

    # Unica proceder se pelo menos um contorno foi encontrado
    # Se pelo menos um contorno for encontrado
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    area1 = 0
    area2 = 0

    # Verificando se existe cortorno verde, caso sim, calcula e exibe no display.
    if len(cntGreen) > 0:
        cGreen = max(cntGreen, key = cv2.contourArea)
        MGreen = cv2.moments(cGreen)
        if MGreen["m00"] != 0:
            x1 = int(MGreen["m10"] / MGreen["m00"])
            y1 = int(MGreen["m01"] / MGreen["m00"])
        rectGreen = cv2.minAreaRect(cGreen)
        boxGreen = cv2.boxPoints(rectGreen)
        boxGreen = np.int0(boxGreen)
    
        cv2.drawContours(contorno_da_imagem, [boxGreen], 0, (0, 255, 0), 2)
        desenha_cruz(contorno_da_imagem, x1, y1, 20, (0, 255, 0))
        area1 = cv2.contourArea(cGreen)
        texto = "CENTRO: ", y1, x1, " ÁREA: ", area1
        origem = (0, 50)
        mostrar_texto(contorno_da_imagem, texto, origem, (0, 255, 0))


     # Verificando se existe contorno amarelo, caso sim, calcula e exibe no display. O verde.
    if len(cntYellow) > 0:
        cYellow = max(cntYellow, key=cv2.contourArea)
        MYellow = cv2.moments(cYellow)
        if MYellow["m00"] != 0:
            x2 = int(MYellow["m10"] / MYellow["m00"])
            y2 = int(MYellow["m01"] / MYellow["m00"])
        rectYellow = cv2.minAreaRect(cYellow)
        boxYellow = cv2.boxPoints(rectYellow)
        boxYellow = np.int0(boxYellow)
      
        cv2.drawContours(contorno_da_imagem, [boxYellow], 0, (0, 255, 255), 2)
        desenha_cruz(contorno_da_imagem, x2, y2, 20, (0, 255, 255))
        area2 = cv2.contourArea(cYellow)
        texto = "Centro: ", y2, x2, " Area: ", area2
        origem = (0, 50)
        mostrar_texto(contorno_da_imagem, texto, origem, (0,255,0))

    color = (255, 255, 255)
    cv2.line(contorno_da_imagem, (x1, y1), (x2, y2), color, 5)

    vY = y1 - y2
    vX = x1 - x2
    rad = math.atan2(vY, vX)
    angulo = math.degrees(rad)
    if angulo < 0:
        angulo += 360

    mediaArea = (area1 + area2) / 2
    controls(angulo, mediaArea)
    texto = "angulo: ", angulo
    origem = (0, 100)
    mostrar_texto(contorno_da_imagem, texto, origem, (0, 255, 255))
    contorno_da_imagem2 = cv2.cvtColor(contorno_da_imagem, cv2.COLOR_HSV2BGR)
    return contorno_da_imagem2


# Definindo nome da janelinha
cv2.namedWindow("CP2")
# define a entrada de video para webcam
vc = cv2.VideoCapture(0)

# configuração do tamanho da janela.
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 620)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 420)

if vc.isOpened():  # Tenta pegar o primeiro frame da webcam
    rval, frame = vc.read()
else:
    rval = False

# Rodar enquanto estiver recebendo frame
while rval:
    imagem = webcam(frame)
    cv2.imshow("CP2", imagem)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27:  # Para fechar a aplicação
        break
cv2.destroyWindow("CP2")

# Desliga o recurso, webcam.
vc.release()
