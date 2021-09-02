from treetransform import *


# Given an integer function f(x, y), checkAssoc returns true if and only if
# f(f(a, b), c) == f(a, f(b, c)).
def checkAssoc(func):
    left = leftAssoc(func)
    right = rightAssoc(func)
    l = left.simplify()
    r = right.simplify()
    cmp = l.compare(r)
    sign = "is equal to"
    if cmp == -1:
        sign = "is greater than"
    elif cmp == 1:
        sign = "is less than"
    return cmp == 0


# Replace x with the given xExpr (e.g. replace x with f(a, b))
# and replace y with the given yExpr (e.g. replace y with c).
class AssocTransform(TreeTransform):
    def __init__(self, xExpr, yExpr):
        super().__init__()
        self.xExpr = xExpr
        self.yExpr = yExpr

    def transformX(self, expr):
        return self.xExpr

    def transformY(self, expr):
        return self.yExpr


# Given an integer function f(x, y), leftAssoc returns f(f(a, b), c).
def leftAssoc(expr):
    fAB = EvalTwoExprs(A(), B()).transform(expr)
    fAB_C = EvalTwoExprs(fAB, C()).transform(expr)
    return fAB_C


# Given an integer function f(x, y), leftAssoc returns f(a, f(b, c)).
def rightAssoc(expr):
    fBC = AssocTransform(B(), C()).transform(expr)
    fA_BC = EvalTwoExprs(A(), fBC).transform(expr)
    return fA_BC
