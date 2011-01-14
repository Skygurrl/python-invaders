#!/usr/bin/env python

# 2007-04-07 - Pablo Carballo - pablodcar@gmail.com

from Tkinter import *
import imagenes, random

objetos = {} #mapea el Id del canvas con el objeto

def t2photo(t): #devuelve (Tk.PhotoImage, alto, ancho)
    photo = PhotoImage()
    put = " ".join(['{%s}' % " ".join([t[0][c] for c in r]) for r in t[1]])
    photo.put(put)
    return (photo, len(t[1]), len(t[1][0]))

def iniciarsprite(obj, x, y, canvas, imagen):
    obj.c, obj.imagen = canvas, imagen
    img = Global.imagenes[imagen]
    obj.photo = img[0].copy()
    obj.height, obj.width = img[1], img[2]
    obj.id = canvas.create_image(x, y, image=obj.photo, tags=obj.__class__.nombre)
    objetos[obj.id] = obj

def chimg(obj, imagen):
    obj.imagen, img = imagen, Global.imagenes[imagen]
    obj.photo = img[0].copy()
    obj.height, obj.width = img[1], img[2]
    obj.c.itemconfigure(obj.id, image=obj.photo)

def limpiar(obj):
    obj.c.delete(obj.id)
    del objetos[obj.id]
    del obj

def seqcalls(*calls): #llamadas secuenciales: ((milisegudos1, func1), (ms2, func2), ...,(msN, funcN))
    milis = 0
    for ms, func in calls:
        milis += ms
        Global.c.after(milis, func)        

class AutoMov(object): 
    def __init__(self, x, y, canvas, imagen, mov, frec):       
        self.mov, self.frec = mov, frec
        iniciarsprite(self, x, y, canvas, imagen)
        self.movid = self.c.after(self.frec, self.desplazar)
     
    def desplazar(self):
        self.c.move(self.id,self.mov[0], self.mov[1])
        x0, y0 = self.c.coords(self.id)
        ids = list(self.c.find_overlapping(x0, y0, x0+self.width, y0+self.height))
        if len(ids) > 1:
            ids.remove(self.id)
            if objetos.has_key(ids[0]): 
                objetos[ids[0]].destruir()
            self.destruir()
        elif y0 - self.height <= 0 or y0 > Global.alto or x0 + self.width < 0 or x0 > Global.ancho:
            self.limpiar()
        else:
            self.movid = self.c.after(self.frec, self.desplazar) 

    def destruir(self): self.limpiar()

    def limpiar(self):
        self.c.after_cancel(self.movid)
        limpiar(self)

    def puntos(self): return 0

class Misil(AutoMov): #Misil del jugador
    nombre = "misil" 

class Misile(AutoMov): #Misil de enemigos
    nombre = "misile" 

class Platillo(AutoMov): 
    nombre = 'platillo'
    puntos = (50, 100, 150, 300)
 
    def destruir(self):
        self.c.after_cancel(self.movid)
        chimg(self, 'platilloexplo')
        seqcalls((500, self.destruir2), (500, self.destruir3))
         
    def destruir2(self):
        chimg(self, 'puntonegro')
        points = self.puntos[random.randint(0,len(Platillo.puntos)-1)]
        Global.puntaje.sumar(points)
        x0, y0 = self.c.coords(self.id)
        self.exploid = self.c.create_text(x0, y0, fill='#F81818', text=points)

    def destruir3(self):
        self.c.delete(self.exploid)
        limpiar(self)
 
class Nave(object):
    movx, movy, frec = 5, 10, 500
    dirx, diry = 1, 0
    nombre = 'nave'
    cant = 0 
    movs = {40: 6, 30: 7, 20: 8, 10: 9, 3: 10}
    puntos = (40, 20, 20, 10, 10)
    def __init__(self, x, y, canvas, images):
        self.images = images
        iniciarsprite(self, x, y, canvas, images[0])
        Nave.cant += 1
        
    def cambimg(self):
        if self.imagen == self.images[0]: chimg(self, self.images[1]) 
        elif self.imagen == self.images[1]: chimg(self, self.images[0])

    def destruir(self):        
        Nave.cant -= 1
        chimg(self, 'explo')
        Global.puntaje.sumar(self.puntos[self.pos[1]])
        self.c.after(200, self.destruir2)

    def destruir2(self):
        if Nave.cant == 0:
            self.c.create_text(Global.ancho/2, Global.alto/2, text='Ganaste', fill='white')
        if Nave.cant in Nave.movs.iterkeys(): 
            Nave.movx = Nave.movs[Nave.cant]
            Nave.frec -= 80
        limpiar(self)

    def disparar(self):
        x, y = self.c.coords(self.id)
        Misile(x, y+20, self.c, 'misil', (0,6), 20)
        
class Canion(object):
    mov, frec = 5, 30
    nombre = 'canion'
    def __init__(self, canvas, imagen):
        self.x, self.y = Global.ancho/2, Global.alto-40
        iniciarsprite(self, self.x, self.y, canvas, imagen)
        self.dir = 0       
        self.c.after(Canion.frec, self.desplazar) 

    def desplazar(self):
        if self.dir != 0:
            self.c.move(Canion.nombre, Canion.mov*self.dir, 0)
        x, y = self.c.coords(self.id)
        self.movid = self.c.after(Canion.frec, self.desplazar)

    def destruir(self):        
        self.c.unbind_all('<KeyPress>')
        self.c.unbind_all('<KeyRelease>')
        self.c.create_text(Global.ancho/2, Global.alto/2, text='Alpiste perdiste', fill='white')
        self.c.after_cancel(self.movid)
        limpiar(self)        

