from clingo import Control, Function, parse_program

def on_model(model):
    output = ""
    for atom in model.symbols(shown=True):
        output += str(atom) + ", "
    if output != "":
        print output[:-2]

ctl = Control()
ctl.configuration.solve.models = 0              # for all answer sets
with ctl.builder() as builder:
    parse_program("#external c. {a; b}. ", lambda statement: builder.add(statement))

ctl.ground([("base", [])])
ctl.assign_external(Function("c"), True)
ctl.solve(on_model=on_model)
