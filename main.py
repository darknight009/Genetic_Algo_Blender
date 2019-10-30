import bpy
import mathutils
import random
import pdb
import math 

done=[]
class puck():
    def __init__(self, target, i, gen):
        bpy.ops.mesh.primitive_cube_add()
        self.value = bpy.context.selected_objects[0]
        self.value.name = "Cube"+str(i)+"_"+str(gen)
        self.value.location = mathutils.Vector((0, 0, 0.5))
        self.value.scale = (1, 1, 0.5)
        self.target = target
        self.fitness = 0
        self.frames = 0
        self.path=[]
        self.error=0
        
    def move(self, disp):
        self.frames+=10
        self.value.location += mathutils.Vector(disp)
        if(self.value.location[1])>16:
            self.value.location-=mathutils.Vector((0,1,0))
        if(self.value.location[1])<-16:
            self.value.location-=mathutils.Vector((0,-1,0))
        if(self.value.location[0])<-16:
            self.value.location-=mathutils.Vector((-1,0,0))
        if(self.value.location[0])>16:
            self.value.location-=mathutils.Vector((1,0,0))       
        self.value.keyframe_insert(data_path='location', frame=self.frames)

    def dist(self, v1, v2):
        d = (v1-v2).dot(v1-v2)
        return abs(d)

    def fit(self):
        err = self.dist(self.value.location, self.target)
        self.error = err
        self.fitness = int(((16**2-err)/16**2)*100)
        if self.fitness<=0:
            self.fitness = 1
        return self.fitness

class Population(): 
    def __init__(self, PopSize, target):
        self.size = PopSize
        self.target = target
        self.value = self.create()

    def create(self):
        pop = []
        for i in range(self.size):
            ball = puck(self.target, i, -1)
            pop.append(ball)
        return pop

def calcFitness(population):
    for ball in population.value:
        ball.fit()

def createPop(popSize, target):
    population = Population(popSize, target)
    bpy.ops.rigidbody.objects_add(type='ACTIVE')
    return population

def clean():
    for i in range(50):
        objs=bpy.data.objects
        objs.remove(objs["Cube"+str(i)+"_16"], True)

def randMove(pop):
    mvs=[]
    for i in range(-1,2):
        for j in range(-1,2):
                t = (i,j,0)
                if t not in mvs:
                    mvs.append(t)
    for p in pop.value:
        path=[]
        for m in range(16):
            r=random.choice(mvs)
            path.append(r)
            p.move(r)
        p.path=path

def mutate(dna):
    mvs=[]
    for i in range(-1,2):
        for j in range(-1,2):
                t = (i,j,0)
                if t not in mvs:
                    mvs.append(t)
                    
    if random.random() <= 0.1:
        dna.path[random.randint(0, 15)] = random.choice(mvs)
    return dna        

def reproduce(population, gen):
    mating_pool = []
    for dna in population.value:
        for i in range(dna.fitness):
            mating_pool.append(dna)
    
    l = len(mating_pool)
    for i in range(population.size):
        A = random.randint(0, l-1)
        B = random.randint(0, l-1)
        parentA = mating_pool[A]
        parentB = mating_pool[B]
        
        while parentA.path == parentB.path:
            B -= 1
            B %= l
            parentB = mating_pool[B]
        
        mid = random.randint(0, 15)
        child = puck(parentA.target, i, gen)
        child.path = parentA.path[:mid] + parentB.path[mid:]
        child = mutate(child)
        population.value[i] = child
        bpy.data.objects.remove(bpy.data.objects["Cube"+str(i)+"_"+str(gen-1)], True)
    return population

def moveNew(population):
    print("Moving")
    for dna in population.value:
        for m in dna.path:
            dna.move(m)
    
def main():
    popSize = 10
    mutation = 0.1
    target = mathutils.Vector((0, -16, 0.5))
    population = createPop(popSize, target)
    f=0
    for i in range(16):
        randMove(population)
    for i in range(1000):
        print("gen = ", i)
        bpy.data.scenes["Scene"].render.filepath = "/tmp/generation_" + str(i) + ".mpeg"
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = 160
        bpy.ops.render.render(animation=True, use_viewport=True)
        calcFitness(population)
        population = reproduce(population, i)
        print("Reproduced")
        moveNew(population)
        print("Moved")
        calcFitness(population)
        for dna in population.value:
            print(dna.error, dna.fitness, dna.value.name)
            if dna.fitness>=100:
                print("Complete")
                f=1
                break
        if f==1:
            break
        

if __name__ == '__main__':
    main()
    #clean()