import numpy as np
from collections import Counter
from copy import deepcopy


class Block:
    def __init__(self, mp):
        self.map = mp
        self.map_tile = deepcopy(self.map)
        self.domain = ['L1', 'Outer', 'Block']
        # self.domain = ['L1', 'L2', 'L3', 'L4', 'Outer', 'Block']
        self.domain_available = deepcopy(self.domain)
        self.is_tile_placed = False
        self.current_tile = None
        self.bush_count = self.get_bush_count_without_tile()

        self.bush_count_of_all_tiles = self.get_bush_count_with_tiles()


    def update_map(self, tile):
        self.map_tile = deepcopy(self.map)

        if tile == 'Block':
            self. map_tile = [[-1, -1, -1, -1],
                              [-1, -1, -1, -1],
                              [-1, -1, -1, -1],
                              [-1, -1, -1, -1]]

        if tile == 'Outer':
            self.map_tile = [[-1, -1, -1, -1],
                             [-1, self.map[1][1], self.map[1][2], -1],
                             [-1, self.map[2][1], self.map[2][2], -1],
                             [-1, -1, -1, -1]]

        if tile == 'L1':
            self.map_tile[0] = [-1, -1, -1, -1]
            for i in self.map_tile:
                i[0] = -1

        if tile == 'L2':
            self.map_tile[0] = [-1, -1, -1, -1]
            for i in self.map_tile:
                i[-1] = -1

        if tile == 'L3':
            self.map_tile[-1] = [-1, -1, -1, -1]
            for i in self.map_tile:
                i[-1] = -1

        if tile == 'L4':
            self.map_tile[-1] = [-1, -1, -1, -1]
            for i in self.map_tile:
                i[0] = -1

    def print_block_without_tile(self):
        for i in self.map:
            print(i)

    def print_block_with_tile(self):
        for i in self.map_tile:
            print(i)

    def get_bush_count_without_tile(self):
        items = Counter(np.array(self.map).flatten())
        for i in range(1, 5):
            if i not in items:
                items[i] = 0
        del items[0]
        return dict(items)

    def get_bush_count_with_tile(self):
        items = Counter(np.array(self.map_tile).flatten())
        for i in range(1, 5):
            if i not in items:
                items[i] = 0
        del items[-1]
        del items[0]
        return dict(items)

    def get_domains(self):
        return self.domain_available

    def get_length(self):
        if self.is_tile_placed: return 9
        return len(self.domain_available)

    def get_min(self):
        current_tile = deepcopy(self.map_tile)

        min_list = [16, 16, 16, 16]

        for tile in self.domain_available:

            self.update_map(tile)
            x = self.get_bush_count_with_tile()

            b = [x[1], x[2], x[3], x[4]]

            for i in range(4):
                if min_list[i] > b[i]:
                    min_list[i] = b[i]

        self.map_tile = deepcopy(current_tile)

        return min_list

    def get_bush_count_with_tiles(self):
        current_tile = deepcopy(self.map_tile)

        ret_list = dict()

        for tile in self.domain_available:
            self.update_map(tile)
            x = self.get_bush_count_with_tile()

            b = [x[1], x[2], x[3], x[4]]

            ret_list[tile] = deepcopy(b)

        self.map_tile = deepcopy(current_tile)

        return ret_list

    def reset_tile(self):
        self.map_tile = deepcopy(self.map)

    def update_domains(self, remaining_tiles, remaining=None, reset=False):
        if self.is_tile_placed:
            return

        if reset:
            self.domain_available = deepcopy(self.domain)


        # Remove Domains Beacuse there are no tiles of a type left
        if remaining_tiles[0] == 0 and 'Block' in self.domain_available:
            self.domain_available.remove('Block')
        if remaining_tiles[1] == 0 and 'Outer' in self.domain_available:
            self.domain_available.remove('Outer')
        if remaining_tiles[2] == 0:
            if 'L1' in self.domain_available: self.domain_available.remove('L1')
            if 'L2' in self.domain_available: self.domain_available.remove('L2')
            if 'L3' in self.domain_available: self.domain_available.remove('L3')
            if 'L4' in self.domain_available: self.domain_available.remove('L4')


        # Remove Domains that will cause the number of bushes to go above target
        to_removal = []
        for domain in self.domain_available:
            condition = [curr <= rem for curr, rem in zip(self.bush_count_of_all_tiles[domain], remaining)]

            if False in condition:
                to_removal.append(domain)

        self.domain_available = [x for x in self.domain_available if x not in to_removal]








    def reset_domains(self):
        if not self.is_tile_placed:
            self.domain_available = ['Block', 'Outer', 'L1', 'L2', 'L3', 'L4']




# __name__ = "__main__"
#
# x = Block([[0, 1, 4, 2], [4, 0, 4, 4], [2, 4, 2, 2], [0, 0, 4, 1]])
# x.update_map('L4')
#
# x.print_block_without_tile()
# print()
# x.print_block_with_tile()
# print()
# x.reset_tile()
# x.print_block_with_tile()
# print()
# x.update_map('L4')
#
# print(x.get_bush_count_without_tile())
# print()
# print(x.get_bush_count_with_tile())
# print()
#
# x.update_domains(remaining_tiles=[1, 1, 1])
# print(x.get_domains())
# print(x.get_length())
# print()
#
# x.print_block_with_tile()
# print()
#
# print(x.bush_count_of_all_tiles)


