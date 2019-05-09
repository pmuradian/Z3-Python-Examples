from __future__ import print_function
from z3 import *
import os
import sys

class Cargoes:
	def __init__(self, grid_size, row_string, col_string):
		self.size = int(grid_size)
		self.cols = []
		self.rows = []

		for l in zip(row_string.split(" "), col_string.split(" ")):
			self.rows.append(int(l[0]))
			self.cols.append(int(l[1]))

	def solve(self):
		self.solver = Solver()
		self.cells = [[Int("cell_%d_%d" % (i + 1, j + 1)) for j in range(self.size)] for i in range(self.size)]

		# row and column constraints
		for i in range(self.size):
			column = []
			for j in range(self.size):
				self.solver.add(self.cells[i][j] >= 0)
				self.solver.add(self.cells[i][j] <= min(self.cols[j], self.rows[i]))
				column.append(self.cells[j][i])
			self.solver.add(Sum(self.cells[i]) == self.rows[i])
			self.solver.add(Sum(column) == self.cols[i])

		# no diagonals
		# no overlaping cargoes are a special case of no diagonals
		# corner cases
		self.solver.add(Or(self.cells[0][0] == 0, And(self.cells[0][0] > 0, self.cells[1][1] == 0)))
		self.solver.add(Or(self.cells[0][self.size - 1] == 0, And(self.cells[0][self.size - 1] > 0, self.cells[1][self.size - 2] == 0)))
		self.solver.add(Or(self.cells[self.size - 1][0] == 0, And(self.cells[self.size - 1][0] > 0, self.cells[self.size - 2][1] == 0)))
		self.solver.add(Or(self.cells[self.size - 1][self.size - 1] == 0, And(self.cells[self.size - 1][self.size - 1] > 0, self.cells[self.size - 2][self.size - 2] == 0)))

		# board middle cases
		for i in range(1, self.size - 1):
			for j in range(1, self.size - 1):
				self.solver.add(Or(self.cells[i][j] == 0, And(self.cells[i][j] > 0, self.cells[i-1][j-1] == 0, self.cells[i-1][j+1] == 0, self.cells[i+1][j+1] == 0, self.cells[i+1][j-1] == 0)))
		
		# board edge cases
		for i in range(1, self.size - 1):
			# vertical edges
			self.solver.add(Or(self.cells[i][0] == 0, And(self.cells[i][0] > 0, self.cells[i - 1][1] == 0, self.cells[i + 1][1] == 0)))
			self.solver.add(Or(self.cells[i][self.size - 1] == 0, And(self.cells[i][self.size - 1] > 0, self.cells[i - 1][self.size - 2] == 0, self.cells[i + 1][self.size - 2] == 0)))
			# horizontal edges
			self.solver.add(Or(self.cells[0][i] == 0, And(self.cells[0][i] > 0, self.cells[1][i - 1] == 0, self.cells[1][i - 1] == 0)))
			self.solver.add(Or(self.cells[self.size - 1][i] == 0, And(self.cells[self.size - 1][i] > 0, self.cells[self.size - 1][i - 1] == 0, self.cells[self.size - 1][i + 1] == 0)))
		
		if self.solver.check() == sat:
			ouput = ""
			for i in range(self.size):
				for j in range(self.size):
					ouput = ouput + str(self.solver.model().evaluate(self.cells[i][j]))
					if j < self.size - 1:
						ouput = ouput + " "
				print(ouput)
				ouput = ""
		else:
			print("unsolvable")

# read board size, raw constraints, column constraints
boardSize = raw_input()
rawConstraints  = raw_input()
columnConstraints = raw_input()

cargoesInstance = Cargoes(boardSize, rawConstraints, columnConstraints)
cargoesInstance.solve()