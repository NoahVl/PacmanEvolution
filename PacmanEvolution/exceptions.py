"""
This file contains pre-defined exceptions (errors) that can be raised under certain conditions.
"""


class EmptyAssignmentError(NotImplementedError):
    def __init__(self, s='this code needs to be filled in to pass the assignment'):
        super().__init__(s)


class EmptyBonusAssignmentError(EmptyAssignmentError):
    def __init__(self, s='this code may be filled in for bonus points'):
        super().__init__(s)
