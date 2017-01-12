import pprint
import antlr4
from proplanguage import Atom, Literal, ExtLiteral, Formula, Operator, Rule
from LparseInputLexer import LparseInputLexer
from LparseInputListener import LparseInputListener
from LparseInputParser import LparseInputParser


class LparseInputLoaderListener(LparseInputListener):

    def __init__(self):
        self.decorations = {}
        self.ruleList = []

    def exitPos_literal(self, ctx):
        if (ctx.predicate().IDENTIFIER()):
            self.decorations[ctx] = Atom(name = ctx.predicate().IDENTIFIER().getText())
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

    def exitLiteral(self, ctx):
        atom = self.decorations[ctx.pos_literal()]
        self.decorations[ctx] = Literal(
            atom = atom,
            neg = (ctx.MINUS())
        )

    def exitExt_literal(self, ctx):
        literal = self.decorations[ctx.literal()]
        self.decorations[ctx] = ExtLiteral(
            literal = literal,
            naf=(ctx.NOT())
        )

    def exitList_literals(self, ctx):
        literalList = []

        if (ctx.literal()):
            # for generality, we store ExtLiterals in the list, rather than Literals
            literal = ExtLiteral(
                literal = self.decorations[ctx.literal()],
                naf = False
            )
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        literalList.append(literal)

        if (ctx.list_literals()):
            literalList = literalList + self.decorations[ctx.list_literals()]

        self.decorations[ctx] = literalList

    def exitList_ext_literals_expressions(self, ctx):
        formulaList = []

        if (ctx.ext_literal()):
            extLiteral = self.decorations[ctx.ext_literal()]
            formula = Formula(
                operator=Operator.POS,
                inputTerms=(extLiteral)
            )
            formulaList.append(formula)
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        if (ctx.list_ext_literals_expressions()):
            formulaList = formulaList + self.decorations[ctx.list_ext_literals_expressions()]

        self.decorations[ctx] = formulaList

    def exitChoice(self, ctx):
        literalList = self.decorations[ctx.list_literals]
        if not ctx.minchoice:
            l = ctx.minchoice.getText()
        else:
            l = 0

        if not ctx.maxchoice:
            r = ctx.maxchoice.getText()
        else:
            r = len(literalList)

        if l == len(literalList) and l == r:
            operator = Operator.AND
        elif l == 1 and r == len(literalList):
            operator = Operator.OR
        elif l == 1 and r == 1:
            operator = Operator.XOR
        else:
            operator = Operator.CHOICE

        formula = Formula(
            operator = operator,
            inputTerms = literalList        # should be ExtLiterals !!!
        )

    def exitHead(self, ctx):
        if ctx.literal():
            literal = self.decorations[ctx.literal()]
            formula = Formula(
                operator = Operator.POS,
                inputTerms = (literal)
            )
        elif ctx.choice():
            formula = self.decorations[ctx.choice()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        self.decorations[ctx] = formula

    def exitBody(self, ctx):
        if ctx.list_ext_literals_expressions():
            formulaList = self.decorations[ctx.list_ext_literals_expressions()]
            formula = Formula(
                operator = Operator.AND,
                inputFormulas = formulaList
            )
        elif ctx.choice():
            formula = self.decorations[ctx.choice()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        self.decorations[ctx] = formula

    def exitConstraint(self, ctx):
        if ctx.body():
            body = self.decorations[ctx.body()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        rule = Rule(body = body)

        self.decorations[ctx] = rule
        self.ruleList.append(rule)

    def exitNormrule(self, ctx):
        if ctx.head():
            head = self.decorations[ctx.head()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        if ctx.body():
            body = self.decorations[ctx.body()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        self.decorations[ctx] = Rule(head = head, body = body)

    def exitAsprule(self, ctx):
        if ctx.constraint():
            rule = self.decorations[ctx.constraint()]
        elif ctx.normrule():
            rule = self.decorations[ctx.normrule()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        self.decorations[ctx] = rule
        self.ruleList.append(rule)

    def exitAspfact(self, ctx):
        if ctx.head():
            head = self.decorations[ctx.head()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        rule = Rule(head = head)

        self.decorations[ctx] = rule
        self.ruleList.append(rule)

def parseString(code):
    return parse(antlr4.InputStream(code))

def parse(inputstream):
    lexer = LparseInputLexer(inputstream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = LparseInputParser(stream)
    tree = parser.program()
    loader = LparseInputLoaderListener()
    walker = antlr4.ParseTreeWalker()
    walker.walk(loader, tree)
    return loader.ruleList

if __name__ == '__main__':
    ruleList = parseString("b :- a. c :- a.")
    for rule in ruleList:
        print str(rule)


