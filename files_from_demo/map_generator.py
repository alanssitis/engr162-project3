"""
Module containing the code required to convert an array of directions and
distances into a mapped system
"""
# 0 NORTH
# 1 EAST
# 2 SOUTH
# 3 WEST
# 4 END
# 5 MAGNETIC
# 6 IR
# 7 START

import math as m


class Map_Generator:
    def __init__(self, input_array, map_num):
        """Initialize the class

        Args:
            input_array (list): contains direction and distance in each node
        """
        self.map_num = map_num
        self.distance_const = 1
        self.x, self.y, self.start, self.endX, self.endY = self.calculate_dimension(
            input_array)

        self.map_matrix = self.create_matrix(self.x, self.y)
        self.map_matrix = self.convert_to_matrix(
            input_array, self.start, self.map_matrix)

        self.print_map(self.map_matrix)
        self.export_map(self.map_matrix, self.map_num)

    def convert_to_matrix(self, array, start, matrix):
        """Modify inputed matrix to map out accrodint to directions

        Args:
            array (list): list containing directions
            start (int): The start x-coordinate
            matrix (matrix): the 0 matrix that will be filled

        Returns:
            matrix: binary map of the path taken by the GEARS
        """
        x = 0
        y = - 1

        fho = open("team73_hazards.csv", "w")

        fho.write(f"Team: 73\nMap: {self.map_num}\n")
        fho.write("Notes: NONE\n")
        fho.write("Hazard Type, Parameter of Interest, Parameter value, Hazard X Coordinate, Hazard Y Coordinate\n")

        for i in range(len(array)):
            node = array[i]
            if node[0] in [0, 1, 2, 3]:
                for _ in range(node[1]):
                    if node[0] == 0:
                        y += 1
                    elif node[0] == 1:
                        x += 1
                    elif node[0] == 2:
                        y -= 1
                    elif node[0] == 3:
                        x -= 1
                    
                    if array[i - 1][0] == 7:
                        matrix[y][start + x] = 5
                        array[i - 1][0] = 0
                    else:
                        matrix[y][start + x] = 1

            if node[0] == 4:
                matrix[y][start + x] = 4
            elif node[0] == 5:
                matrix[y][start + x] = 3
                fho.write(f"Magnetic Source, Field strength (uT), {m.floor(node[1])}, {(start + x) * 5}, {y * 5}\n")
            elif node[0] == 6:
                matrix[y][start + x] = 2
                fho.write(f"Heat source, IR Sensor Units (u), {m.floor(node[1])}, {(start + x) * 5}, {y * 5}\n")
                
        fho.close()
        return matrix

    def create_matrix(self, x, y):
        """Create a x by y zero matrix

        Args:
            x (int): number of 0 per row
            y (int): number of rows

        Returns:
            matrix: zero matrix of dimensions x * y
        """
        return [[0] * x for _ in range(y)]

    def calculate_dimension(self, moves):
        """Get the dimensions of the map matrix

        Args:
            moves (list): contains a list of all moves made by the truck [direction, distance]

        Returns:
            int: dimensions of matrix
        """
        x = 0
        y = 0
        x_min = 0
        x_max = 0
        height = 0

        for move in moves:
            if move[0] in [4, 5, 6]:
                pass
            elif move[0] % 2 == 0:
                y += (1 - move[0]) * move[1]
                if y > height:
                    height = y
            else:
                x += (2 - move[0]) * move[1]
                if x > x_max:
                    x_max += x - x_max
                elif x < x_min:
                    x_min += x - x_min

        width = x_max - x_min + 1
        start = - x_min

        return width, height, start, x, y

    def print_map(self, map):
        """Print out map from a binary matrix

        Args:
            map (matrix): Binary matrix representation of the map
        """
        border = ['#', ' #']
        bordercounter = 0
        map.reverse()

        for list in map:
            row = ['#']
            for path in list:
                if path == 0:
                    str = "  "
                elif path == 1:
                    str = " X"
                elif path == 2:
                    str = " I"
                elif path == 3:
                    str = " M"
                elif path == 4:
                    str = " E"
                elif path == 5:
                    str = " S"
                row.append(str)
                if bordercounter == 0:
                    border.append(' #')
            if bordercounter == 0:
                print(''.join(border))
                bordercounter += 1
            row.append(' #')
            print(''.join(row))

        print(''.join(border))

    def export_map(self, map, mapNum):
        """Export map to a csv in desired format

        Args:
            map (matrix): Two dimensional array containing map
            mapNum (int): Map number
        """
        width = len(map[1])
        height = len(map)

        with open('team73_map.csv', 'w') as f:
            f.write(f"Team: 73\nMap: {mapNum}\n")
            f.write("Unit Length: 5\nUnit: cm\n")
            f.write(f"Origin: ({self.start},0)\n")
            f.write("Notes: \n")

            for y in range(height):
                for x in range(width):
                    f.write(f"{map[y][x]},")
                f.write("\n")


if __name__ == "__main__":
    test_array = [[7, 0], [0, 4], [1, 3], [2, 1], [6, 0], [3, 0], [0, 5], [4, 0]]
    # test_array = [[0, 4], [1, 3], [2, 1], [3, 0], [0, 5], [1, 0], [2, 4], [
    #     3, 8], [0, 0], [1, 2], [2, 2], [3, 0], [0, 4], [1, 0], [2, 2]]
    # ^^ Successful
    # test_array = [[0, 2], [1, 0], [2, 0], [3, 4], [0, 4], [1, 4], [2, 2], [1, 2]]
    # ^^ Successful
    MG = Map_Generator(test_array, 1)
