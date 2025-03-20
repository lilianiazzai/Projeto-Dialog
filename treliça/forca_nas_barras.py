import numpy as np
import random
import copy
import math

area = 0.0007  # m²
e = 200000000  # kN/m²

areas = [0.0003, 0.0004, 0.0005]
comprimentos = [1,2,3]
forcas = [10,10,10,10,10]

class No:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.forcas = np.array([0, 0]) 
        self.barras = []

    def adicionar_barra(self, barra):
        self.barras.append(barra)
    def aplicar_forca(self, forca):
        self.forcas += forca


class Barra:
    def __init__(self, no1, no2, comprimento, name):
        self.no1 = no1
        self.no2 = no2
        self.comprimento = comprimento
        self.name = name
        self.angulo = self.calcular_angulo()

    def calcular_angulo(self):
        return np.arctan2(self.no2.y - self.no1.y, self.no2.x - self.no1.x)

    def vetor(self):
        return np.array([self.no2.x - self.no1.x, self.no2.y - self.no1.y])

class Trelica:
    def __init__(self):
        self.nos = []
        self.barras = []
        self.comprimentos = []
        self.comprimentos_diagonais = []
        self.areas = random.choices(areas,k = 13)
        self.forcas = forcas
        self.fitness = 0
        self.delta_c = 0
        self.m = 0
        self.alfa = 0
        self.beta = 0
        self.gama = 0
        self.psi = 0
        self.lambida = 0
        self.omega = 0
        self.phi = 0
        self.sigma = 0
        self.mi = 0
        self.alfa2 = 0
        self.beta2 = 0
        self.gama2 = 0

    def gerar_comprimentos_nos_barras(self):
        l1 = random.choices(comprimentos)[0]
        l2 = random.choices(comprimentos)[0]
        l3 = random.choices(comprimentos)[0]
        l4 = random.choices(comprimentos)[0]
        l6 = random.choices(comprimentos)[0]
        l8 = random.choices(comprimentos)[0]
        l10 = random.choices(comprimentos)[0]
        l_diagonal = pow(l1 * l1 + l6 * l6, 1/2)
        l5 = l7 = l9 = l11 = l12 = l13 = l_diagonal
        self.comprimentos.append(l1)
        self.comprimentos.append(l2)
        self.comprimentos.append(l3)
        self.comprimentos.append(l4)
        self.comprimentos.append(l6)
        self.comprimentos.append(l8)
        self.comprimentos.append(l10)
        self.comprimentos_diagonais.append(l5)
        self.comprimentos_diagonais.append(l7)
        self.comprimentos_diagonais.append(l9)
        self.comprimentos_diagonais.append(l11)
        self.comprimentos_diagonais.append(l12)
        self.comprimentos_diagonais.append(l13)
        
        A = self.adicionar_no(0,0) 
        B = self.adicionar_no(l1,0) #B
        C = self.adicionar_no(l1+l2,0) #C
        D = self.adicionar_no(l1+l2+l3,0) #D
        E = self.adicionar_no(l1+l2+l3+l4,0) #E
        F = self.adicionar_no(l1,l6) #F
        H = self.adicionar_no(l1+l2,l8) #H
        G = self.adicionar_no(l1+l2+l3,l10) #G

        b1 = self.adicionar_barra(A, B, l1, "1")
        b2 = self.adicionar_barra(B,C,l2, "2")
        b3 = self.adicionar_barra(C,D,l3, "3")
        b4 = self.adicionar_barra(D,E,l4, "4")
        b5 = self.adicionar_barra(A,F,l5, "5")
        b6 = self.adicionar_barra(F,B,l6, "6")
        b7 = self.adicionar_barra(F,C,l7, "7")
        b8 = self.adicionar_barra(H,C,l8, "8")
        b9 = self.adicionar_barra(C,G,l9, "9")
        b10 = self.adicionar_barra(G,D,l10, "10")
        b11 = self.adicionar_barra(G,E,l11, "11")
        b12 = self.adicionar_barra(F,H,l12, "12")
        b13 = self.adicionar_barra(H,G,l13, "13")
    
    def trelica_nova(self, comprimentos, areas):
        self.comprimentos = comprimentos
        self.areas = areas

        self.nos.clear()
        self.barras.clear()

        l1 = self.comprimentos[0]
        l2 = self.comprimentos[1]
        l3 = self.comprimentos[2]
        l4 = self.comprimentos[3]
        l6 = self.comprimentos[4]
        l8 = self.comprimentos[5]
        l10 = self.comprimentos[6]

        l5 = pow(l1 * l1 + l6 * l6, 1/2)
        l7 = pow(l6 * l6 + l2 * l2, 1/2)
        l9 = pow(l10 * l10 + l3 * l3, 1/2)
        l11 = pow(l10 * l10 + l4 * l4, 1/2)
            
        l12 = pow((l8-l6)*(l8-l6) + l2*l2, 1/2)
        l13 = pow((l8-l10)*(l8-l10) + l3*l3, 1/2)
       
        self.comprimentos_diagonais = [l5,l7,l9,l11,l12,l13]

        A = self.adicionar_no(0,0) 
        B = self.adicionar_no(l1,0) #B
        C = self.adicionar_no(l1+l2,0) #C
        D = self.adicionar_no(l1+l2+l3,0) #D
        E = self.adicionar_no(l1+l2+l3+l4,0) #E
        F = self.adicionar_no(l1,l6) #F
        H = self.adicionar_no(l1+l2,l8) #H
        G = self.adicionar_no(l1+l2+l3,l10) #G

        b1 = self.adicionar_barra(A, B, l1, "1")
        b2 = self.adicionar_barra(B,C,l2, "2")
        b3 = self.adicionar_barra(C,D,l3, "3")
        b4 = self.adicionar_barra(D,E,l4, "4")
        b5 = self.adicionar_barra(A,F,l5, "5")
        b6 = self.adicionar_barra(F,B,l6, "6")
        b7 = self.adicionar_barra(F,C,l7, "7")
        b8 = self.adicionar_barra(H,C,l8, "8")
        b9 = self.adicionar_barra(C,G,l9, "9")
        b10 = self.adicionar_barra(G,D,l10, "10")
        b11 = self.adicionar_barra(G,E,l11, "11")
        b12 = self.adicionar_barra(F,H,l12, "12")
        b13 = self.adicionar_barra(H,G,l13, "13")

        return self

    def adicionar_no(self, x, y,):
        no = No(x, y)
        self.nos.append(no)
        return no

    def adicionar_barra(self, no1, no2, c, name):
        barra = Barra(no1, no2, c, name)
        self.barras.append(barra)
        no1.adicionar_barra(barra)
        no2.adicionar_barra(barra)
        return barra

    def aplicar_forca_no_no(self, no, forca):
        no.aplicar_forca(forca)

    def calcular_forcas_nas_barras(self):
        l1 = self.comprimentos[0]
        l2 = self.comprimentos[1]
        l3 = self.comprimentos[2]
        l4 = self.comprimentos[3]
        l6 = self.comprimentos[4]
        l8 = self.comprimentos[5]
        l10 = self.comprimentos[6]

        l5 = self.comprimentos_diagonais[0]
        l7 = self.comprimentos_diagonais[1]
        l9 = self.comprimentos_diagonais[2]
        l11 = self.comprimentos_diagonais[3]
        l12 = self.comprimentos_diagonais[4]
        l13 = self.comprimentos_diagonais[5]

        f1 = self.forcas[0]
        f2 = self.forcas[1]
        f3 = self.forcas[2]
        f4 = self.forcas[3]
        f5 = self.forcas[4]

        #forças de ação e reação
        Fxa = 0
        Fye = ((f2 * l6) + (f3 * l8) + (f4 * l10) + (f5 * (l1 + l2 + l3 + l4))) / (l1 + l2 + l3 + l4)
        Fya = (-1) * Fye + f1 + f2 + f3 + f4 + f5
        Fc = 0 #força total no eixo y no ponto c
        
        #forcas normais das barras q nao mudam independente da treliça
        Nb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        Nb[4] = (f1 - Fya) * l5 / l6
        Nb[0] = (-1) * Nb[4] * l1 / l5
        Nb[10] = ( (-1) * Fye + f5) * l11 / l10
        Nb[3] = (-1) * Nb[10] * l4 / l11
        Nb[5] = 0
        Nb[1] = Nb[0]
        Nb[9] = 0
        Nb[2] = Nb[3]
        
        #forças q mudam dependendo da treliça

        # H > F & H > G
        if l8 > l6 and l8 > l10:
            Nb[11] = (f2 + (Nb[4] * (l6 * (l2 + l1) / (l5 * l2)))) * l12 / l8
            Nb[6] = ((Nb[4] * l1 * l6) / (l5 * l2) - (Nb[11] * l6 / l12)) * l7 / l6
            Nb[12] = (Nb[11] * l2 * l13) / (l12 * l3)
            Nb[7] = f3 + (Nb[11] * (l8 - l6) / l12) + (Nb[12] * (l8 - l10) / l13)
            Nb[8] = (f4 - (Nb[12] * (l8 - l10) / l13) + (Nb[10] * l10 / l11)) * (-1) * l9 / l10
            Fc = ((Nb[6] * l6 / l7) + Nb[7] + (Nb[8] * l10 / l9))
        

        # H = F & H = G
        if l6 == l8 and l6 == l10:
            Nb[6] = f2 + (Nb[4] *  l7 / l5)
            Nb[11] = (Nb[4] * l1 / l5) - (Nb[6] * l2 / l7)
            Nb[7] = (-1) * f3
            Nb[12] = Nb[11]
            Nb[8] = (f4 + Nb[9] + (Nb[10] * l10 / l11)) * (-1) * l9 / l10
            Fc = ((Nb[6] * l8 / l7) + Nb[7] + (Nb[8] * l8 / l9))

        # F < H = G
        if l6 < l8 == l10 :
            Nb[11] = (f2 + (Nb[4] * ((l6 * l2) + (l1 * l6)) / (l5 * l2))) * l12 / l8
            Nb[6] = ((Nb[4] * l1 / l5) - (Nb[12] * l2 / l12)) * l7 / l12
            Nb[7] = (-1) * f3 - (Nb[11] * (l8 - l6) / l12)
            Nb[12] = Nb[11] * l2 / l12
            Nb[8] = (f4 + Nb[9] + ( Nb[10] * l10 / l11)) * (-1) * l9 / l10
            Fc = ((Nb[6] * l6 / l7) + Nb[7] + (Nb[8] * l10 / l9))
            
        # F = H > G
        if l6 == l8 > l10 :
            Nb[6] = (f2 + (Nb[4] * l6 / l5)) * (-1) * l7 / l6
            Nb[11] = (Nb[4] * l1 / l5) - ( Nb[6] * l2 / l6)
            Nb[12] = Nb[11] * l13 / l3
            Nb[7] = ((-1) * f3) - (Nb[12] * (l8 - l10) / l13)
            Nb[8] = ( (-1) * f4 - Nb[9] + (Nb[12] * (l8 - l10) / l13) - (Nb[10] * l10 / l11)) * l9 / l10
            Fc = ((Nb[6] * l8 / l7) + Nb[7] + (Nb[8] * l8 / l9))

        # F > H && G > H
        if l6 > l8 and l10 > l8:
            Nb[11] = (f2 + (Nb[4] * (l6/l5 + ((l1*l6)/(l5*l2))))) * l12 / l8
            Nb[6] = (Nb[4] * l1/ l5 - (Nb[11] * l2 / l12)) * l7 / l2
            Nb[12] = Nb[11] * (l2/l12) * (l13/l3) 
            Nb[7] = (-1) * f3 + (Nb[12] * (l10-l8) / l13) + (Nb[11] * (l6 - l8) / l12)
            Nb[8] = ((-1) * f4 - (Nb[10] * l10 / l11) - (Nb[12] * (l10 - l8) / l13)) * l9 / l10
            Fc = ((Nb[6] * l6 / l7) + Nb[7] + (Nb[8] * l10 / l9)) 

        if l6 > l8 and l8 >= l10:
            xi = 180 - self.phi - self.psi # beta no papel da lilan
            #self.beta  = lambda no papel da lilian
            #self.gama = alfa no papael da lilian
            #self.lambida = teta1 no papael da lilian
            #self.psi - 1.54 = teta2 no papel da lilian / 1.54 = 90 graus em ras
            Nb[11] = (f2 + Nb[4]*(math.cos(self.beta) + (math.sin(self.beta) + math.cos(self.gama))/math.sin(self.gama)))/(-math.cos(self.gama + xi) + (math.sin(self.gama + xi)*math.cos(self.gama))/math.sin(self.gama))
            Nb[6] = -(Nb[11]*math.cos(self.gama + xi) + f2 + Nb[4]*math.cos(self.beta))/math.cos(self.gama)
            Nb[12] = Nb[11]*math.cos(self.psi - 1.54)/math.sin(self.lambida)
            Nb[7] = -f3 -Nb[12]*math.cos(self.psi - 1.54) + Nb*math.sin(self.psi - 1.54)
            Nb[8] = (-f4 - Nb[9] - (Nb[10]*l10/l11) - (Nb[12]*(l8-l10)/l13)) *l9/l10
            Fc = ((Nb[6] * l6 / l7) + Nb[7] + (Nb[8] * l10 / l9))

        if l10 > l8 and l8 >= l6:
            #0 = teta1 no papael da lilian
            #self.gama = TETA2 no papael da lilian
            #self.beta  = TETA3 no papel da lilian
            #self.lambida - 1.54 = TETA4 no papel da lilian / 1.54 = 90 graus em ras
            Nb[12] = (Nb[5]*(math.sin(self.beta + math.cos(self.beta) * math.sin(self.gama) / math.cos(self.gama))) + f2*math.sin(self.gama)/math.cos(self.gama) + Nb[6] * math.sin(self.gama)/math.cos(self.gama)) / (math.cos(0) + math.sin(0).math.tan(self.gama))
            Nb[7] = (Nb[5] * math.sin(self.beta) - Nb[12]*math.cos(0))/math.sin(self.gama)
            Nb[13] = Nb[12]*(l2/l12)/math.cos(self.lambida - 1.54) 
            Nb[8] = -f3 + Nb[13]*math.sin(self.lambida - 1.54) - Nb[12]*(l8-l6)/l12
            Nb[9] = (-f4 - Nb[10] - Nb[13] * (l10-l8)/l13 - Nb[11]*l10/l11)*(l9/l10)
            Fc = ((Nb[6] * l8 / l7) + Nb[7] + (Nb[8] * l8 / l9))


        #calculando as forças virtuais
        Nv = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        for i in range (0, 13):
            Nv[i] = Nb[i] * (1/Fc)
        
        for c in range (0, 13):
            print(f'Força normal na barra {c+1}= {Nb[c]};')
            print(f'Força virtual na barra {c+1}= {Nv[c]};')

    def calcular_angulo_entre_barras(self, barra1, barra2):
        vetor1 = barra1.vetor()
        vetor2 = barra2.vetor()
        l1 = self.comprimentos[0]
        l2 = self.comprimentos[1]
        l3 = self.comprimentos[2]
        l4 = self.comprimentos[3]
        l5 = self.comprimentos_diagonais[0]
        l6 = self.comprimentos[4]
        l7 = self.comprimentos_diagonais[1]
        l8 = self.comprimentos[5]
        l9 = self.comprimentos_diagonais[2]
        l10 = self.comprimentos[6]
        l11 = self.comprimentos_diagonais[3]
        l12 = self.comprimentos_diagonais[4]
        l13 = self.comprimentos_diagonais[5]
        
        # F > H = G
        if l6 > l10 == l8:
            if barra1.name == "5" and barra2.name == "6":
                vetor1 *= -1
            if barra1.name == "12" and barra2.name == "8":
                vetor1 *= -1  
            if barra1.name == "8" and barra2.name == "9":
                vetor1 *= -1
            if barra1.name == "10" and barra2.name == "9":
                vetor2 *= -1

        # F = H = G
        if l10 == l6 == l8:
            if barra1.name == "5" and barra2.name == "6":
                vetor2 *= -1
            if barra1.name == "8" and barra2.name == "9":
                vetor1 *= -1
            if barra1.name == "10" and barra2.name == "9":
                vetor2 *= -1
 
        # F = H < G
        if  l6 == l8 < l10 :
            if barra1.name == "5" and barra2.name == "6":
                vetor2 *= -1
            if barra1.name == "8" and barra2.name == "9":
                vetor2 *= -1
            if barra1.name == "10" and barra2.name == "9":
                vetor2 *= -1

        # F < H = G
        if l10 == l8 > l6:
            if barra1.name == "5" and barra2.name == "6":
                vetor2 *= -1
            if barra1.name == "12" and barra2.name == "8":
                vetor2 *= -1
            if barra1.name == "8" and barra2.name == "9":
                vetor2 *= -1
            if barra1.name == "10" and barra2.name == "9":
                vetor2 *= -1

        # F = H > G
        if l6 == l8 > l10:
            if barra1.name == "5" and barra2.name == "6":
                vetor1 *= -1

            if barra1.name == "8" and barra2.name == "9":
                vetor1 *= -1 

            if barra1.name == "11" and barra2.name == "4":
                vetor1 *= -1 
                vetor2 *= -1 

            if barra1.name == "10" and barra2.name == "9":
                vetor2 *= -1 

        # H > F & H > G
        if l8 > l6 and  l8 > l10:
            if barra1.name == "5" and barra2.name == "6":
                vetor1 *= -1
            if barra1.name == "12" and barra2.name == "8":
                vetor1 *= -1  
            if barra1.name == "8" and barra2.name == "9":
                vetor1 *= -1
            if barra1.name == "10" and barra2.name == "9":
                vetor2 *= -1

        # H < F && H < G
        if l8 < l6 and  l8 < l10:
            if barra1.name == "5" and barra2.name == "6":
                vetor1 *= -1

            if barra1.name == "2" and barra2.name == "7":
                vetor1 *= -1
                vetor2 *= -1
            if barra1.name == "7" and barra2.name == "8":
                vetor1 *= -1
                vetor2 *= -1

            if barra1.name == "8" and barra2.name == "9":
                vetor1 *= -1
                vetor2 += -1
            
            if barra1.name == "10" and barra2.name == "9":
                vetor2 *= -1

            if barra1.name == "12" and barra2.name == "8":
                vetor1 *= -1  
            
        produto_escalar = np.dot(vetor1, vetor2)
        magnitude1 = np.linalg.norm(vetor1)
        magnitude2 = np.linalg.norm(vetor2)
        cos_theta = produto_escalar / (magnitude1 * magnitude2)
        angulo = np.arccos(cos_theta)
        return angulo

    def encontrar_barra(self, name):
        for barra in self.barras:
            if barra.name == name:
                return barra

    def calcular_angulos(self):
        print("oidaodijawodijoaijdoiajdoia\n\n\n\n\n")

        self.alfa = trelica.calcular_angulo_entre_barras(self.encontrar_barra("1"), self.encontrar_barra("b"))
        # print(f'O angulo entre as barras b1 e b5 (alfa) é {alfa:.2f} radianos, {np.degrees(alfa):.2f} graus')

        self.gama = trelica.calcular_angulo_entre_barras(self.encontrar_barra("6"), self.encontrar_barra("7"))
        # print(f'O angulo entre as barras b6 e b7 (gama) é {gama:.2f} radianos, {np.degrees(gama):.2f} graus')

        self.beta = trelica.calcular_angulo_entre_barras(self.encontrar_barra("5"), self.encontrar_barra("6"))
        # print(f'O angulo entre as barras b5 e b6 (beta) é {beta:.2f} radianos, {np.degrees(beta):.2f} graus')

        ##

        self.lambida = trelica.calcular_angulo_entre_barras(self.encontrar_barra("13"), self.encontrar_barra("8"))
        # print(f'O angulo entre as barras b13 e b8 (lambda) é {lambida:.2f} radianos, {np.degrees(lambida):.2f} graus')

        self.psi = trelica.calcular_angulo_entre_barras(self.encontrar_barra("12"), self.encontrar_barra("8"))
        # print(f'O angulo entre as barras b12 e b8 (psi) é {psi:.2f} radianos, {np.degrees(psi):.2f} graus')

        ##

        self.omega = trelica.calcular_angulo_entre_barras(self.encontrar_barra("2"), self.encontrar_barra("7"))
        # print(f'O angulo entre as barras b2 e b7 (omega) é {omega:.2f} radianos, {np.degrees(omega):.2f} graus')

        self.phi = trelica.calcular_angulo_entre_barras(self.encontrar_barra("7"), self.encontrar_barra("8"))
        # print(f'O angulo entre as barras b7 e b8 (phi) é {phi:.2f} radianos, {np.degrees(phi):.2f} graus')

        self.sigma = trelica.calcular_angulo_entre_barras(self.encontrar_barra("8"), self.encontrar_barra("9"))
        # print(f'O angulo entre as barras b8 e b9 (sigma) é {sigma:.2f} radianos, {np.degrees(sigma):.2f} graus')

        self.mi = trelica.calcular_angulo_entre_barras(self.encontrar_barra("9"), self.encontrar_barra("3"))
        # print(f'O angulo entre as barras b9 e b3 (mi) é {mi:.2f} radianos, {np.degrees(mi):.2f} graus')

        ##

        self.alfa2 = trelica.calcular_angulo_entre_barras(self.encontrar_barra("11"), self.encontrar_barra("4"))
        # print(f'O angulo entre as barras b11 e b4 (alfa2) é {alfa2:.2f} radianos, {np.degrees(alfa2):.2f} graus')

        self.gama2 = trelica.calcular_angulo_entre_barras(self.encontrar_barra("10"), self.encontrar_barra("9"))
        # print(f'O angulo entre as barras b10 e b9 (gama2) é {gama2:.2f} radianos, {np.degrees(gama2):.2f} graus')

        self.beta2 = trelica.calcular_angulo_entre_barras(self.encontrar_barra("10"), self.encontrar_barra("11"))
        # print(f'O angulo entre as barras b10 e b11  (beta)2 é {beta2:.2f} radianos, {np.degrees(beta2):.2f} graus')

        self.calcular_forcas_nas_barras()

    def forcas_virtuais_n():
        pass

    def calcular_massa_trelica(self):
        massa_especifica_aco = 7870 
        massa_total = 0

        comprimentos = (
            [self.comprimentos[0]] +
            [self.comprimentos[1]] +
            [self.comprimentos[2]] +
            [self.comprimentos[3]] +
            [self.comprimentos_diagonais[0]] +
            [self.comprimentos[4]] +
            [self.comprimentos_diagonais[1]] +
            [self.comprimentos[5]] +
            [self.comprimentos_diagonais[2]] +
            [self.comprimentos[6]] +
            self.comprimentos_diagonais[3:]
        )

        for area, comprimento in zip(self.areas, comprimentos):
            volume = area * comprimento  
            massa = volume * massa_especifica_aco  
            massa_total += massa

        return massa_total, comprimentos

    def calcular_deformacao_c(trelica):
        pass

