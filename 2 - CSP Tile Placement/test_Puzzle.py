from unittest import TestCase
import os


class Test(TestCase):
    def test_main(self):
        from Puzzle import main

        x = os.listdir("Tests")

        print_graph =False

        for i in x:
            main("Tests/" + i, print_graph_list=print_graph)
