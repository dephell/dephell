
class UnknownLink:
    def __init__(self, link):
        self.short = link.split('#')[0]
        self.long = link

    def __str__(self):
        return self.long
