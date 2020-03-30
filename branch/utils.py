def contains(list, predicate):
    return find(list, predicate) and True or False

def find(list, predicate, default=None):
    for element in list:
        if predicate(element):
            return element
    return default

def map(list, operator):
    return [ operator(element) for element in list ]