def gerar_cromossomo():
    trelica = Trelica()
    trelica.gerar_comprimentos_nos_barras()
    return trelica

def gerar_populacao(tamanho_populacao):
    populacao = []
    for i in range(tamanho_populacao):
        populacao.append(gerar_cromossomo())
    return populacao

def avaliar(populacao):
    for trelica in populacao:
        '''trelica.m = calcular_massa_trelica(trelica)
        trelica.delta_c = calcular_deformacao_c(trelica)
        trelica.fitness = 1 / (0.1 * m + delta_c)'''
        trelica.calcular_angulos()
        trelica.fitness = random.choice([1,10,15,20,25,30,35,40])
    
def fazer_selecao(populacao):
    fit_total = sum(trelica.fitness for trelica in populacao)
    roleta = [(trelica.fitness / fit_total, trelica) for trelica in populacao]

    sorteado = random.random()
    part = 0
    for particao in roleta:
        part += particao[0]
        if sorteado <= part:
            return particao[1]

def selecao(populacao):
    pai1 = fazer_selecao(populacao)
    populacao_temp = [t for t in populacao if t != pai1]
    pai2 = fazer_selecao(populacao_temp)
    return pai1, pai2

def fazer_cruzamento(pai1_comprimentos, pai1_areas, pai2_comprimentos, pai2_areas):
    ponto_de_corte_comprimentos = random.randint(0, len(pai1_comprimentos) - 1)
    filho1_comprimentos = pai1_comprimentos[:ponto_de_corte_comprimentos] + pai2_comprimentos[ponto_de_corte_comprimentos:]
    filho2_comprimentos = pai2_comprimentos[:ponto_de_corte_comprimentos] + pai1_comprimentos[ponto_de_corte_comprimentos:]
    
    ponto_de_corte_areas = random.randint(0, len(pai1_areas) - 1)
    filho1_areas = pai1_areas[:ponto_de_corte_areas] + pai2_areas[ponto_de_corte_areas:]
    filho2_areas = pai2_areas[:ponto_de_corte_areas] + pai1_areas[ponto_de_corte_areas:]

    filho1 = Trelica().trelica_nova(filho1_comprimentos, filho1_areas)
    filho2 = Trelica().trelica_nova(filho2_comprimentos,filho2_areas)
    
    return filho1, filho2

