class IndexError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        
        
class SearchError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        
        
class SearchDatasetError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        
class AnswerError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        
        
class AnswerDatasetError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        
class EvaluateError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        
__all__ = ['IndexError',
           'SearchError',
           'SearchDatasetError',
           'AnswerError',
           'AnswerDatasetError',
           'EvaluateError'
           ]