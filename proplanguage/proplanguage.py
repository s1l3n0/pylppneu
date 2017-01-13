import pprint


class Atom:
    # -- Fields --
    # name : String
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "[A]" + self.name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Literal:
    # -- Fields --
    # atom : Atom
    # neg : Boolean
    def __init__(self, atom, neg = False):
        self.atom = atom
        self.neg = neg

    def __str__(self):
        if (self.neg):
            prefix = "-"
        else:
            prefix = ""
        return "[L]" + prefix + str(self.atom)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class ExtLiteral:
    # -- Fields --
    # literal : Literal
    # naf : Boolean
    def __init__(self, literal, naf = False):
        self.literal = literal
        self.naf = naf

    def __str__(self):
        if (self.naf):
            prefix = "not"
        else:
            prefix = ""
        return "[E]" + prefix + str(self.literal)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Formula:
    # -- Fields --
    # operator : Operator
    # inputFormulas : Formula list
    # inputTerms : ExtLiteral list
    def __init__(self, operator, inputFormulas = (), inputTerms = ()):
        self.operator = operator
        self.inputFormulas = inputFormulas
        self.inputTerms = inputTerms

    def __str__(self):
        output = "{'operator': " + str(self.operator) + ", "
        if len(self.inputFormulas) > 0:
            output += "'inputFormulas': ["
            for inputFormula in self.inputFormulas:
                output += str(inputFormula) + ", "
            output = output[:-2] + "]"
        elif len(self.inputTerms) > 0:
            output += "'inputTerms': ["
            for inputTerm in self.inputTerms:
                output += str(inputTerm) + ", "
            output = output[:-2] + "]"
        return output + "}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def extract_literals(self, filter = None):
        literals = []
        if len(self.inputFormulas) > 0:
            for inputFormula in self.inputFormulas:
                literals.extend(inputFormula.extract_literals(filter))
        elif len(self.inputTerms) > 0:
            for ext_literal in self.inputTerms:
                if filter is None or ext_literal.naf is filter:
                    literals.append(ext_literal.literal)
        return literals

    def extract_pos_literals(self):
        return self.extract_literals(False)

    def extract_neg_literals(self):
        return self.extract_literals(True)

    def extract_atoms(self):
        return self.extract_literals(None)

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
    def __init__(self, head = None, body = None):
        self.head = head
        self.body = body

    def __str__(self):
        return "{'body': " + str(self.body) + ", 'head': " + str(self.head) + "}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def extract_atoms(self):
        atoms = []
        if self.head is not None:
            atoms.extend(self.head.extract_atoms())
        if self.body is not None:
            atoms.extend(self.body.extract_atoms())
        return atoms
