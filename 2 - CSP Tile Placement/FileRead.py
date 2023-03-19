import ast

class Reader:
    def __init__(self):
        print_graph=False
        pass

    @staticmethod
    def read_file(path):
        file1 = open(path, 'r')
        lines = file1.readlines()
        file1.close()

        graph = []

        length = 0
        for line in lines:
            if line[0] == "#":
                continue

            if line[0] == "\n":
                break

            if len(line) > length:
                length = len(line)


        for line in lines:
            if line[0] == "#":
                continue

            if line[0] == "\n":
                break

            x = []
            line = line.rstrip('\n')
            line = line.rstrip(' ')

            if len(line) != length:
                pad = ' ' * abs(len(line) - length)
                line = line + pad

            # print(line)

            for i in range(0, len(line), 2):


                if line[i] == ' ':
                    x.append(0)
                else:
                    x.append(int(line[i]))

            graph.append(x)

        if len(graph) + 1 == len(graph[0]):
            for i in range(len(graph)):
                graph[i] = graph[i][:-1]

        try:
            assert len(graph) == len(graph[0])
        except:
            raise ValueError("Invalid Graph")





        tiles = ""
        for line in lines:
            if line[0] == "#":
                continue

            if line[0] == "{":
                tiles = line
                tiles = tiles.rstrip("\n")[1:-1]
                tiles = dict((a.strip(), int(b.strip()))
                             for a, b in (element.split('=')
                                          for element in tiles.split(', ')))
                tiles = [tiles['FULL_BLOCK'], tiles['OUTER_BOUNDARY'], tiles['EL_SHAPE']]
                break


        target = []
        for line in lines:
            if line[0] == "#":
                continue

            if ":" in line:
                target.append(int(line.rstrip("\n").split(':')[1]))

        # print(graph)
        # print(tiles)
        # print(target)

        return graph, tiles, target


__name__ = "__main__"