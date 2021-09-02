from conditions import *
from treetransform import *
from constants import *


# Given a boolean expression `cond(x)` and an integer function `f(x, y)`,
# checkClosure returns true if and only if `cond(f(x, y))` is true, i.e.
# that if x and y both meet the conditions in `cond`, that `f(x, y)` also
# meets the conditions in `cond`.
#
# The two kinds of conditions that are specifically checked are:
# 1. The sets of possible values that x % n can take, for 0 <= n < x, and:
# 2. The ranges [[b_1, t_1], [b_2, t_2], ..., [b_n, t_n]] that may contain x.
def checkClosure(cond, func):
    c = cond.simplify()
    f = func.simplify()

    xyModVals = getModVals(c)
    fModVals = inferModVals(f, xyModVals)

    # For each key i in the target mod vals, the inferred mod vals for i must
    # be a subset of the target mod vals.
    # For example, if the condition requires that x % i be equal to 0 or 1,
    # then the function must not allow x % i to be anything other than 0 or 1.
    if not checkMod(xyModVals, fModVals):
        return False

    ors = c.flatten()
    ranges = []
    bottoms = []
    tops = []
    for elt in ors:
        bottom = getBottom(elt)
        top = getTop(elt)
        ranges.append((bottom, top))
        bottoms.append(bottom)
        tops.append(top)
    badCond = getForbiddenRanges(bottoms, tops)
    allowedFunc = inferAllowedRanges(f, ranges)
    return checkRanges(badCond, allowedFunc)


# Given a `target` map of mod values that are required by a boolean condition,
# c(x), and an `inferred` map of mod values that are guaranteed by an integer
# function f(x, y), checkMod returns true if and only if, for each key k in
# `target`:
# 1. The key k is present in `inferred`, and:
# 2. The list inferred[k] is a subset of the list target[k]
def checkMod(target, inferred):
    for key in target:
        if key not in inferred:
            raise ValueError(
                "!!! Error: inferred mod vals  does not contain an entry for target key " + str(key), + " !!!")
            return False
        if not isSubset(inferred[key], target[key]):
            return False
    return True


# Given a list `targetForbidden` of ranges that are not allowed to contain
# a number, and a list `inferredAllowed` of ranges that may contain the
# number, checkRanges returns true if and only none of the allowed ranges
# overlap with any of the forbidden ranges.
def checkRanges(targetForbidden, inferredAllowed):
    for src in inferredAllowed:
        for dst in targetForbidden:
            if rangeOverlaps(src, dst):
                return False
    return True


###### Functions for computing target and inferred mod values ######


# Given a boolean expression `cond(x)`, getModVals returns a map
# n => [v_1, v_2, ... v_k] where each v_i is a possible number
# that x % n is allowed to be equal to.
def getModVals(cond):
    if isinstance(cond, And):
        l = getModVals(cond.left)
        r = getModVals(cond.right)
        return intersectMaps(l, r)
    if isinstance(cond, Or):
        l = getModVals(cond.left)
        r = getModVals(cond.right)
        return unionMaps(l, r)
    # x % i == j implies i => [j]
    elif isinstance(cond, Equal):
        i, j, exists = getModIJ(cond)
        if exists:
            return {i: [j]}
        else:
            return {}
    # x % i > j implies i => [j + 1, ..., i - 1]
    elif isinstance(cond, Greater):
        i, j, exists = getModIJ(cond)
        if exists:
            if i > j + 1:
                return {i: list(range(j + 1, i))}
            else:
                raise ValueError(
                    "!!! Invalid modulo greater operator: " + str(cond) + " !!!")
                return {}
        else:
            return {}
    # x % i >= j implies i => [j, ..., i - 1]
    elif isinstance(cond, Geq):
        i, j, exists = getModIJ(cond)
        if exists:
            return {i: list(range(j, i))}
        else:
            return {}
    # x % i < j implies i => [0, ..., j - 1]
    elif isinstance(cond, Less):
        i, j, exists = getModIJ(cond)
        if exists:
            return {i: list(range(0, j))}
        else:
            return {}
    # x % i <= j implies i => [0, ..., j]
    elif isinstance(cond, Leq):
        i, j, exists = getModIJ(cond)
        if exists:
            return {i: list(range(0, j + 1))}
        else:
            return {}
    else:
        return {}


# If `cond` is of the form x % i OP j, where OP is ==, >, >=, <, or <=
# and 0 <= j < i, then getModIJ returns (i, j, True).
# Otherwise, it returns (0, 0, False).
def getModIJ(cond):
    if not isinstance(cond, BinaryCondition):
        return 0, 0, False
    elif isinstance(cond.left, Mod):
        if isinstance(cond.left.left, X):
            rVal, rExists = cond.right.eval()
            if rExists and rVal >= 0:
                lVal, lExists = cond.left.right.eval()
                if lExists and rVal < lVal:
                    return lVal, rVal, True
    return 0, 0, False


# Given a function f(x, y) and a map of mod values that both x and y
# fulfill, return the map of modValues that f(x, y) fulfill.
def inferModVals(f, modVals):
    result = {}
    for key in modVals:
        result[key] = inferOneModVal(f, key, modVals[key])
    return result