def cruzamento(pai1, pai2, prob_cruzamento):
    sorteado = random.random()
    if sorteado <= prob_cruzamento:
        filho1, filho2 = fazer_cruzamento(pai1.comprimentos, pai1.areas, pai2.comprimentos, pai2.areas)
    else:
        filho1 = pai1
        filho2 = pai2
    return filho1, filho2 

def mutacao(filho, prob_mutacao):
    sorteado = random.random()
    if sorteado <= prob_mutacao:
        ponto_de_swap1 = random.randint(0, len(filho.comprimentos) - 1)
        ponto_de_swap2 = random.randint(0, len(filho.comprimentos) - 1)

        while ponto_de_swap1 == ponto_de_swap2:
            ponto_de_swap1 = random.randint(0, len(filho.comprimentos) - 1)
            ponto_de_swap2 = random.randint(0, len(filho.comprimentos) - 1)
            
        ponto_de_swap3 = random.randint(0, len(filho.areas) - 1)
        ponto_de_swap4 = random.randint(0, len(filho.areas) - 1)
        
        while ponto_de_swap3 == ponto_de_swap4:
            ponto_de_swap3 = random.randint(0, len(filho.areas) - 1)
            ponto_de_swap4 = random.randint(0, len(filho.areas) - 1)

        comprimentos = filho.comprimentos
        areas = filho.areas
        comprimentos[ponto_de_swap1], comprimentos[ponto_de_swap2] = comprimentos[ponto_de_swap2], comprimentos[ponto_de_swap1]
        areas[ponto_de_swap3], areas[ponto_de_swap4] = areas[ponto_de_swap4], areas[ponto_de_swap3]

        filho = Trelica().trelica_nova(comprimentos, areas)

    return filho

