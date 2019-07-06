stdEntry = {
    'from': '',
    'to': '',
    'from_key': '',
    'to_key': '',
    'connections': {}
}


class RainFieldGraph:
    def __init__(self):
        self.from_tos = []

    def connectionExists(self, rf):
        return(rf.key in [entry.from_key for entry in self.from_tos])
