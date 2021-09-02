from conditions import *
from treetransform import *


# Given a boolean expression `cond(x)` and an integer function `f(x, y`),
# if there exists an integer-constant expression e that such that:
# 1. cond(e) == True, and:
# 2. f(x, e) == f(e, x) == x for all x,
# then checkIdentity returns (e, True). Otherwise, it returns (Num(0), False).
def checkIdentity(cond, func):
    fBA = EvalA_B(b, a).transform(func)
    testBA = Equal(fBA, B()).simplify()
    fAB = EvalA_B(a, b).transform(func)
    testAB = Equal(fAB, B()).simplify()

    solvedBA, existsBA = testBA.solve()
    solvedAB, existsAB = testAB.solve()

    if existsBA and existsAB:
        if isinstance(solvedBA.right, Num) and isinstance(solvedAB.right, Num) and solvedBA.right.value == solvedAB.right.value:
            identity = solvedBA.right
            # Check if the proposed identity (Num expression) fulfills the condition:
            # If we replace x with the identity and evaluate the condition,
            # the boolean result must be true.
            # For example, if the condition is x >= 0 && x % 2 == 1, and the proposed
            # identity is 1, evaluating 1 >= 0 && 1 % 2 == 1 results in true.
            c = EvalIdentity(identity).transform(cond)
            c = c.simplify()
            isInGroup = c.eval()
            if c.eval():
                return identity, True
    return Num(0), False


# Replace x with a and y with b.
class EvalA_B(TreeTransform):
    def __init__(self, xVar, yVar):
        super().__init__()
        if xVar == a:
            self.xVar = A()
        elif xVar == b:
            self.xVar = B()
        if yVar == a:
            self.yVar = A()
        if yVar == b:
            self.yVar = B()

    def transformX(self, expr):
        return self.xVar

    def transformY(self, expr):
        return self.yVar


# Replace x with the given number.
# Intended to be applied to a boolean condition.
class EvalIdentity(TreeTransform):
    def __init__(self, num):
        super().__init__()
        self.num = num

    def transformX(self, expr):
        return self.num