# Given a function f(x, y), a number num, and a list vals of numbers
# that x % num and y % num can be equal to, return a list of numbers
# that f(x, y) % num can be equal to.
def inferOneModVal(f, num, vals):
    result = []
    for i in vals:
        for j in vals:
            n, exists = EvalTwoNums(i, j).transform(f).simplify().eval()
            if exists:
                result.append(n % num)
            else:
                raise ValueError("!!! Failed to evaluate " + str(f) +
                                 " with integers " + str(i) + " and " + str(j) + " !!!")
    return list(set(result))


###### Functions for computing target and inferred ranges ######


# Given a condition `c(x)`, getAllowedRanges returns the list of ranges
# that are allowed to contain x.
def getAllowedRanges(c):
    ranges = []
    ors = c.flatten()
    ranges = []
    bottoms = []
    tops = []
    for elt in ors:
        bottom = getBottom(elt)
        top = getTop(elt)
        ranges.append((bottom, top))
    return ranges


# Given a list `bottoms` of the minimum values that may contain a number
# and a list `tops` of the maximum values that may contain a number,
# getForbiddenRanges returns a list of ranges that are not allowed to
# contain the number.
def getForbiddenRanges(bottoms, tops):
    bottoms.sort()
    tops.sort()
    bad = []

    for index, t in enumerate(tops):
        if t == TOP:
            continue
        topVal = t + 1
        foundOverlap = False
        for overlapIndex, b in enumerate(bottoms):
            if b <= topVal:
                tCheck = tops[overlapIndex]
                if tCheck >= topVal:
                    foundOverlap = True
                    break
        if foundOverlap:
            continue
        options = [value for value in bottoms if value > topVal]
        minBottomGreaterThanTopVal = topVal
        if len(options) > 0:
            minBottomGreaterThanTopVal = min(options)
        bad.append((topVal, minBottomGreaterThanTopVal - 1))

    for index, b in enumerate(bottoms):
        if b == BOTTOM:
            continue
        bottomVal = b - 1
        foundOverlap = False
        for overlapIndex, t in enumerate(tops):
            if t >= bottomVal:
                bCheck = bottoms[overlapIndex]
                if bCheck <= bottomVal:
                    foundOverlap = True
                    break
        if foundOverlap:
            continue
        options = [value for value in tops if value < bottomVal]
        minTopLessThanBottomVal = BOTTOM - 1
        if len(options) > 0:
            minBottomLessThanBottomVal = min(options)
        bad.append((minTopLessThanBottomVal + 1, bottomVal))

    return bad


# Given a boolean expression `cond(x)`, getBottom returns the minimum value of x.
def getBottom(cond):
    eq, eqExists = getEqual(cond)
    if eqExists:
        return eq
    elif isinstance(cond, And):
        l = getBottom(cond.left)
        r = getBottom(cond.right)
        return max(l, r)
    elif isinstance(cond, Or):
        l = getBottom(cond.left)
        r = getBottom(cond.right)
        return min(l, r)
    elif isinstance(cond, Equal):
        return getRHSConst(cond, BOTTOM)
    elif isinstance(cond, Greater):
        c = getRHSConst(cond, BOTTOM)
        if c == BOTTOM:
            return c
        else:
            return c + 1
    elif isinstance(cond, Geq):
        return getRHSConst(cond, BOTTOM)
    elif isinstance(cond, Less):
        return BOTTOM
    elif isinstance(cond, Leq):
        return BOTTOM
    else:
        return BOTTOM


# Given a boolean expression `cond(x)`, getTop returns the maximum value of x.
def getTop(cond):
    eq, eqExists = getEqual(cond)
    if eqExists:
        return eq
    elif isinstance(cond, And):
        l = getTop(cond.left)
        r = getTop(cond.right)
        return min(l, r)
    elif isinstance(cond, Or):
        l = getTop(cond.left)
        r = getTop(cond.right)
        return max(l, r)
    elif isinstance(cond, Equal):
        return getRHSConst(cond, TOP)
    elif isinstance(cond, Greater):
        return TOP
    elif isinstance(cond, Geq):
        return TOP
    elif isinstance(cond, Less):
        c = getRHSConst(cond, TOP)
        if c == TOP:
            return c
        else:
            return c - 1
    elif isinstance(cond, Leq):
        return getRHSConst(cond, TOP)
    else:
        return TOP


# Given a boolean expression `cond(x)`, if `cond` implies that x must be equal
# to a number n, getEqual returns (n, True). Otherwise, it returns (0, False).
def getEqual(cond):
    if isinstance(cond, And):
        l, lExists = getEqual(cond.left)
        r, rExists = getEqual(cond.right)
        if lExists and rExists:
            if l == r:
                return l, True
            else:
                raise ValueError(
                    "!!! Error: conflicting equality values " + str(l) + " and " + str(r) + " !!!")
                return 0, False
        elif lExists:
            return l, True
        elif rExists:
            return r, True
        return 0, False
    elif isinstance(cond, Or):
        l, lExists = getEqual(cond.left)
        r, rExists = getEqual(cond.right)
        if lExists and rExists:
            if l == r:
                return l, True
            else:
                return 0, False
        return 0, False
    elif isinstance(cond, Equal):
        eq = getRHSConst(cond, TOP)
        return eq, eq != TOP
    else:
        return 0, False


