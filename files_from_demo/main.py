import GEARS as g
import map_generator as mg


if __name__ == "__main__":
    system = g.GEARS()
    print("0: Medical supplies\n1: Emergency shelter\n2: Fuel\n3: Food and Water")
    label = input("Input type of cargo -> ")
    system.show_label(label)
    system.traverse_maze()
    mg.Map_Generator(system.out_array, 1)
