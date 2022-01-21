from automatic_questing.AutoForagingFishing import FastQuest
from automatic_questing.AutoMiningGardening import SlowQuest


class Job:
    def __init__(self, config, user):
        self.config = config
        self.user = user
        self.fast = FastQuest(self.config, self.user)
        self.slow = SlowQuest(self.config, self.user)

    def run(self):
        self.fast.complete_all_quest()
        self.slow.complete_all_quest()
        self.slow.start("mining")
        self.slow.start("gardening")
        self.fast.start("fishing")
        self.fast.start("foraging")
