
# The class
class Parser:
    def __init__(self, tryParse): #tryParse :: source -> (source', out)
        self.tryParse = tryParse
        
    def parse(self, in):
        res = self.tryParse(in)
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
        return Parser(bindTryFunc)
    
    @staticmethod
    def guard(b):
        return emptyParse if b else failParse
    
    @staticmethod
    def ret(val):
        return Parser(lambda x: (x, val))

# The basic combinators
def sumParser(parser1, parser2):
    def sumTryParse(in):
        res = parser1.tryParse(in)
        if res is None:
            return parser2.tryParse(in)
        else:
            return res
    return Parser(sumTryParse)

def prodParser(parser1, parser2):
    def prodTryParse(in):
        res1 = parser1.tryParse(in)
        if res1 is None:
            return None
        else:
            res2 = parser2.tryParse(res1[0])
            return (res2[0], (res1[1], res2[1]))
    return Parser(prodTryParse):
        
# Kleene star
def kleeneStar(parser):
    def kleeneTryParse(in):
        res = parser.tryParse(in)
        if res is None:
            return ()
        else:
            res_inner = kleeneTryParse(res[0])
            return (res_inner[0], res[1] + res_inner[1])
    return Parser(kleeneTryParse)

# Some basic building blocks
emptyParse = Parser.ret(())
failParse = Parser(lambda x: None)
parseAnyElem = Parser(lambda x: None if length(x) == 0 else (x[1:], x[0]))
parseElem = lambda c: parseAnyElem.bind(lambda e: Parser.guard(e == c).bind(Parser.ret(e)))
