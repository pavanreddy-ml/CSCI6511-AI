import numpy as np
from Block import Block
from copy import deepcopy
from FileRead import Reader
import time
import os

class Puzzle:
    def __init__(self, graph, available_tiles, target):
        self.graph = graph
        self.graph_arr = np.array(graph)
        self.available_tiles = available_tiles

        self.target = target
        self.current_bushes = [0, 0, 0, 0]
        self.remaining = deepcopy(target)

        self.graph_size = len(graph)
        self.TILE_SIZE = 4

        assert len(np.array(graph).flatten()) == self.graph_size ** 2

        self.grid_size = self.graph_size // 4
        self.num_tiles = self.grid_size ** 2

        self.blocks = [Block(i) for i in self.get_blocks()]
        self.blocks = self.blocks
        self.domain_lengths = []

        self.steps = 0

    def get_blocks(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                yield self.graph_arr[row * 4:(row * 4) + 4, col * 4:(col * 4) + 4]


    def get_MRV_index(self):
        x = []
        for i in self.blocks:
            x.append(i.get_length())

        lowest = min(x)
        MRV_index = x.index(lowest)

        return MRV_index

    def get_LCV_order(self, index):
        temp_blocks = deepcopy(self.blocks)
        temp_block = temp_blocks[index]
        current_sum = sum([i.get_length() for i in temp_blocks if i.get_length() != 9])
        LCV = dict()

        for i in temp_block.domain_available:
            if not self.check_tile_validity(tile=i):
                continue

            temp_block.current_tile = i
            temp_block.is_tile_placed = True
            temp_block.update_map(i)
            self.update_tile_count(action='Place Tile', tile=i)
            self.update_current_bushes()

            for x in temp_blocks:
                x.update_domains(remaining_tiles=self.available_tiles, remaining=self.remaining)

            LCV[i] = current_sum - sum([i.get_length() for i in temp_blocks if i.get_length() != 9])

            self.update_tile_count(action='Remove Tile', tile=temp_block.current_tile)
        temp_block.current_tile = None
        temp_block.is_tile_placed = False
        for x in self.blocks:
            x.update_domains(remaining_tiles=self.available_tiles, remaining=self.remaining, reset=True)
        temp_block.map_tile = deepcopy(temp_block.map)

        LCV = [k for k, v in sorted(LCV.items(), key=lambda item: item[1], reverse=True)]

        return LCV




    def run(self):
        find = self.find_empty()
        if find == None:
            return True
        else:
            index = self.get_MRV_index()
            block = self.blocks[index]

        # Using LCV
        LCV = self.get_LCV_order(index=index)
        block.domain_available = deepcopy(LCV)


        for i in block.domain_available:
            self.steps += 1
            if self.steps > 50000:
                return False

            # print(self.steps)
            if not self.check_tile_validity(tile=i):
                continue

            block.current_tile = i
            block.is_tile_placed = True
            block.update_map(i)
            self.update_tile_count(action='Place Tile', tile=i)
            self.update_current_bushes()

            for x in self.blocks:
                x.update_domains(remaining_tiles=self.available_tiles, remaining=self.remaining)

            # self.print_tiles()
            self.domain_lengths = self.get_domains_length()
            # print(self.domain_lengths)


            # print([block.bush_count_of_all_tiles[x] for x in block.domain_available])
            if self.isvalid():

                if self.run():
                    return True

            self.update_tile_count(action='Remove Tile', tile=block.current_tile)
            block.current_tile = None
            block.is_tile_placed = False
            for x in self.blocks:
                x.update_domains(remaining_tiles=self.available_tiles, remaining=self.remaining, reset=True)
            block.map_tile = deepcopy(block.map)

        return False

    def update_tile_count(self, action, tile):
        if action == 'Place Tile':
            if tile == 'Block':
                self.available_tiles[0] -= 1
            if tile == 'Outer':
                self.available_tiles[1] -= 1
            if tile in ['L1', 'L2', 'L3', 'L4']:
                self.available_tiles[2] -= 1

        if action == 'Remove Tile':
            if tile == 'Block':
                self.available_tiles[0] += 1
            if tile == 'Outer':
                self.available_tiles[1] += 1
            if tile in ['L1', 'L2', 'L3', 'L4']:
                self.available_tiles[2] += 1


    def check_tile_validity(self, tile):
        if tile == 'Block' and self.available_tiles[0] == 0:
            return False
        if tile == 'Outer' and self.available_tiles[1] == 0:
            return False
        if tile in ['L1', 'L2', 'L3', 'L4'] and self.available_tiles[2] == 0:
            return False

        return True


    def update_current_bushes(self):
        total = [0, 0, 0, 0]
        for block in self.blocks:
            if block.is_tile_placed:
                total = [a+b for a, b in zip(total, block.bush_count_of_all_tiles[block.current_tile])]

        self.current_bushes = deepcopy(total)

        self.remaining = [a-b for a, b in zip(self.target, self.current_bushes)]


    def print_tiles(self):
        x = [i.current_tile for i in self.blocks]
        if None in x:
            print(False)
        else:
            print(x)

    def get_domains_length(self):
        return [i.get_length() for i in self.blocks]

    def sum_validity(self):
        outer = []
        l = [[], [], [], []]

        for block in self.blocks:
            if block.get_length() == 9:
                continue

            if 'Outer' in block.domain_available:
                outer.append(block.bush_count_of_all_tiles['Outer'])

            if 'L1' in block.domain_available or 'L2' in block.domain_available or 'L3' in block.domain_available or 'L4' in block.domain_available:
                if 'L1' in block.domain_available:
                    l[0].append(block.bush_count_of_all_tiles['L1'])
                else:
                    l[0].append([999, 999, 999, 999])

                if 'L2' in block.domain_available:
                    l[1].append(block.bush_count_of_all_tiles['L2'])
                else:
                    l[1].append([999, 999, 999, 999])

                if 'L3' in block.domain_available:
                    l[2].append(block.bush_count_of_all_tiles['L3'])
                else:
                    l[2].append([999, 999, 999, 999])

                if 'L4' in block.domain_available:
                    l[3].append(block.bush_count_of_all_tiles['L4'])
                else:
                    l[3].append([999, 999, 999, 999])

        available_tiles = deepcopy(self.available_tiles)
        num_tiles = available_tiles[1] + available_tiles[2]

        # Outer Sorted by bushes
        outer_sorted1 = sorted(outer, key=lambda x: x[0])
        outer_sorted2 = sorted(outer, key=lambda x: x[1])
        outer_sorted3 = sorted(outer, key=lambda x: x[2])
        outer_sorted4 = sorted(outer, key=lambda x: x[3])

        # Outer Sorted by bushes
        l_mins = [min(l[0][i], l[1][i], l[2][i], l[3][i]) for i in range(len(l[0]))]
        l_sorted1 = sorted(l_mins, key=lambda x: x[0])
        l_sorted2 = sorted(l_mins, key=lambda x: x[1])
        l_sorted3 = sorted(l_mins, key=lambda x: x[2])
        l_sorted4 = sorted(l_mins, key=lambda x: x[3])

        sum = [0, 0, 0, 0]

        for i in range(available_tiles[1]):
            try:
                sum[0] += outer_sorted1[i][0]
                sum[1] += outer_sorted2[i][1]
                sum[2] += outer_sorted3[i][2]
                sum[3] += outer_sorted4[i][3]
            except:
                pass

        for i in range(available_tiles[2]):
            try:
                sum[0] += l_sorted1[i][0]
                sum[1] += l_sorted2[i][1]
                sum[2] += l_sorted3[i][2]
                sum[3] += l_sorted4[i][3]
            except: pass

        for i in range(len(sum)):
            if sum[i] > self.remaining[i]:
                return False

        return True


    def isvalid(self, final=False):
        # print(self.target, self.current_bushes, self. remaining, "\n")
        # print("target: ", self.target,"Current: ", self.current_bushes, "remaining: ", self.remaining)

        # If length of any domain is 0, no solution can be found
        for i in self.blocks:
            if i.get_length() == 0:
                return False

        placed_tiles = [x.is_tile_placed for x in self.blocks]
        if False not in placed_tiles:
            for i in self.remaining:
                if i != 0:
                    return False

        for i in range(len(self.target)):
            if self.target[i] < self.current_bushes[i]:
                return False

        if self.sum_validity() == False:
            return False

        return True

    def find_empty(self):
        for i in range(len(self.blocks)):
            if self.blocks[i].is_tile_placed == False:
                return i
        return None

def main(path, print_graph_list):
    gra, til, tar = Reader.read_file(path)

    if print_graph_list:
        for i in gra:
            print(i)

    g = Puzzle(gra, available_tiles=til, target=tar)

    start_time = time.time()
    g.run()
    g.print_tiles()
    print("--- %s seconds ---" % (time.time() - start_time))
    print()

__name__ = "__main__"


# main('New Text Document.txt', print_graph_list=False)
