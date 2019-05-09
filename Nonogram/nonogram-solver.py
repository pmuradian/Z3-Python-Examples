from __future__ import print_function
from z3 import *

class Nonogram:
 	def __init__(self, filepath):
		in_file = open(filepath, "r")
		lines = in_file.readlines()
		in_file.close()

		self.column_count = int(lines[0].strip("\n").split(" ")[0])
		self.row_count = int(lines[0].strip("\n").split(" ")[1])

		self.columns = []
		self.rows = []

		self.solver = Solver()

		for i in range(1, len(lines)):
			line = lines[i].strip("\n").split(" ")
			# remove last 0
			line.pop()
 			for j in range(len(line)):
				line[j] = int(line[j])

			if i <= self.row_count:
				self.rows.append(line)
			else:
				self.columns.append(line)

  	def create_column_variables(self):
		variables = []
		for i in range(self.column_count):
			result = []
			for j in range(len(self.columns[i])):
				var_start = Int("col_start_%d_%d" % (i + 1, j + 1))
				var_end = Int("col_end_%d_%d" % (i + 1, j + 1))
				# length of the block must be self.columns[i][j] - 1
				self.solver.add(var_end - var_start == self.columns[i][j] - 1)
				# start of the block must be inside the grid
				self.solver.add(var_start >= 0)
				# end of the block must be inside the grid
				self.solver.add(var_end < self.row_count)
				result.append([var_start, var_end])
				if j > 0:
					end = result[j - 1][1]
					# there must be at least one empty cell between two blocks
					self.solver.add(var_start >= end + 2)
			variables.append(result)
		return variables

  	def create_row_variables(self):
		variables = []
		for i in range(self.row_count):
			result = []
			for j in range(len(self.rows[i])):
				var_start = Int("row_start_%d_%d" % (i + 1, j + 1))
				var_end = Int("row_end_%d_%d" % (i + 1, j + 1))
				# length of the block must be self.rows[i][j] - 1
				self.solver.add(var_end - var_start == self.rows[i][j] - 1)
				# start of the block must be inside the grid
				self.solver.add(var_start >= 0)
				# end of the block must be inside the grid
				self.solver.add(var_end < self.column_count)
				result.append([var_start, var_end])
				if j > 0:
					end = result[j - 1][1]
					# there must be at least one empty cell between two blocks
					self.solver.add(var_start >= end + 2)
			variables.append(result)
		return variables

	def print_solution(self):
		solution_count = 0
		solution_model = 0
		while self.solver.check() == sat:
			if solution_count > 1:
				break
			model = self.solver.model()
			solution_model = model
			solution = []
			for m in model:
				solution.append(m() != model[m])
			self.solver.add(Or(solution))
			solution_count = solution_count + 1

		f = open(nonogram.output_file, "a")
		if solution_count == 0:
			print("unsolvable")
			f.write("unsolvable")
		elif solution_count == 1:
			for i in range(self.row_count):
				for j in range(self.column_count):
					if solution_model.evaluate(self.cells[i][j]) == True:
						print("#", end="")
						f.write("#")
					else:
						print(".", end="")
						f.write(".")
				print("")
				f.write("\n")
		else:
			print("many solutions")
			f.write("many solutions")
		f.close()

  	def solve(self):
		self.cells = [ [ Bool("cell_%d_%d" % (i + 1, j + 1)) for j in range(self.column_count)] for i in range(self.row_count) ]

		self.column_vars = self.create_column_variables()
		self.row_vars = self.create_row_variables()

		# add constraints for columns
		for i in range(self.column_count):
			col_vars = []
			for row in self.cells:
				col_vars.append(row[i])
			for j in range(len(col_vars)):
				constraint = Or([And(start <= j, j <= end) for (start, end) in self.column_vars[i]])
				self.solver.add(col_vars[j] == constraint)

		# add constraints for rows
		for i in range(self.row_count):
			for j in range(len(self.cells[i])):
				constraint = Or([And(start <= j, j <= end) for (start, end) in self.row_vars[i]])
				self.solver.add(self.cells[i][j] == constraint)

		self.print_solution()

if len(sys.argv) > 0:
	nonogram = Nonogram(sys.argv[1])
	nonogram.output_file = sys.argv[1].strip(".in") + ".out"
	nonogram.solve()
# nonogram = Nonogram("./tester/sample_2.in")
# nonogram.solve()
# nonogram = Nonogram("./tester/sample_1.in")
# nonogram.solve()
# nonogram = Nonogram("./tester/sample.in")
# nonogram.solve()
# nonogram = Nonogram("./tester/ambiguous.in")
# nonogram.solve()
# nonogram = Nonogram("./tester/unsolvable.in")
# nonogram.solve()
