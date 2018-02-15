
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
        
    def __call__(self, inStream):
        return self.parse(inStream)
    
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
            x = self.tryParse(inStream)
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
    return parser1.bind(lambda res1: parser2.bind(lambda res2: Parser.ret((res1, res2))))
        
# Parses as many of its input as possible that still allow the next parser to parse.
def kleeneStarThen(parser, thenParser):
    innerThenParser = thenParser.fmap(lambda x: ((), x))
    def kleeneTryParse(inStream):
        print(inStream)
        res = parser.tryParse(inStream)
        if res is None:
            return innerThenParser.tryParse(inStream)
        else:
            res_inner = kleeneTryParse(res[0])
            if res_inner is None:
                return innerThenParser.tryParse(inStream)
            else:
                (kleenePart, thenPart) = res_inner[1]
                return (res_inner[0], ((res[1],) + kleenePart, thenPart))
    return Parser(kleeneTryParse)

kleeneStar = lambda parser: kleeneStarThen(parser, emptyParse).fmap(lambda x: x[0])

# Some basic building blocks
emptyParse = Parser.ret(())
failParse = Parser(lambda x: None)
parseAnyElem = Parser(lambda x: None if len(x) == 0 else (x[1:], x[0]))
parseElemPred = lambda predicate: parseAnyElem.bind(
    lambda e: Parser.guard(predicate(e)).bind_(
              Parser.ret(e)))
parseElem = lambda c: parseElemPred(lambda e: e==c)