# Given a boolean expression `cond(x)` and a number `default`, if `cond`
# is of the form x OP val, where OP is ==, <, >, <=, or >= and val is an
# integer constant, getRHSConst returns (val, True). Otherwise it returns
# (default, False).
def getRHSConst(cond, default):
    if isinstance(cond, BinaryCondition):
        if isinstance(cond.left, X):
            rVal, rExists = cond.right.eval()
            if rExists:
                return rVal
    return default


# Given a function `f(x, y)` and a list allowedRanges of the ranges that
# may contain x and y, inferAllowedRanges returns a list of the ranges
# that may contain `f(x, y)`.
def inferAllowedRanges(f, allowedRanges):
    allowed = []
    val, exists = f.eval()
    if exists:
        allowed.append((val, val))
    elif isinstance(f, X) or isinstance(f, Y):
        return allowedRanges
    elif isinstance(f, Add):
        left = inferAllowedRanges(f.left, allowedRanges)
        right = inferAllowedRanges(f.right, allowedRanges)
        for l in left:
            for r in right:
                bb = l[0] + r[0]
                tt = l[1] + r[1]
                allowed.append((bb, tt))
    elif isinstance(f, Sub):
        left = inferAllowedRanges(f.left, allowedRanges)
        right = inferAllowedRanges(f.right, allowedRanges)
        for l in left:
            for r in right:
                bb = l[0] - r[0]
                bt = l[0] - r[1]
                tb = l[1] - r[0]
                tt = l[1] - r[1]
                vals = [bb, bt, tb, tt]
                allowed.append((min(vals), max(vals)))
    elif isinstance(f, Mult):
        left = inferAllowedRanges(f.left, allowedRanges)
        right = inferAllowedRanges(f.right, allowedRanges)
        for l in left:
            for r in right:
                bb = l[0] * r[0]
                bt = l[0] * r[1]
                tb = l[1] * r[0]
                tt = l[1] * r[1]
                vals = [bb, bt, tb, tt]
                allowed.append((min(vals), max(vals)))
    elif isinstance(f, Minus):
        child = inferAllowedRanges(f.child, allowedRanges)
        for c in child:
            allowed.append((-c[1], -c[0]))
    elif isinstance(f, Div):
        left = inferAllowedRanges(f.left, allowedRanges)
        right = inferAllowedRanges(f.right, allowedRanges)
        for l in left:
            for r in right:
                vals = []
                if r[0] != 0:
                    vals.append(int(l[0] / r[0]))
                    vals.append(int(l[1] / r[0]))
                if r[1] != 0:
                    vals.append(int(l[0] / r[1]))
                    vals.append(int(l[1] / r[1]))
                allowed.append((min(vals), max(vals)))
    else:
        allowed.append((BOTTOM, TOP))
    return allowed


###### Helper functions ######


# Returns true if there is any overlap between the src and dst ranges,
# i.e. if any number allowed in the src range is also allowed in the dst range
# or vice versa.
def rangeOverlaps(src, dst):
    return numInRange(src[0], dst) or numInRange(src[1], dst) or numInRange(dst[0], src) or numInRange(dst[1], src)


# Returns true if the number num is within the range r.
def numInRange(num, r):
    bottom = r[0]
    top = r[1]
    if bottom <= BOTTOM or num >= bottom:
        if top >= TOP or num <= top:
            return True
    return False


# Returns a map of number => list of numbers where,
# for each key k that is present in both maps l and r:
# result[k] = l[key] intersect r[key]
def intersectMaps(l, r):
    result = {}
    for key in l:
        if key in r.keys():
            result[key] = intersectLists(l[key], r[key])
        else:
            result[key] = l[key]
    for key in r:
        if key not in l.keys():
            result[key] = r[key]
    return result


# Returns the intersection of the lists of numbers l and r.
def intersectLists(l, r):
    result = [value for value in l if value in r]
    return result


# Returns a map of number => list of numbers, where,
# for each key k that is present in l or r:
# result[k] = l[k] union r[k]
def unionMaps(l, r):
    result = {}
    for key in l:
        if key in r.keys():
            result[key] = unionLists(l[key], r[key])
        else:
            result[key] = l[key]
    for key in r:
        if key not in r.keys():
            result[key] = r[key]
    return result


# Returns the union of the lists of numbers l and r.
def unionLists(l, r):
    result = [value for value in l] + [value for value in r if value not in l]
    return result


# Returns true if every number in l is also present in r.
def isSubset(l, r):
    for val in l:
        if val not in r:
            return False
    return True


# Evaluate a function(x, y) given two numerical values i and j for x and y.
class EvalTwoNums(TreeTransform):
    def __init__(self, i, j):
        super().__init__()
        self.i = Num(i)
        self.j = Num(j)

    def transformX(self, expr):
        return self.i

    def transformY(self, expr):
        return self.j
