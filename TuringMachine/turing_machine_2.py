from z3 import *
import time
import os

class Transition:
    """docstring for ."""
    def __init__(self, args):
        self.inputSymbol = args[0]
        self.inputState = args[1]
        self.outputSymbol = args[2]
        self.outputState = args[3]
        self.direction = int(args[4])

class Machine:
    """docstring for ."""
    def __init__(self, args):
        if len(args) == 3:
            self.alphabetCount = int(args[0])
            self.stateCount = int(args[1])
            self.transitionCount = int(args[2])
        else:
            print("incorrect number of arguments to initialize the machine")

    def indexForSymbol(self, symbol):
        return self.alphabet.index(symbol)

    def indexForState(self, state):
        return self.alphabetCount + self.states.index(state)

    def initialStateIndex(self):
        return self.indexForState(self.initial)

    def acceptingStateIndex(self):
        return self.indexForState(self.accepting)

    def simulateRun(self, machine_state, head_pos, chars, max_number, current_number):

        if head_pos > self.word_length:
            return []

        # Loop was found
        if current_number > max_number:
            return []

        string = ""
        for i in range(self.word_length):
            string += chars[i] + "|"
            if head_pos == i:
                string += machine_state
            string += " "

        output_state = machine_state
        for t in self.transitions:
             if t.inputSymbol == chars[head_pos]:
                 if t.inputState == machine_state:
                     chars[head_pos] = t.outputSymbol
                     output_state = t.outputState
                     if t.direction == 1:
                         head_pos = head_pos + 1
                         break
                     elif t.direction == -1:
                         head_pos = head_pos - 1
                         break
                     else :
                        break

        if self.indexForState(machine_state) == self.indexForState(self.accepting):
            return [string]
        else:
            ret = self.simulateRun(output_state, head_pos, chars, max_number, current_number + 1)
            if len(ret) > 0:
                ret.append(string)
            return ret

    # returns the possible transition values
    def transitionsFor(self, window):
        right = window[2]
        middle = window[1]
        left = window[0]

        trns = []

        # left is a state
        if left >= self.alphabetCount:
            for trans in self.transitions:
                if trans.inputSymbol == self.alphabet[middle]:
                    if trans.inputState == self.states[left - self.alphabetCount]:
                        if trans.direction == 1:
                            trns.append((self.indexForSymbol(trans.outputSymbol), self.indexForState(trans.outputState), right))
                        elif trans.direction == 0:
                            trns.append((self.indexForState(trans.outputState), self.indexForSymbol(trans.outputSymbol), right))
                        else:
                            for val in self.alphabet:
                                trns.append((self.indexForSymbol(val), self.indexForSymbol(trans.outputSymbol), right))
        # middle is a state
        elif middle >= self.alphabetCount:
            for trans in self.transitions:
                if trans.inputSymbol == self.alphabet[right]:
                    if trans.inputState == self.states[middle - self.alphabetCount]:
                        if trans.direction == 1:
                            trns.append((left, self.indexForSymbol(trans.outputSymbol), self.indexForState(trans.outputState)))
                        elif trans.direction == 0:
                            trns.append((left, self.indexForState(trans.outputState), self.indexForSymbol(trans.outputSymbol)))
                        else:
                            trns.append((self.indexForState(trans.outputState), left, self.indexForSymbol(trans.outputSymbol)))
        return trns


input_file_path = ""

if len(sys.argv) > 1:
    input_file_path = sys.argv[1]

if input_file_path == "":
    print("Missing input file")
    sys.exit()



in_file = open(input_file_path, "r")
lines = in_file.readlines()
output_file_path = os.path.splitext(input_file_path)[0] + ".tout"
out_file = open(output_file_path, "w+")

in_file.close()

# print(lines)

machine = Machine(lines[0].strip("\n").split(" "))
machine.alphabet = lines[1].strip("\n")
machine.states = lines[2].strip("\n").split(" ")
machine.initial = lines[3].strip("\n")
machine.accepting = lines[4].strip("\n")
machine.transitions = []

next_index = 5

for i in range(machine.transitionCount):
    machine.transitions.append(Transition(lines[i + 5].strip("\n").split(" ")))
    next_index = next_index + 1

machine.word_length = int(lines[next_index])
machine.word = lines[next_index + 1].replace(" ", "").strip("\n")
# print(machine.word)

print("Machine configured, solving")

# check if word contains characters from the alphabet
for ch in machine.word:
    if not any(ch in s for s in machine.alphabet):
        print("NO")
        out_file.write("NO")
        out_file.close()
        sys.exit(0)



length = len(machine.word) + 1

# cells[i][j][k] where k is a value between 0 and machine.alphabetCount + machine.stateCount
# and indicates if cell[i][j] contains symbol (0 to machine.alphabetCount) or state (machine.alphabetCount to machine.stateCount)
cells = [ [ [Bool("x_%s_%s_%s" % (i+1, j+1, k+1)) for k in range(machine.alphabetCount + machine.stateCount)] for j in range(length)] for i in range(length)]

