# pypneu
*Python library for Logic Programming Petri Nets (LPPN)*

LPPN integrates procedural aspects specified by Petri Nets with declarative specified by Logic Programming (ASP). 
In contrast to `lppneu`, coded in `Java` and calling the ASP solver `lparse+smodels`, `pypneu` exploits the python module of `clingo`; this means that an instance of the declarative bindings is maintained within the script, without requiring regrounding at each cycle. Performances are much better.

## files

- **pypneu**: basic Petri Nets (PN) interpreter (execution, analysis) 
- **pypropneu**: propositional LPPNs interpreter providing two operational semantics 
  - *hybrid*: separating the procedural components (brute execution + backtracking) and the declarative components (determined by clingo)
  - *denotational*: translating the net to ASP using Event-Calculus, and calling `clingo`.
- **proplanguage**: propositional ASP-like language parser

## dependencies

**clingo** (the ASP solver)
- download the sources from [https://github.com/potassco/clingo]
- compile the python library following the instructions
- add the library to the project dependencies 

To work on the grammars, you need to download the ANTLR complete JAR file and the necessary Python module.
The easiest way is using pip.

> pip install antlr4-python2-runtime

