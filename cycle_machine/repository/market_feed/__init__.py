from cycle_machine.repository import Repository


class MarketFeed:
    def __init__(self, repository: Repository):
        self.repository = repository


