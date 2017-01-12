import pprint


class Atom:
    # -- Fields --
    # name : String
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

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
        return prefix + str(self.atom)

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
        return prefix + str(self.literal)

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
            output = output + "'inputFormulas': ["
            for inputFormula in self.inputFormulas:
                output = output + str(inputFormula) + ", "
            output = output[:-2] + "]"
        elif len(self.inputTerms) > 0:
            output = output + "'inputTerms': ["
            for inputTerm in self.inputTerms:
                output = output + str(inputTerm) + ", "
            output = output[:-2] + "]"
        return output + "}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class Operator:
    POS = 1
    NEG = 2
    NAF = 3
    AND = 4
    OR = 5
    XOR = 6
    IF = 7
    CHOICE = 8

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
