from django.db import models

# Create your models here.
class Grid:
    def __init__(self, r, c):
        """
        :param r: The row index of current grid.
        :param c: The column index of current grid.
        """
        self.is_wall = False
        self.is_visited = False
        self.r = r
        self.c = c

class Row:
    def __init__(self, row_idx, grid_num):
        """
        Row class stands for one row in the map.
        Each row contains multiple grids.

        :param row_idx: The index of current row in the entire map.
        :param grid_num: The number of grids will be contained in this row.
        """
        self.row_idx = row_idx
        self.grids = [ Grid(row_idx, i) for i in range(grid_num) ]

class Map:
    def __init__(self, height, width):
        assert height > 0 and width > 0
        self.height = height
        self.width = width
        self.rows = [ Row(i, width) for i in range(height) ]

    def display(self):
        '''
        This is a unicode fancy display.
        please make sure your terminal and your font supports unicode display.
        '''
        print(f"Current map is {self.height} x {self.width}\n")
        for row in self.rows:
            for col in row.grids:
                if col.is_wall:
                    print("\u2588", end=' ')
                else:
                    print("\u25af", end=' ')
            print('\n')

    def toggle_wall(self, i, j):
        '''
        Toggle the wall on row i column j.

        :param i: The index of row.
        :param j: The index of column.
        '''
        self.rows[i].grids[j].is_wall = not self.rows[i].grids[j].is_wall

    def shape(self):
        return self.height, self.width


# Test
# mymap = Map(4, 3)
# mymap.display()
# mymap.toggle_wall(2, 1)
# mymap.display()

# mymap.toggle_wall(2, 1)
# mymap.display()
# print(mymap.shape())