# only one value per cell
cell_formula = 0
start_formula = 0
accept_formula = 0
transition_formula = 0
transitionValuation = []
bar = []
windows = []
start_config = []
i = 0

for i in range(length):
    # formula for the first row (starts from initial state)
    start_config.append(cells[0][i][machine.indexForSymbol(machine.word[i - 1])])

    for j in range(length):
        arr = []
        rng = range(machine.alphabetCount + machine.stateCount)
        # at least one variable
        var = Or([cells[i][j][k] for k in rng])
        # transition formula
        if len(windows) > 0:
            win = Or([windows[w] for w in range(len(windows))])
            transitionValuation.append(win)
        windows = []
        # value in a cell depends on 3 cells direcly above it
        for k in rng:
            for t in rng:
                for z in rng:
                    if i + 1 < length and j + 2 < length:
                        # value of cells[i][j] is a state
                        if k >= machine.alphabetCount and t < machine.alphabetCount and z < machine.alphabetCount:
                            trns = machine.transitionsFor((k, t, z))
                            # for every transition
                            for trz in trns:
                                temp = And(cells[i][j][k], cells[i][j + 1][t], cells[i][j + 2][z], cells[i + 1][j][trz[0]], cells[i + 1][j + 1][trz[1]], cells[i + 1][j + 2][trz[2]])
                                windows.append(temp)

                        # value of cells[i][j + 1] is a state
                        elif t >= machine.alphabetCount and k < machine.alphabetCount and z < machine.alphabetCount:
                            trns = machine.transitionsFor((k, t, z))
                            # for every transition
                            for trz in trns:
                                temp = And(cells[i][j][k], cells[i][j + 1][t], cells[i][j + 2][z], cells[i + 1][j][trz[0]], cells[i + 1][j + 1][trz[1]], cells[i + 1][j + 2][trz[2]])
                                windows.append(temp)
                        # value of cells[i][j + 2] is a state
                        elif z >= machine.alphabetCount and t < machine.alphabetCount and k < machine.alphabetCount:
                            # value for cells[i][j] can be anything
                            for st in machine.states:
                                temp = And(cells[i][j][k], cells[i][j + 1][t], cells[i][j + 2][z], cells[i + 1][j][k], cells[i + 1][j + 1][machine.indexForState(st)], cells[i + 1][j + 2][t])
                                windows.append(temp)
                            for smb in range(machine.alphabetCount + machine.stateCount):
                                temp = And(cells[i][j][k], cells[i][j + 1][t], cells[i][j + 2][z], cells[i + 1][j][k], cells[i + 1][j + 1][t], cells[i + 1][j + 2][smb])
                                windows.append(temp)

                        elif z < machine.alphabetCount and t < machine.alphabetCount and k < machine.alphabetCount:
                            # value for cells[i][j] can be anything
                            for st in machine.states:
                                temp1 = And(cells[i][j][k], cells[i][j + 1][t], cells[i][j + 2][z], cells[i + 1][j][k], cells[i + 1][j + 1][t], cells[i + 1][j + 2][machine.indexForState(st)])
                                temp2 = And(cells[i][j][k], cells[i][j + 1][t], cells[i][j + 2][z], cells[i + 1][j][machine.indexForState(st)], cells[i + 1][j + 1][t], cells[i + 1][j + 2][z])
                                windows.append(temp1)
                                windows.append(temp2)

                            temp1 = And(cells[i][j][k], cells[i][j + 1][t], cells[i][j + 2][z], cells[i + 1][j][k], cells[i + 1][j + 1][t], cells[i + 1][j + 2][z])
                            temp2 = And(cells[i][j][k], cells[i][j + 1][t], cells[i][j + 2][z], cells[i + 1][j][k], cells[i + 1][j + 1][t], cells[i + 1][j + 2][z])
                            windows.append(temp1)
                            windows.append(temp2)

                if k == t:
                    continue
                # no more than one variable
                arr.append(Or(Not(cells[i][j][k]), Not(cells[i][j][t])))
        # one value per cell (either a state or a symbol)
        bar.append(And(var, And([arr[index] for index in range(len(arr))])))

# every cell can contain accepting state
accept_formula = Or([Or([cells[i][j][machine.acceptingStateIndex()] for j in range(length)]) for i in range(length)])

cell_formula = And([bar[q] for q in range(len(bar))])
start_formula = And([start_config[n] for n in range(len(start_config))])

# every value in a cell must be calculated from the 3 cells above it by transition function
transition_formula = And([transitionValuation[indx] for indx in range(len(transitionValuation))])

s = Solver()
s.add(And(transition_formula, start_formula, cell_formula, accept_formula))

# check if the formula is satisfiable
if s.check() == sat:
    # start from initial state and head position on the first cell
    run = machine.simulateRun(machine.initial, 0, list(machine.word), machine.word_length, 0)
    if len(run) > 0:
        print("YES")
        out_file.write("YES")
        for row in reversed(run):
            print(row)
            out_file.write(row)
    else:
        print("NO")
        out_file.write("NO")
else:
    print("NO")
    out_file.write("NO")

out_file.close()
