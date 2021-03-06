from math import *
from visual import *
import argparse
import csv
import string
import time

G = 6.0673e-41
meter_scale = 1.03227e10
dt = 3.15569e3
kerbal_year = 9.2077e6
kerbol_rad = 2.616e8
radius_scale = 10.0

class Quad:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.bodies = None

    def contains(Px, Py):
        if (Px < x + size) and (Px >= x):
            if (Py < y + size) and (Py >= y):
                return True
        return False

    def add_body(self):
        if not self.bodies:
            self.bodies

    def NW():
        return Quad(x,y,size/2)

    def NE():
        return Quad(x+size/2,y,size/2)

    def SW():
        return Quad(x,y+size/2,size/2)

    def SE():
        return Quad(x+size/2,y+size/2,size/2)

class Body:
    def __init__(self, r, v, mass, radius, color):
        self.r = r
        self.v = v
        self.a = vector(0,0,0)
        self.mass = mass 
        self.radius = radius
        self.color = color
        self.visual = sphere(pos = r, radius = self.radius, color = self.color)
        self.visual.trail = curve(color = self.color)

    def __repr__(self):
        return '%s,%s,%s,%s,%s' % (self.r, self.v, self.mass, self.radius, self.color)

    def update(self, dt):
        self.v = self.v + dt * self.a
        self.r = self.r + dt * self.v
        if vis_mode:
            self.visual.pos = self.r
            self.visual.trail.append(pos=self.r, retain=400)
        self.a = vector(0,0,0)

class BarnesHutNode:
    def __init__(self, quad):
        self.quad = quad
        self.body = None
        self.NW = None
        self.NE = None
        self.SW = None
        self.SE = None

    def external(node):
        if (node.NW or node.NE or node.SW or node.SE):
            return False
        return True

    def insert(new_body): # finish
        if not self.body:
            self.body = new_body

        elif (not self.external(self)):
            self.body = None

def main(loadfile):
    if not loadfile:
        loadfile = 'start.csv'
    time_elapsed, bodies, init_angl_mom = init(loadfile)
    save(time_elapsed,bodies)

    cycles = 1
    while(True):
        rate(500)
        if scene.kb.keys:
            if scene.kb.getkey() == 'q':
                print "saving!"
                save(time_elapsed,bodies)
        for i in bodies:
            for j in bodies:
                if j != i:
                    if mag(i.r - j.r) <(i.radius + j.radius):
                        print "collision! all bets are off"
                    else:
                        i.a = i.a + newton_grav(i,j)/i.mass
            i.update(dt)
        time_elapsed = time_elapsed + dt
        if time_elapsed > kerbal_year * cycles:
            cycles = cycles + 1
            print time_elapsed/kerbal_year, ' ', sum_momentum(bodies)/init_angl_mom - 1
        scene.center = bodies[0].visual.pos    

'''Hard Coded Init, Outdated, Now Starts from start.csv
def init_old(bodies):
    Kerbol = Body(vector(0.0,0.0,0.0),vector(0.0,0.0,0.0),1.756e28,2.616e8, color.red)
    Moho = Body(vector(6.31576e9,0.0,0.0),vector(0.0,12186.0,0.0),2.526e21,2.5e5, color.gray(0.5))
    Eve = Body(vector(9.931e9,0.0,0.0),vector(0.0,10811.0,0.0),1.2233e23,7e5, (0.5,0.0,1.0))
    Kerbin = Body(vector(1.3599e10,0.0,0.0),vector(0.0,9284.5,0.0),5.292e22,6.00e5, color.blue)
    Duna = Body(vector(2.17832e10,0.0,0.0),vector(0.0,7147.0,0.0),4.5154e21,3.20e5, (0.4,0.0,0.0))
    Dres = Body(vector(-4.67610e10,0.0,0.0),vector(0.0,-4630.0,0.0),3.2191e20,1.38e5, color.gray(0.7))
    Jool = Body(vector(7.22122e10,0.0,0.0),vector(0.0,3927.0,0.0),4.2333e24,6.0e6, color.green)
    Eeloo = Body(vector(-1.13549e11,0.0,0.0),vector(0.0,-2764.0,0.0),1.1149358e21,2.1e5, color.white)
    bodies.append(Kerbol)
    bodies.append(Moho)
    bodies.append(Eve)
    bodies.append(Kerbin)
    bodies.append(Duna)
    bodies.append(Dres)
    bodies.append(Jool)
    bodies.append(Eeloo)
    if vis_mode:
        scene.center = Kerbol.visual.pos
    return sum_momentum(bodies)
'''

def init(save_file):
    time, saved_bodies = load(save_file)
    return time, saved_bodies, sum_momentum(saved_bodies)

def newton_grav(body, ext):
    r = body.r - ext.r
    r_mag = mag(r)
    r_norm = norm(r)
    return (-G*ext.mass*body.mass/(r_mag**2)) * r_norm

def sum_momentum(bodies):
    sum = 0
    for i in bodies:
        sum = sum + i.mass * mag(i.v) * mag(i.r) * sin(diff_angle(i.r,i.v))
    return sum

def save(time,bodies):
    with open('save.csv', 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerow([time])
        a.writerow(bodies)

def load(file):
    data = []
    ret_bods = []
    with open(file, 'r') as fp:
        a = csv.reader(fp, delimiter=',')
        for row in a:
            data.append(row)
    time = float(data[0][0])
    identity = string.maketrans("","")
    load_bods = [s.translate(identity, "<>()") for s in data[1]]
    for b in load_bods:
        b = b.split(',')
        b = [s.translate(identity, " ") for s in b]
        b = map(float,b)
        ret_bods.append(Body(vector(b[0],b[1],b[2]),vector(b[3],b[4],b[5]),b[6],b[7],(b[8],b[9],b[10])))
    return time, ret_bods

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v','--visual', action='store_true', required=False)
    parser.add_argument('-l','--load', dest='load', required=False)
    args = parser.parse_args()
    if args.visual:
        vis_mode = True
    else:
        vis_mode = False

    if vis_mode:
        scene.width = 800
        scene.height = 800
        scene.title = 'KSP Small-N'
        scene.autoscale = False
        scene.fullscreen = False
    else:
        scene.visible = False

    main(args.load)