class Puntaje(object):
    nombre = 'puntaje'
    leyenda = 'Score: %d'
    def __init__(self, canvas):
        self.c = canvas
        self.puntos = 0
        self.id = canvas.create_text(20, 20, anchor=NW, fill='#33FF00', text=Puntaje.leyenda % self.puntos)
    def sumar(self, cant):
        self.puntos += cant
        self.c.itemconfigure(self.id, text=Puntaje.leyenda % self.puntos)

class Escudo(object):
    nombre = 'escudo'
    def __init__(self, x, y, canvas, imagen):
        iniciarsprite(self, x, y, canvas, imagen)
        self.estado = 3

    def destruir(self):
        self.estado -= 1
        if self.estado == 0:
            limpiar(self)
        else:
            self.romper()

    def romper(self):
        put, raw = '', ''
        lraw = []
        for r in self.crudo[1]:
            put += '{'            
            for p in r:
                if random.randint(0,1) == 0:
                    put += ' #000000 '
                    raw += ' '
                else:
                    put += ' %s ' % self.crudo[0][p]
                    raw += p
            put += '} '
            lraw.append(raw)
            raw = ''
        self.crudo = (self.crudo[0], tuple(lraw))
        self.photo.put(put)

class Global(object):
    ancho, alto = 640, 480
    maxcantmis = 1 #Maxima cantidad de misiles simultaneos
    def __init__(self, master):
        display = Frame(master)
        Global.imagenes = {} 

        for img in [i for i in dir(imagenes) if not i.startswith("__")]:
            Global.imagenes[img] = t2photo(getattr(imagenes, img))
        
        c = Canvas(display, background='#000000', width=Global.ancho, height=Global.alto)
        self.canion = Canion(c, 'canion')
        c.bind_all('<KeyPress>', self.keypress)
        c.bind_all('<KeyRelease>', self.keyrelease)
        self.c = c
        Global.c = c
        c.grid()
        display.grid()
        Global.puntaje = Puntaje(self.c)
        self.crearnaves()
        self.crearescudos()
        self.c.after(random.randint(15000, 30000), self.crearplatillo)
	self.c.postscript(file="/home/pablo/codigo/spaceinv/mispace.ps",height=480, width=640, colormode="color")

    def keypress(self, e):
        if e.keysym == 'Left':
            self.canion.dir = -1   
        elif e.keysym == 'Right':
            self.canion.dir = 1
        elif e.keysym == 'z' or e.keysym == 'Z':
            self.disp()            

    def keyrelease(self, e):
        if e.keysym == 'Left' and self.canion.dir == -1 or e.keysym == 'Right' and self.canion.dir == 1:
            self.canion.dir = 0

    def disp(self):
        x0, y0 = self.c.coords(Canion.nombre)
        if len(self.c.find_withtag(Misil.nombre)) < Global.maxcantmis:
            Misil(x0, y0-20, self.c, 'misil', (0, -8), 20)

    def crearescudos(self):
        x, y = Global.ancho/5, Global.alto -100
        for i in xrange(4):
            self.crearescudo(x + (Global.ancho/5) * i, y)

    def crearescudo(self, x, y):
        images = ((('escudo1', imagenes.escudo1), ('escudo2', imagenes.escudo2), ('escudo3', imagenes.escudo3)), 
                  (('escudo2', imagenes.escudo2), ('escudo2', imagenes.escudo2), ('escudo2', imagenes.escudo2)), 
                  (('escudo4', imagenes.escudo4), '', ('escudo5', imagenes.escudo5)))
        for i in images:
            x1 = x           
            for j in i:
                if j != '':
                    e = Escudo(x1, y, self.c, j[0])
                    e.crudo = j[1]
                x1 += e.width
            y += e.height

    def crearnaves(self):
        x, y = 100, 80
        filas = (('nave11', 'nave12'), ('nave21', 'nave22'), 
         ('nave21', 'nave22'), ('nave31', 'nave32'), ('nave31', 'nave32'))
        for j in xrange(5):
            for i in xrange(11):
                n = Nave(x, y, self.c, filas[j])
                n.pos = (i, j)
                x += 40
            y += 40
            x = 100    
        self.c.after(Nave.frec, self.movernaves)
        self.c.after(1500, self.atacar)

    def movernaves(self):
        if Nave.cant == 0: return None
        x0, y0, x1, y1 = self.c.bbox(Nave.nombre)
        if x0 <= 5: 
            Nave.dirx, Nave.diry = 1, 1
        elif x1 >= Global.ancho - 5:
            Nave.dirx, Nave.diry = -1, 1
        else:
            Nave.diry = 0

        self.c.move(Nave.nombre, Nave.dirx*Nave.movx, Nave.diry*Nave.movy)
        for n in [a for a in objetos.itervalues() if type(a) == Nave]:
            n.cambimg()
        if y1 >= self.canion.y: 
            self.canion.destruir()
        else:
            self.c.after(Nave.frec, self.movernaves)    

    def atacar(self):
        atacante = {} 
        for nave in [o for o in objetos.itervalues() if type(o) == Nave]:
            if not atacante.has_key(nave.pos[0]):
                atacante[nave.pos[0]] = nave
            elif nave.pos[1] > atacante[nave.pos[0]].pos[1]:
                atacante[nave.pos[0]] = nave
        if len(atacante) > 0:
            pos = random.choice(atacante.keys())
            atacante[pos].disparar()
            self.c.after(random.randint(700, 1500), self.atacar)

    def crearplatillo(self):
        if random.randint(0,1) == 1:
            Platillo(4, 40, self.c, 'platillo', (4, 0), 30)
        else: 
            Platillo(Global.ancho-4, 40, self.c, 'platillo', (-4, 0), 30)
        self.c.after(random.randint(15000, 30000), self.crearplatillo)

if __name__ == '__main__':
    root = Tk()
    Global(root)
    root.mainloop()
