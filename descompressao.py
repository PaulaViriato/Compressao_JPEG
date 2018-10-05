import sys
import cv2
import numpy as np
import matplotlib.pyplot as plot
import math
from PIL import Image

tqua = [[16, 11, 10, 16, 24,  40,  51,  61],
        [12, 12, 14, 19, 26,  58,  60,  55],
        [14, 13, 16, 24, 40,  57,  69,  56],
        [14, 17, 22, 29, 51,  87,  80,  62],
        [18, 22, 37, 56, 68,  109, 103, 77],
        [24, 35, 55, 64, 81,  104, 113, 92],
        [79, 64, 78, 87, 103, 121, 120, 101],
        [72, 92, 95, 98, 112, 100, 103, 99]]

def exibicao (imagem, texto, caminho):
    plot.subplot(121)
    plot.imshow(imagem, cmap = 'gray')
    cv2.imwrite(caminho[:(len(caminho)-5)]+"_pjpg.png", imagem)
    plot.title(str(texto)), plot.xticks([]), plot.yticks([])
    plot.show()

def quantizacao (matriz, hi, hf, wi, wf):
    mat_qua = matriz

    for i in range(hi, hf):
        for j in range(wi, wf):
            mat_qua[i][j] = matriz[i][j]*tqua[i%8][j%8]

    return mat_qua

def nucdct (m, u):
    inter  = math.pi*(2*m +1)*u
    inter /= 16
    return math.cos(inter)

def kdct (value):
    if (value == 0):
        return float(1/math.sqrt(2))
    else:
        return float(1)

def dct (matriz, hi, hf, wi, wf):
    mat_dct = []

    for u in range(hi, hf):
        line_dct = []
        for v in range(wi, wf):
            soma = 0

            for i in range(hi, hf):
                for j in range(wi, wf):
                    soma += ((kdct(i%8)*kdct(j%8))/4)*matriz[i][j]*nucdct(u%8,i%8)*nucdct(v%8,j%8)
            if (soma < 0):
                soma *= -1
            line_dct.append(int(soma))
        mat_dct.append(line_dct)

    return mat_dct

def descompressao_jpeg (caminho):
    arq = open(caminho,"rb")
    arq.seek(0,2)
    tamanho = arq.tell()
    arq.seek(0)

    height = int.from_bytes(arq.read(4), 'big')
    width  = int.from_bytes(arq.read(4), 'big')
    matriz = []

    for i in range(height):
        line = []
        for j in range(width):
            line.append(int.from_bytes(arq.read(1), 'big'))
        matriz.append(line)

    codigo = []
    while arq.tell() < tamanho:
        sig = (str(arq.read(1)))[2]
        valor = int.from_bytes(arq.read(1), 'big')
        if (sig == "-"):
            valor *= -1
        codigo.append(valor)

    for i in range(height):
        for j in range(width):
            matriz[i][j] = codigo[matriz[i][j]]

    mat_res = []
    for i in range(height):
        line_res = []
        for j in range(width):
            line_res.append(int(0))
        mat_res.append(line_res)

    for i in range(0, height, 8):
        x=i+8
        if (x>=height):
            x = height
        for j in range(0, width, 8):
            y=j+8
            if (y>=width):
                y=width
            mat = quantizacao (matriz, i, x, j, y)
            mat = dct (mat, i, x, j, y)
            
            for m in range(len(mat)):
                for n in range(len(mat[0])):
                    mat_res[i+m][j+n] = int(mat[m][n])

    imagem = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            imagem[i,j,0] = mat_res[i][j]
            imagem[i,j,1] = mat_res[i][j]
            imagem[i,j,2] = mat_res[i][j]

    return imagem

if __name__ == "__main__":
    caminho = str(input("Caminho imagem: "))
    imagem = descompressao_jpeg (caminho)
    exibicao (imagem, "Imagem de Saida: ", caminho)