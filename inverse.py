from conditions import *
from treetransform import *
from closure import *


# Given a boolean expression cond(x), an integer function f(x, y), and an
# integer-constant expression `identity`, if for each integer a there exists
# an integer function g(a) such that:
# 1. cond(g(a)) == True, and:
# 2. f(a, g(a)) == f(g(a), a) == a
# then checkInverse return (g, True). Otherwise, it returns (Num(0), False).
def checkInverse(cond, func, identity):
    c = cond.simplify()
    f = func.simplify()
    fBA = EvalTwoExprs(B(), A()).transform(f).simplify()
    testBA = Equal(fBA, identity).simplify()
    fAB = EvalTwoExprs(A(), B()).transform(f).simplify()
    testAB = Equal(fAB, identity).simplify()

    solvedBA, existsBA = testBA.solve()
    solvedAB, existsAB = testAB.solve()

    if existsBA and existsAB and solvedBA.right.compare(solvedAB.right) == 0:
        inverse = EvalInverse().transform(solvedBA.right)
        if checkClosure(c, inverse):
            return PrettyInverse().transform(inverse), True

    return Num(0), False


# Replace b with y.
class EvalInverse(TreeTransform):
    def __init__(self):
        super().__init__()

    def transformB(self, expr):
        return Y()


# Replace y with x.
class PrettyInverse(TreeTransform):
    def __init__(self):
        super().__init__()

    def transformY(self, expr):
        return X()
