import sys

import numpy as np
import itertools
from copy import copy
from heapq import heappush, heappop
import cv2


class PriorityQueue:
    def __init__(self, iterable=[]):
        self.heap = []
        for value in iterable:
            heappush(self.heap, (0, value))

    def add(self, item):
        heappush(self.heap, item)

    def pop(self):
        item = heappop(self.heap)
        return item

    def print(self):
        for x in self.heap[:10]:
            print(x.water_state, x.heuristic, sep=" -> ", end=" | ")
        print()
        print()

    def __len__(self):
        return len(self.heap)


class State:
    def __init__(self, prev_state=None, water_state=None):
        if prev_state is not None:
            self.prev_state = prev_state.water_state
            self.prev_state_heuristic = prev_state.heuristic

        if water_state is None:
            raise ValueError("Invalid Water State")
        else:
            self.water_state = water_state

        if prev_state is None:
            self.action = 'add'
        else:
            if self.prev_state[-1] < self.water_state[-1]:
                self.action = 'target'
            elif sum(self.prev_state[1:-1]) == sum(self.water_state[1:-1]):
                self.action = 'transfer'
            elif sum(self.prev_state[1:-1]) < sum(self.water_state[1:-1]):
                self.action = 'add'

        if prev_state is None:
            self.heuristic = 0
            self.depth = 0
        else:
            self.depth = prev_state.depth + 1
            self.heuristic = self.get_heuristic()



    def get_heuristic(self):
        target = njugs.target
        current_final_ptcher = self.water_state[-1]
        prev_final_ptcher = self.prev_state[-1]
        remaining = target - self.water_state[-1]
        max_cap = njugs.max_capacities.copy()
        total_pitcher_capacity = sum(njugs.max_capacities[1:-1])
        num_j = len(self.water_state)

        # If water in all pitchers are full and target pitcher is greater than target, no solution can be reached
        if sum(self.water_state[1:]) > total_pitcher_capacity + target:
            return np.inf

        #if final state is reached
        if self.water_state[-1] == njugs.target:
            return -np.inf

        if self.water_state[-1] > njugs.target:
            return np.inf

        # If any pitcher contains the amount required to reach target, it is the penultimate state
        if remaining in self.water_state[1:-1]:
            return -np.inf
        else:
            if remaining < max_cap[-2]:
                return self.prev_state_heuristic+self.depth

            h0 = 0
            for i in range(num_j - 2, 0, -1):
                if remaining % max_cap[i] == 0:
                    if self.water_state[i] == max_cap[i] and self.prev_state == 0:
                        h0 += (remaining // max_cap[i]) * 2
                    elif self.water_state[i] == 0 and current_final_ptcher-prev_final_ptcher == max_cap[i]:
                        h0 += ((remaining // max_cap[i]) * 2)-1
                        break

            h = 0
            for i in range(num_j - 2, 0, -1):
                if remaining > max_cap[i] and self.water_state[i] == max_cap[i] and current_final_ptcher <= target:
                    h += ((remaining // max_cap[i]) * 2)
                    remaining = remaining % max_cap[i]
                    if current_final_ptcher > prev_final_ptcher:
                        h+=1


            return max(h0,h) + self.depth







    def get_string(self):
        x = []
        for t in self.water_state:
            if t == np.inf:
                x.append('inf')
            else:
                x.append(str(int(t)))
        return '_'.join(x)

    def __str__(self):
        return self.get_string()

    def __gt__(self, other):
        return self.heuristic > other.heuristic

    def __lt__(self, other):
        return self.heuristic < other.heuristic


class NJugs():
    def __init__(self, jug_capacities, target):
        self.NUM_JUGS = len(jug_capacities)
        self.max_capacities = [np.inf] + jug_capacities + [np.inf]
        self.target = target
        self.constraint = sum(jug_capacities) + target

        self.jugs = [np.inf] + [0] * (self.NUM_JUGS + 1)
        self.target_state = [-1] * (self.NUM_JUGS + 1) + [target]

        self.get_moves_list(self.jugs)

    def get_moves_list(self, state):
        self.moves_list = []
        ls = range(self.NUM_JUGS + 2)
        self.moves_list = [t for t in (itertools.product(ls, ls)) if t[0] != t[1]]

        ls = range(self.NUM_JUGS + 2)
        self.moves_list = self.moves_list + [(t, -1) for t in ls]

        self.moves_list.remove((0, -1))
        self.moves_list.remove((self.NUM_JUGS+1, -1))

        # infinity = source
        # cannot transfer from infinity to target
        self.moves_list.remove((0, self.NUM_JUGS + 1))

        # cannot transfer from any pitcher to infinity
        self.moves_list = [x for x in self.moves_list if x[1] != 0]

        # # cannot transfer from target to anything
        self.moves_list = [x for x in self.moves_list if x[0] != self.NUM_JUGS + 1]

        # cannot transfer to any pitcher that is already full
        for i in range(1, self.NUM_JUGS + 1):
            if state[i] == self.max_capacities[i]:
                self.moves_list = [x for x in self.moves_list if x[1] != i]

        for i in range(1, self.NUM_JUGS + 1):
            if state[i] == 0:
                self.moves_list = [x for x in self.moves_list if x[0] != i]

        # print(state)



    def is_legal_state(self, state):
        state_l = copy(state.water_state)
        if len(state_l) != len(self.max_capacities):
            raise Exception(
                f"Bad state length. State is {len(state_l)} long. while capacities are {len(self.max_capacities)} long.")
        is_legal_list = [state_l[i] <= self.max_capacities[i] for i in range(len(state_l))]
        return all(is_legal_list)

    def is_winning_state(self, state):
        state_l = copy(state.water_state)

        winning = [False] * len(state_l)
        for i in range(len(state_l)):
            is_dc = self.target_state[i] == -1
            is_hit = self.target_state[i] == state_l[i]
            winning[i] = is_dc or is_hit
        return all(winning)

    def apply(self, state, action):
        prev_state = state
        new_state = copy(state.water_state)

        from_jar = action[0]
        to_jar = action[1]

        amount_to_move = self.max_capacities[to_jar] - new_state[to_jar]
        amount_to_move = min(amount_to_move, new_state[from_jar])

        if from_jar == 0:
            new_state[to_jar] = self.max_capacities[to_jar]
        elif to_jar == -1:
            new_state[from_jar] = 0
        else:
            new_state[from_jar] -= amount_to_move
            new_state[to_jar] += amount_to_move

        n_state = State(prev_state=prev_state, water_state=new_state)
        if self.is_legal_state(n_state) and n_state.water_state[-1] < self.constraint:
            return n_state
        else:
            return None

    def get_next_states(self, state):
        state_l = copy(state.water_state)
        # print(state)
        self.get_moves_list(state.water_state)
        ret = [self.apply(state, action) for action in self.moves_list]
        ret = [s for s in ret if s is not None]
        # print([r.water_state for r in ret])
        return ret


def a_star_graph_search(start_state, lower_bound):
    visited = set()
    came_from = dict()
    distance = {start_state: 0}
    q = PriorityQueue()
    q.add(start_state)

    while q:
        current_state = q.pop()

        if current_state.get_string() in visited:
            continue

        if njugs.is_winning_state(current_state):
            return reconstruct_path(came_from, start_state, current_state)

        visited.add(current_state.get_string())

        for next_state in njugs.get_next_states(current_state):

            if next_state.heuristic == np.inf:
                visited.add(next_state.get_string())
                del next_state
                continue

            # Define Lower Bound
            if next_state.heuristic > lower_bound:
                del next_state
                continue

            if next_state.get_string() not in visited:
                q.add(next_state)
                if next_state not in distance or distance[current_state] + 1 < distance[next_state]:
                    distance[next_state] = distance[current_state] + 1
                    came_from[next_state] = current_state

        # q.print()

    return None

def reconstruct_path(came_from, start, end):
    reverse_path = [end]
    while end != start:
        end = came_from[end]
        reverse_path.append(end)
    return list(reversed(reverse_path))

def main(path=None):
    if path is None:
        raise ValueError("No Path Given")

    f = open(path, 'r')
    count = 0

    try:
        jugs = f.readline()
        jugs = jugs.split(',')
        jugs = [int(num) for num in jugs]
        target = int(f.readline())

        if type(jugs) is not list:
            raise ValueError("Invalid Format for Jugs")
        if type(target) is not int:
            raise ValueError("Invalid Format for int")
    except:
        raise ValueError("Invalid Format")

    f.close()

    global njugs

    print("Jugs : ", jugs)
    print("Target : ", target)


    if len(jugs) == 1:
        if target % jugs[0] != 0:
            print("Steps : ", -1)
            print("No Path to Display")
            print("---------------------------------------------------------------------------------------")
            return
            # return [-1, "No Path to Display"]

    njugs = NJugs(jug_capacities=jugs, target=target)
    init_state = State(water_state=njugs.jugs)

    lower_bound = target + sum(jugs)
    x = a_star_graph_search(init_state, lower_bound)

    # if x is None:
    #     return [-1, "No Path to Display"]
    # else:
    #     return [len(x) - 1, [i.get_string() for i in x]]

    if x is None:
        print("Steps : ", -1)
        print("No Path to Display")
        print("---------------------------------------------------------------------------------------")
    else:
        print("Steps : ", len(x) - 1)
        print("Path : ", [i.get_string() for i in x])
        print("---------------------------------------------------------------------------------------")


__name__ = "__main__"

# print(main("Test Files/input5.txt"))
