import antlr4
import logging

from proplanguage import Atom, Literal, ExtLiteral, Formula, Operator, Rule
from gen.LparseInputLexer import LparseInputLexer
from gen.LparseInputListener import LparseInputListener
from gen.LparseInputParser import LparseInputParser

logging.basicConfig(filename='LparseInputLoaderListener.log', filemode='w', level=logging.INFO)

class LparseInputLoaderListener(LparseInputListener):

    def __init__(self):
        self.decorations = {}
        self.ruleList = []

    def exitPos_literal(self, ctx):
        if ctx.predicate().IDENTIFIER():
            atom = Atom(name=ctx.predicate().IDENTIFIER().getText())
            self.decorations[ctx] = atom
            logging.info("captured pos literal: " + str(atom))
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

    def exitLiteral(self, ctx):
        atom = self.decorations[ctx.pos_literal()]
        literal = Literal(
            atom=atom,
            neg=(ctx.MINUS())
        )
        self.decorations[ctx] = literal
        logging.info("captured literal: " + str(literal))

    def exitExt_literal(self, ctx):
        literal = self.decorations[ctx.literal()]
        extliteral = ExtLiteral(
            literal=literal,
            naf=(ctx.NOT())
        )
        self.decorations[ctx] = extliteral
        logging.info("captured ext literal: " + str(extliteral))

    def exitList_literals(self, ctx):
        literal_list = []

        if ctx.literal():
            # for generality, we store ExtLiterals in the list, rather than Literals
            literal = ExtLiteral(
                literal=self.decorations[ctx.literal()],
                naf=False
            )
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        literal_list.append(literal)

        if ctx.list_literals():
            literal_list = literal_list + self.decorations[ctx.list_literals()]

        self.decorations[ctx] = literal_list
        logging.info("captured (ext) literal list: " + str(literal_list))

    def exitList_ext_literals_expressions(self, ctx):
        formula_list = []

        if ctx.ext_literal():
            ext_literal = self.decorations[ctx.ext_literal()]
            formula = Formula(
                operator=Operator.NONE,
                inputTerms=[ext_literal]
            )
            formula_list.append(formula)
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        if ctx.list_ext_literals_expressions():
            formula_list = formula_list + self.decorations[ctx.list_ext_literals_expressions()]

        self.decorations[ctx] = formula_list
        logging.info("captured (ext literal list) formula list: " + str(formula_list))

    def exitChoice(self, ctx):
        literal_list = self.decorations[ctx.list_literals]
        if not ctx.minchoice:
            l = ctx.minchoice.getText()
        else:
            l = 0

        if not ctx.maxchoice:
            r = ctx.maxchoice.getText()
        else:
            r = len(literal_list)

        if l == len(literal_list) and l == r:
            operator = Operator.AND
        elif l == 1 and r == len(literal_list):
            operator = Operator.OR
        elif l == 1 and r == 1:
            operator = Operator.XOR
        else:
            operator = Operator.CHOICE

        formula = Formula(
            operator=operator,
            inputTerms=literal_list        # should be ExtLiterals !!!
        )

        self.decorations[ctx] = formula
        logging.info("captured choice formula: " + str(formula))

    def exitHead(self, ctx):
        if ctx.literal():
            extliteral = ExtLiteral(
                literal=self.decorations[ctx.literal()],
                naf=False
            )
            formula = Formula(
                operator=Operator.NONE,
                inputTerms=[extliteral]
            )
        elif ctx.choice():
            formula = self.decorations[ctx.choice()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        self.decorations[ctx] = formula
        logging.info("captured head formula: " + str(formula))

    def exitBody(self, ctx):
        if ctx.list_ext_literals_expressions():
            formula_list = self.decorations[ctx.list_ext_literals_expressions()]
            formula = Formula(
                operator=Operator.AND,
                inputFormulas=formula_list
            )
        elif ctx.choice():
            formula = self.decorations[ctx.choice()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        self.decorations[ctx] = formula
        logging.info("captured body formula: " + str(formula))

    def exitConstraint(self, ctx):
        if ctx.body():
            body = self.decorations[ctx.body()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        rule = Rule(body=body)

        self.decorations[ctx] = rule
        logging.info("captured constraint: :- " + str(rule))
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

        logging.info("captured normal rule: " + str(head) + ":-" + str(body))
        self.decorations[ctx] = Rule(head = head, body = body)

    def exitAsprule(self, ctx):
        if ctx.constraint():
            rule = self.decorations[ctx.constraint()]
        elif ctx.normrule():
            rule = self.decorations[ctx.normrule()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        logging.info("captured asp rule: " + str(rule))
        self.decorations[ctx] = rule
        self.ruleList.append(rule)

    def exitAspfact(self, ctx):
        if ctx.head():
            head = self.decorations[ctx.head()]
        else:
            raise ValueError("Unexpected element in " + ctx.getText())

        rule = Rule(head = head)

        logging.info("captured asp fact: " + str(rule))
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
    ruleList = parseString("b :- a, b. c :- a.")
    for rule in ruleList:
        print str(rule)


