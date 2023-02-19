from unittest import TestCase


class Test(TestCase):
    def test_main(self):
        from main import main
        print(main("Test Files/input.txt")[0])
        print(main("Test Files/input1.txt")[0])
        print(main("Test Files/input2.txt")[0])
        print(main("Test Files/input3.txt")[0])
        print(main("Test Files/input4.txt")[0])

