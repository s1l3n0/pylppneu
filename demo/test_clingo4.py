from gringo import Control, Model, Fun

def on_model(model):
    output = ""
    for atom in model.atoms(Model.ATOMS):
        output += str(atom) + ", "
    if output != "":
        print output[:-2]

prg = Control()
prg.load("external.lp")
prg.ground([("base", [])])

print "############## 1"
prg.assign_external(Fun("a"), True)
prg.solve(on_model=on_model)

print "############## 2"
prg.assign_external(Fun("a"), False)
prg.solve(on_model=on_model)

