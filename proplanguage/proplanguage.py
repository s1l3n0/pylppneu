import dependencygraph as dg
# from gringo import Control, Model, Fun     ## for clingo 4.5.4
from clingo import Control                   ## for clingo 5.1.0

import ASPProgramLoader

class Atom:
    # -- Fields --
    # name : String
    def __init__(self, name):
        if name.isalnum():
            self.name = name
        else:
            raise ValueError("Only alphanumeric strings are allowed for atoms. ["+name+"]")

    def __str__(self):
        # return "[A]"
        return self.name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def to_ASP(self):
        return self.name


class Literal:
    # -- Fields --
    # atom : Atom
    # neg : Boolean
    def __init__(self, atom, neg=False):
        self.atom = atom
        self.neg = neg

    def __str__(self):
        if self.neg:
            prefix = "-"
        else:
            prefix = ""
        # return "[L]"
        return prefix + str(self.atom)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash((self.neg, self.atom.name))

    def to_ASP(self):
        if self.neg:
            prefix = "-"
        else:
            prefix = ""
        return prefix + str(self.atom)


class ExtLiteral:
    # -- Fields --
    # literal : Literal
    # naf : Boolean
    def __init__(self, literal, naf=False):
        self.literal = literal
        self.naf = naf

    def __str__(self):
        if self.naf:
            prefix = "not "
        else:
            prefix = ""
        # return "[E]"
        return prefix + str(self.literal)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def to_ASP(self):
        if self.naf:
            prefix = "not "
        else:
            prefix = ""
        return prefix + str(self.literal)


class Formula:
    # -- Fields --
    # operator : Operator
    # inputFormulas : Formula list
    # inputTerms : ExtLiteral list
    def __init__(self, operator, input_formulas=(), input_terms=()):
        self.operator = operator
        self.input_formulas = input_formulas
        self.input_terms = input_terms

    def __str__(self):
        output = "{'operator': " + str(self.operator) + ", "
        if len(self.input_formulas) > 0:
            output += "'inputFormulas': ["
            for inputFormula in self.input_formulas:
                output += str(inputFormula) + ", "
            output = output[:-2] + "]"
        elif len(self.input_terms) > 0:
            output += "'inputTerms': ["
            for inputTerm in self.input_terms:
                output += str(inputTerm) + ", "
            output = output[:-2] + "]"
        return output + "}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def extract_literals(self, filter=None):
        literals = []
        if len(self.input_formulas) > 0:
            for inputFormula in self.input_formulas:
                literals.extend(inputFormula.extract_literals(filter))
        elif len(self.input_terms) > 0:
            for ext_literal in self.input_terms:
                if filter is None:
                    literals.append(ext_literal.literal)
                elif ext_literal.naf == filter:
                    literals.append(ext_literal.literal)
        return literals

    def extract_asserted_literals(self):
        return self.extract_literals(False)

    def extract_naf_literals(self):
        return self.extract_literals(True)

    def to_ASP(self, head=False):
        output = ""

        n = len(self.input_formulas)

        if self.operator is Operator.NONE:
            if n > 1:
                raise ValueError("there should be only an atom here")
        elif self.operator is Operator.AND:
            if head is True:
                output += n + "{"
        elif self.operator is Operator.OR:
            output += "1{"
        elif self.operator is Operator.CHOICE:
            # TODO: choice parameters to be implemented
            output += "{"
        elif self.operator is Operator.XOR:
            output += "1{"
        else:
            raise ValueError("Not yet implemented")

        if len(self.input_formulas) > 0:
            for formula in self.input_formulas:
                output += formula.to_ASP() + ', '
            output = output[0:-2]
        else:
            if len(self.input_terms) > 1:
                raise ValueError("In this atomic formula there are more atoms !?!")
            output += self.input_terms[0].to_ASP()

        if self.operator is not Operator.NONE:
            if self.operator is Operator.AND:
                if head is True:
                    output += "}" + n
            elif self.operator is Operator.OR:
                output += "}"
            elif self.operator is Operator.CHOICE:
                # TODO: choice parameters to be implemented
                output += "}" + n
            elif self.operator is Operator.XOR:
                output += "}1"
            else:
                raise ValueError("Not yet implemented")

        return output


class Operator:
    NONE = 0
    AND = 1
    OR = 2
    XOR = 3
    CHOICE = 4


class Rule:
    # -- Fields --
    # head : Formula
    # body : Formula
    def __init__(self, head=None, body=None):
        self.head = head
        self.body = body

    def __str__(self):
        return "{'body': " + str(self.body) + ", 'head': " + str(self.head) + "}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def extract_literals(self, filter=None):
        atoms = []
        if self.head is not None:
            atoms.extend(self.head.extract_literals(filter))
        if self.body is not None:
            atoms.extend(self.body.extract_literals(filter))
        return atoms

    def extract_asserted_literals(self):
        return self.extract_literals(False)

    def extract_naf_literals(self):
        return self.extract_literals(True)

    def is_norm_rule(self):
        return self.head is not None and self.body is not None

    def is_fact(self):
        return self.head is not None and self.body is None

    def is_constraint(self):
        return self.head is None and self.body is not None

    def to_ASP(self):
        output = ""
        if self.head is not None:
            output += self.head.to_ASP()
        if self.body is not None:
            output += " :- " + self.body.to_ASP()
        return output + "."


class Program:
    # -- Fields --
    # rule_list
    def __init__(self, rule_list=()):
        self.rule_list = rule_list
        self.answer_sets = None

    def dependency_graph(self):
        return dg.DependencyGraph(self.rule_list)

    def to_ASP(self):
        output = ""
        for rule in self.rule_list:
            output += rule.to_ASP() + "\n"
        return output

    def __on_model(self, model):
        self.answer_sets = []
        answer_set = []
        for atom in model.symbols(atoms="True"):       ## for clingo 5.1.0
            answer_set.append(ASPProgramLoader.parse_literal(str(atom)))
        self.answer_sets.append(answer_set)

    def solve(self):
        tmp_file = "../tmp/program.lp"

        out_file = open(tmp_file, "w")
        out_file.write(self.to_ASP())
        out_file.close()

        ctl = Control()
        ctl.load(tmp_file)
        ctl.ground([("base", [])])
        ctl.solve(on_model=self.__on_model)
        return self.answer_sets

if __name__ == '__main__':
    program = ASPProgramLoader.parse_string("b :- not a. -c :- a. a.")
    answer_sets = program.solve()
    assert len(answer_sets) == 1
    assert len(answer_sets[0]) == 2
    assert answer_sets[0][0] == Literal(Atom("a"), False)
    assert answer_sets[0][1] == Literal(Atom("c"), True)
