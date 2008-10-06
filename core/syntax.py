class Operator(object):
    def __init__(self, constant, arity, associativity, precedence):
        self.name = constant.name
        self.token = self.name.upper()
        if self.token == '=':
            self.token = 'EQUALS'
        self.constant = constant
        self.arity = arity
        self.associativity = associativity
        self.precedence = precedence

class Binder(object):
    def __init__(self, constant):
        self.name = constant.name
        self.token = self.name.upper()
        self.constant = constant

class Type(object):
    def __init__(self, constructor, name):
        self.name = name
        self.token = self.name.upper()
        self.constructor = constructor
        
class Syntax(object):
    def __init__(self, words=[]):
        self._words = {}
        for word in words:
            self._words[word.name] = word

    def _add_word(self, word):
        self._words[word.name] = word
        
    def add_operator(self, constant, arity, associativity):
        self._add_word(Operator(constant, arity, associativity))
        
    def add_binder(self, constant):
        self._add_word(Binder(constant))

    def add_type(self, constant, name):
        self._add_word(Type(constant, name))

    def _filter_class(self, cls):
        return [word for word in self.words() if isinstance(word, cls)]
                
    def binders(self):
        return self._filter_class(Binder)

    def types(self):
        return self._filter_class(Type)

    def operators(self):
        return self._filter_class(Operator)

    def names(self):
        return self._words.keys()

    def words(self):
        return self._words.values()

    def __getitem__(self, key):
        return self._words[key]
