from clingo import Control

## Solve monolithically

def on_model(model):
    output = ""
    for atom in model.symbols(atoms=True):
        output += str(atom) + ", "
    print output[:-2]

ctl = Control()
ctl.load("program.lp")
ctl.ground([("base", [])])
ctl.solve(on_model=on_model)

## Solve iteratively

ctl = Control()
ctl.load("program.lp")
ctl.ground([("base", [])])

with ctl.solve_iter() as it:
    for model in it:
        output = ""
        for atom in model.symbols(atoms="True"):
            output += str(atom) + ", "
        print output[:-2]


