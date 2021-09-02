from conditions import *


# TreeTransform can be used to replace occurrences of expressions within
# a boolean condition or an integer function with other expressions.
# Subclasses of TreeTransform can override transform* methods to make these
# replacements.
class TreeTransform:
    def __init__(self):
        pass

    def transform(self, expr):
        if isinstance(expr, All):
            return self.transformAll(expr)
        elif isinstance(expr, Empty):
            return self.transformEmpty(expr)
        elif isinstance(expr, And):
            return self.transformAnd(expr)
        elif isinstance(expr, Or):
            return self.transformOr(expr)
        elif isinstance(expr, Equal):
            return self.transformEqual(expr)
        elif isinstance(expr, Greater):
            return self.transformGreater(expr)
        elif isinstance(expr, Geq):
            return self.transformGeq(expr)
        elif isinstance(expr, Less):
            return self.transformLess(expr)
        elif isinstance(expr, Leq):
            return self.transformLeq(expr)
        elif isinstance(expr, Add):
            return self.transformAdd(expr)
        elif isinstance(expr, Sub):
            return self.transformSub(expr)
        elif isinstance(expr, Mult):
            return self.transformMult(expr)
        elif isinstance(expr, Minus):
            return self.transformMinus(expr)
        elif isinstance(expr, Mod):
            return self.transformMod(expr)
        elif isinstance(expr, A):
            return self.transformA(expr)
        elif isinstance(expr, B):
            return self.transformB(expr)
        elif isinstance(expr, C):
            return self.transformC(expr)
        elif isinstance(expr, X):
            return self.transformX(expr)
        elif isinstance(expr, Y):
            return self.transformY(expr)
        elif isinstance(expr, Num):
            return self.transformNum(expr)
        else:
            raise ValueError("Unexpected expression " + str(expr))

    def transformAll(self, expr):
        return All()

    def transformEmpty(self, expr):
        return Empty()

    def transformAnd(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return And(l, r)

    def transformOr(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Or(l, r)

    def transformEqual(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Equal(l, r)

    def transformGreater(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Greater(l, r)

    def transformGeq(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Geq(l, r)

    def transformLess(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Less(l, r)

    def transformLeq(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Leq(l, r)

    def transformAdd(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Add(l, r)

    def transformSub(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Sub(l, r)

    def transformMult(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Mult(l, r)

    def transformMinus(self, expr):
        c = self.transform(expr.child)
        return Minus(c)

    def transformMod(self, expr):
        l = self.transform(expr.left)
        r = self.transform(expr.right)
        return Mod(l, r)

    def transformA(self, expr):
        return A()

    def transformB(self, expr):
        return B()

    def transformC(self, expr):
        return C()

    def transformX(self, expr):
        return X()

    def transformY(self, expr):
        return Y()

    def transformNum(self, expr):
        return Num(expr.value)


# Replace occurrences of x and y in an integer function f(x, y) with the
# given `xExpr` and `yExpr`.
class EvalTwoExprs(TreeTransform):
    def __init__(self, xExpr, yExpr):
        super().__init__()
        self.xExpr = xExpr
        self.yExpr = yExpr

    def transformX(self, expr):
        return self.xExpr

    def transformY(self, expr):
        return self.yExpr
