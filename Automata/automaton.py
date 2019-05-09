# The hole algorithm was changed, in the first version, every word of length 'n' was generated
# For each word, a propositional sentence was consturcted using automaton description in a similar manner to the new algorithm,
# but the 'final' sentence itself was completely different, and was tested for satisfiability

# New version of the algorithm constructs a propositional formula using automaton description and the number 'n'
# As an abstraction on an automaton run, a boolean matrix is being used, each cell of the matrix is a representation of a letter
# The cells on the diagonal (cell[i][i]) represents the sate of the automaton at a given step

# The 'final' sentence that describes the computation is a logical 'And' between the following propositions
# Every cell must have a single value, exept the diagonal cells, because the automaton is nondeterministic
# Cell[0][0] must be an initial state
# Every diagonal cell must not be a final state
# Every row of the matrix must be represented as a transition from the previous row

# If the 'final' sentence evaluates to 'sat' then the automaton rejects at least one word of a given length
# If the 'final' sentence evaluates to 'unsat' then the automaton accepts all words of a given length

from z3 import *
import time
import itertools
import os
import sys

class Transition:
    """docstring for ."""
    def __init__(self, args):
        self.inputState = args[0]
        self.inputSymbol = args[1]
        self.outputState = args[2]

class Automaton:
    """docstring for ."""
    def __init__(self, args):
        if len(args) == 5:
            self.alphabetCount = int(args[0])
            self.stateCount = int(args[1])
            self.initialCount = int(args[2])
            self.finalCount = int(args[3])
            self.transitionCount = int(args[4])
        else:
            print("incorrect number of arguments to initialize the automaton")
            exit(1)

    def indexForSymbol(self, symbol):
        return self.alphabet.index(symbol)

    def indexForState(self, state):
        return self.states.index(state)

    def initialStateIndex(self):
        ret = []
        for st in self.initial:
            ret.append(self.indexForState(st))
        return ret

    def acceptingStateIndex(self):
        ret = []
        for st in self.accepting:
            ret.append(self.indexForState(st))
        return ret

# Main

automaton = Automaton(raw_input().split(" "))
automaton.alphabet = raw_input().split(" ")
automaton.states = raw_input().split(" ")
automaton.initial = raw_input().split(" ")
automaton.accepting = raw_input().split(" ")
automaton.transitions = []

next_index = 5

for i in range(automaton.transitionCount):
    tr = Transition(raw_input().split(" "))
    automaton.transitions.append(tr)
    next_index = next_index + 1

automaton.word_length = int(raw_input())

length = automaton.word_length + 1

# cells[i][j][k] where k is a value between 0 and automaton.alphabetCount if i != j and automaton.stateCount if i == j
# and indicates if cell[i][j] contains symbol (0 to automaton.alphabetCount) or state (0 to automaton.stateCount)
cells = []

for i in range(length):
    c1 = []
    for j in range(length):
        c2 = []
        for k in range(automaton.stateCount if i == j else automaton.alphabetCount):
            c2.append(Bool("x_%s_%s_%s" % (i, j, k)))
        c1.append(c2)
    cells.append(c1)


transitionValuation = []
singleValueConstraint = []
i = 0
j = 0
k = 0

for i in range(length):
    # cell can contain only one alphabet value
    for j in range(length):
        arr = []
        var = []
        if i == j:
            continue
        for k in range(automaton.alphabetCount):
            var.append(cells[i][j][k])
            for t in range(automaton.alphabetCount):
                # no more than one variable
                if k != t:
                    arr.append(Or(Not(cells[i][j][k]), Not(cells[i][j][t])))
        singleValueConstraint.append(And(Or(var), And(arr)))

    # value in a cell depends on 2 cells direcly above it
    if i + 1 < length:
        for t in automaton.transitions:
            in_state = automaton.indexForState(t.inputState)
            in_symbol = automaton.indexForSymbol(t.inputSymbol)
            out_state = automaton.indexForState(t.outputState)
            temp = Implies(And(cells[i][i][in_state], cells[i][i + 1][in_symbol]), cells[i + 1][i + 1][out_state])
            transitionValuation.append(temp)

# every final state must be false
accept_formulas = []
for st in automaton.acceptingStateIndex():
    for i in range(length):
        accept_formulas.append(Not(cells[i][i][st]))

# all initial states must be true
initial_start_configs = []
for st in automaton.initialStateIndex():
    initial_start_configs.append(cells[0][0][st])

solver = Solver()
sentence = And(And(transitionValuation), And(singleValueConstraint), And(accept_formulas), And(initial_start_configs))
solver.add(sentence)

# check if the formula is satisfiable
if solver.check() == sat:
    print("NO\n")
    model = solver.model()
    rejectedWord = ""
    # reconstruct rejected word
    for i in range(1, length):
        for j in range(automaton.alphabetCount):
            if model[cells[i - 1][i][j]]:
                rejectedWord = rejectedWord + automaton.alphabet[j] + " " 
    
    if len(rejectedWord) > 0:
        rejectedWord = rejectedWord[:-1]
    print(rejectedWord)
else:
    print("YES")