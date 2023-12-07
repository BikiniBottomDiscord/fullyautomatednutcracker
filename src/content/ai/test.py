import random
import typing
import time

p1 = set()
p2 = set()

guaranteed_numbers = 1000000
possible_numbers   = 1000000000

while len(p1) != guaranteed_numbers:
    p1.add(random.randint(0, possible_numbers))
while len(p2) != guaranteed_numbers:
    p2.add(random.randint(0, possible_numbers))


def std_intersect(s1: set, s2: set):
    return s1.intersection(s2)


def loop_intersect(s1: typing.Union[set, list], s2: typing.Union[set, list]):
    res = set()
    for i in s1:
        for j in s2:
            res.add(i) if i == j else None
    return res


def in_intersect(s1: typing.Union[set, list], s2: typing.Union[set, list]):
    res = set()
    for i in s1:
        res.add(i) if i in s2 else None
    return res


def generator_intersect(s1: set, s2: set):
    return {i for i in s1 if i in s2}


def perform_test(method, s1, s2):
    t1 = time.time()
    method(s1, s2)
    t2 = time.time()
    return t2 - t1

print(f'Set Intersection: {perform_test(std_intersect, p1, p2)}s')
print(f'Loop In Intersection: {perform_test(in_intersect, p1, p2)}s')
print(f'Generator Intersection: {perform_test(in_intersect, p1, p2)}s')
print(f'Double Loop Intersection: {perform_test(loop_intersect, p1, p2)}s')

