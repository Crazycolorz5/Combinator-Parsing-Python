
# The class
class Parser:
    def __init__(self, tryParse): #tryParse :: source -> (source', out)
        self.tryParse = tryParse
        
    def parse(self, inStream):
        res = self.tryParse(inStream)
        if res is None:
            return None
        else:
            return res[1]
    
    def bind(self, parserFunc):
        def bindTryParse(a):
            res = self.tryParse(a)
            if res is None:
                return None
            else:
                return parserFunc(res[1]).tryParse(res[0])
        return Parser(bindTryParse)
    
    def bind_(self, parser):
        return self.bind(lambda x: parser)

    def fmap(self, func):
        def fmapTryParse(inStream):
            x = self.tryParse
            if x is None:
                return None
            else:
                return (x[0], func(x[1]))
        return Parser(fmapTryParse)
    
    @staticmethod
    def guard(b):
        return emptyParse if b else failParse
    
    @staticmethod
    def ret(val):
        return Parser(lambda x: (x, val))

# The basic combinators
def sumParser(parser1, parser2):
    def sumTryParse(inStream):
        res = parser1.tryParse(inStream)
        if res is None:
            return parser2.tryParse(inStream)
        else:
            return res
    return Parser(sumTryParse)

def prodParser(parser1, parser2):
    def prodTryParse(inStream):
        res1 = parser1.tryParse(inStream)
        if res1 is None:
            return None
        else:
            res2 = parser2.tryParse(res1[0])
            return (res2[0], (res1[1], res2[1]))
    return Parser(prodTryParse)
        
# Greedy Kleene star. Parses as many of its input as possible before returning.
def kleeneStar(parser):
    def kleeneTryParse(inStream):
        res = parser.tryParse(inStream)
        if res is None:
            return (inStream, ())
        else:
            res_inner = kleeneTryParse(res[0])
            if res_inner is None:
                return (res[0], (res[1],))
            else:
                return (res_inner[0], (res[1],) + res_inner[1])
    return Parser(kleeneTryParse)

# Some basic building blocks
emptyParse = Parser.ret(())
failParse = Parser(lambda x: None)
parseAnyElem = Parser(lambda x: None if len(x) == 0 else (x[1:], x[0]))
parseElem = lambda c: parseAnyElem.bind(
    lambda e: Parser.guard(e == c).bind_(
    Parser.ret(e)))
