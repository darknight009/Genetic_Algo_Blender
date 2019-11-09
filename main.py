import bpy
import mathutils
import random
import pdb
import math
import numpy as np
import copy


class puck():
    def __init__(self, target, i, gen):
        bpy.ops.mesh.primitive_cube_add()
        mat = bpy.data.materials.new("PKHG")
        mat.diffuse_color = tuple(np.random.randint(256, size=3))
        mat.diffuse_color = tuple(float(ti / 256) for ti in mat.diffuse_color)
        bpy.context.selected_objects[0].active_material = mat
        self.value = bpy.context.selected_objects[0]
        self.value.name = "Cube" + str(i) + "_" + str(gen)
        self.value.location = mathutils.Vector((0, 0, 0.5))
        self.value.scale = (1, 1, 0.5)
        self.target = target
        self.fitness = 0
        self.frames = 0
        self.path = []
        self.error = 0

    def move(self, disp):
        self.frames += 10
        self.value.location += mathutils.Vector(disp)
        if (self.value.location[1]) > 16:
            self.value.location -= mathutils.Vector((0, 1, 0))
        if (self.value.location[1]) < -16:
            self.value.location -= mathutils.Vector((0, -1, 0))
        if (self.value.location[0]) < -16:
            self.value.location -= mathutils.Vector((-1, 0, 0))
        if (self.value.location[0]) > 16:
            self.value.location -= mathutils.Vector((1, 0, 0))
        self.value.keyframe_insert(data_path='location', frame=self.frames)

    def dist(self, v1, v2):
        d = (v1 - v2).dot(v1 - v2)
        return abs(d)

    def fit(self):
        err = self.dist(self.value.location, self.target)
        self.error = err
        self.fitness = 256 - err
        if self.fitness <= 0:
            self.fitness = 0
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
        objs = bpy.data.objects
        objs.remove(objs["Cube" + str(i) + "_16"], True)


def randMove(pop):
    mvs = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            t = (i, j, 0)
            if t not in mvs:
                mvs.append(t)
    for p in pop.value:
        path = []
        for m in range(20):
            r = random.choice(mvs)
            path.append(r)
            p.move(r)
        p.path = path


def mutate(dna, rate):
    mvs = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            t = (i, j, 0)
            if t not in mvs:
                mvs.append(t)

    if random.random() <= rate:
        dna.path[random.randint(0, 19)] = random.choice(mvs)
    return dna


def reproduce(population, gen):
    rate = 0.2
    popfit = []
    for dna in population.value:
        popfit.append(dna.fitness)

    if len(set(popfit)) == 1:
        p = [0.1] * population.size
    else:
        stdev = np.std(popfit)
        mean = np.mean(popfit)
        popfit = [(x - mean) / stdev for x in popfit]
        mn = min(popfit)
        mx = max(popfit)
        rng = mx - mn
        popfit = [(x - mn) / rng for x in popfit]
        totwt = sum(popfit)
        p = [x / totwt for x in popfit]
    print(p)
    children = []
    print([x.value.name for x in population.value])
    print("+++++++++++++++++")
    for i in range(population.size):
        # print([x.value.name for x in population.value])
        A = np.random.choice(population.size, 1, replace=False, p=p)
        B = np.random.choice(population.size, 1, replace=False, p=p)
        parentA = population.value[A]
        parentB = population.value[B]

        # while parentA.path == parentB.path:
        #    B = random.randint(0, population.size-1)
        #    parentB = population.value[B]
        mid = 10
        print("Creating_" + parentA.value.name + "+" + parentB.value.name)
        child = puck(parentA.target, i, gen)
        child.path = parentA.path[:mid] + parentB.path[mid:]
        child = mutate(child, rate)
        children.append(child)
    for dna in population.value:
        bpy.data.objects.remove(bpy.data.objects[dna.value.name], True)
    population.value = children
    del popfit
    del p
    del children
    return population


def moveNew(population):
    print("Moving")
    for dna in population.value:
        for m in dna.path:
            dna.move(m)


def main():
    print("+++++++++++++++++++++++++++++++++++++++++++")
    popSize = 10
    mutation = 0.1
    target = mathutils.Vector((0, -16, 0.5))
    population = createPop(popSize, target)
    f = 0
    for i in range(20):
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
            if dna.value.location == target:
                print("Complete")
                f = 1
                break
        if f == 1:
            break


if __name__ == '__main__':
    main()
    # clean()