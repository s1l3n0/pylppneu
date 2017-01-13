import proplanguage
from LparseLoader import parseString


class Vertex:
    # -- Fields --
    # name
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Edge:
    # -- Fields --
    # source
    # target
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class DependencyGraph:
    # -- Fields --
    # rule_list
    # vertices
    # positive_edges
    # negative_edges

    def __init__(self, rule_list=()):
        self.rule_list = rule_list
        self.vertices = []
        self.pos_edges = []
        self.neg_edges = []

        atoms = []
        for rule in rule_list:
            for atom in rule.extract_atoms():
                if atom not in atoms:
                    atoms.append(atom)

        for atom in atoms:
            self.vertices.append(Vertex(atom))

        for rule in rule_list:
            print rule.head.extract_pos_literals()
            print rule.body
            print rule.body.extract_pos_literals()
            print rule.body.extract_neg_literals()
            for source in rule.head.extract_pos_literals():
                for target in rule.body.extract_pos_literals():
                    self.pos_edges.append(Edge(source, target))
                for target in rule.body.extract_neg_literals():
                    self.neg_edges.append(Edge(source, target))

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


if __name__ == '__main__':
    rule_list = parseString("b :- a, b. c :- a.")
    dependency_graph = DependencyGraph(rule_list)
    print str(dependency_graph)
