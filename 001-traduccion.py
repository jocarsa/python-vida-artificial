import cv2
import numpy as np
import random
import math

# Video properties
width, height = 1920, 1080
fps = 60
duration = 60  # seconds
output_file = "simulation_video.mp4"

# Number of frames
total_frames = fps * duration

# Entity classes
class Entidad:
    def __init__(self):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)

class Comida(Entidad):
    def dibuja(self, frame):
        cv2.circle(frame, (int(self.x), int(self.y)), 2, (0, 0, 255), -1)

class Hogar(Entidad):
    def dibuja(self, frame):
        cv2.circle(frame, (int(self.x), int(self.y)), 2, (255, 0, 0), -1)

class Persona(Entidad):
    def __init__(self, miva):
        super().__init__()
        self.a = random.uniform(0, np.pi * 2)
        self.r = random.randint(0, 255)
        self.g = random.randint(0, 255)
        self.b = random.randint(0, 255)
        self.e = random.uniform(0, 100)  # Energy
        self.d = random.uniform(-0.05, 0.05)
        self.s = random.uniform(0, 100)  # Sleepiness
        self.va = miva
        self.edad = 0  # Age
        self.reproducido = False

    def vive(self, frame, comidas, hogares, personas):
        if self.s > 80:
            self.busca_hogar(hogares)
            self.mueve()
        else:
            if self.e > 10:
                if 20 < self.edad < 50:
                    self.busca_pareja(personas)
                    self.mueve()
                else:
                    self.d += self.va
                    self.a += self.d  
                    self.mueve()
            else:
                self.busca_comida(comidas)
                self.mueve()
        
        self.edad += 0.1
        self.dibuja(frame)

    def mueve(self):
        self.x += math.cos(self.a)
        self.y += math.sin(self.a)
        self.e -= 0.1
        self.s += 0.1
        self.rebote_pared()

    def dibuja(self, frame):
        cv2.rectangle(frame, (int(self.x), int(self.y)), (int(self.x) + 2, int(self.y) + 2), (self.b, self.g, self.r), -1)

    def busca_comida(self, comidas):
        mejor_candidato = min(comidas, key=lambda c: calcula_distancia(self.x, self.y, c.x, c.y))
        self.a = angulo_entre_dos_puntos(self.x, self.y, mejor_candidato.x, mejor_candidato.y)
        if calcula_distancia(self.x, self.y, mejor_candidato.x, mejor_candidato.y) < 10:
            self.come()

    def busca_pareja(self, personas):
        if personas:
            pareja = random.choice(personas)
            self.a = angulo_entre_dos_puntos(self.x, self.y, pareja.x, pareja.y)
            if calcula_distancia(self.x, self.y, pareja.x, pareja.y) < 10 and not self.reproducido:
                self.reproduce(personas, pareja)

    def reproduce(self, personas, pareja):
        self.reproducido = True
        pareja.reproducido = True
        for _ in range(2):
            personas.append(Persona(self.va))

    def busca_hogar(self, hogares):
        mejor_candidato = min(hogares, key=lambda h: calcula_distancia(self.x, self.y, h.x, h.y))
        self.a = angulo_entre_dos_puntos(self.x, self.y, mejor_candidato.x, mejor_candidato.y)
        if calcula_distancia(self.x, self.y, mejor_candidato.x, mejor_candidato.y) < 10:
            self.duerme()

    def come(self):
        self.e = 100

    def duerme(self):
        self.s = 0

    def rebote_pared(self):
        if self.y < 0 or self.y > height:
            self.a = -self.a
        if self.x < 0 or self.x > width:
            self.a = np.pi - self.a

    # Added methods
    def getEnergia(self):
        return self.e

    def getEdad(self):
        return self.edad

def calcula_distancia(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def angulo_entre_dos_puntos(x1, y1, x2, y2):
    return np.arctan2(y2 - y1, x2 - x1)

# Create instances
personas = [Persona((random.uniform(-0.5, 0.5) / 40)) for _ in range(10)]
comidas = [Comida() for _ in range(55)]
hogares = [Hogar() for _ in range(55)]

# Video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

# Main loop
for _ in range(total_frames):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Draw entities
    for comida in comidas:
        comida.dibuja(frame)
    
    for hogar in hogares:
        hogar.dibuja(frame)
    
    for persona in personas[:]:  # Copy to avoid mutation issues
        persona.vive(frame, comidas, hogares, personas)
        if persona.getEnergia() < 0 or persona.getEdad() > 100:
            personas.remove(persona)

    out.write(frame)

# Release video writer
out.release()
