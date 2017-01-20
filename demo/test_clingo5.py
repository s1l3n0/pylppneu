from clingo import Control, Function

def on_model(model):
    output = ""
    for atom in model.symbols(shown=True):
        output += str(atom) + ", "
    if output != "":
        print output[:-2]

prg = Control()
prg.load("external.lp")
prg.ground([("base", [])])

print "############## 1"
prg.assign_external(Function("d"), True)
prg.solve(on_model=on_model)

print "############## 2"
prg.assign_external(Function("d"), True)
prg.solve(on_model=on_model)