def selecionar_melhores(n, filhos_mutacoes):
    return sorted(filhos_mutacoes, key = lambda x: x.fitness, reverse=False)[n:]

def elitismo(n, populacao, filhos_mutacoes):
    return sorted(populacao, key = lambda x: x.fitness, reverse=True)[:n] + selecionar_melhores(n, filhos_mutacoes)

def algoritmo_genetico(tamanho_populacao, numero_geracoes,prob_cruzamento, prob_mutacao, tem_elitismo, n_elitismo):
    populacoes = []
    filhos = []
    filhos_mutacao = []
    populacao_nova = []

    populacao = gerar_populacao(tamanho_populacao)  
    populacoes.append(populacao)
    avaliar(populacao)
    while numero_geracoes > 1:
        while len(filhos) < tamanho_populacao:
            pai1, pai2 = selecao(populacao)
            filho1, filho2 = cruzamento(pai1, pai2, prob_cruzamento)
            filhos.append(filho1)
            filhos.append(filho2)
        for filho in filhos:
            filho_mutacao = mutacao(filho, prob_mutacao)
            filhos_mutacao.append(filho_mutacao)
        if tem_elitismo:
            populacao_nova = elitismo(n_elitismo, populacao, filhos_mutacao) 
        else:
            populacao_nova = filhos_mutacao
        
        avaliar(populacao_nova)
        
        populacoes.append(populacao_nova)
        populacao = copy.deepcopy(populacao_nova)
        populacao_nova = []  
        filhos = []
        filhos_mutacao = []
        numero_geracoes-=1
    return populacoes

if __name__== "__main__":

    """populacoes = algoritmo_genetico(tamanho_populacao = 6, numero_geracoes = 2, prob_cruzamento = 0.8, prob_mutacao = 0.05, tem_elitismo = True, n_elitismo = 2)

    for populacao in populacoes:
        print("==============================POPULACAO ")
        for trelica in populacao:
            print("=======trelica======")
            print(f" comprimentos: {trelica.comprimentos} diagonais: {trelica.comprimentos_diagonais} areas: {trelica.areas} fitness: {trelica.fitness} ")"""
    
    trelica = Trelica()
    trelica.gerar_comprimentos_nos_barras()
    print(f" comprimentos: {trelica.comprimentos} diagonais: {trelica.comprimentos_diagonais} areas: {trelica.areas} fitness: {trelica.fitness} ")
    m, comprimentos = trelica.calcular_massa_trelica()
    print(m)
    print(comprimentos)