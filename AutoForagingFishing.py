# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 17:38:33 2022
Automatic questing for foraging and fishing
@author: Gok
"""
import time
from itertools import chain
from UserWeb3 import UserWeb3

class FastQuest(UserWeb3):
    
    def __init__(self, user):
        UserWeb3.__init__(self, user)
        self.MAX_QUESTERS = 6
        self.MAX_ATTEMPTS = 5

    def complete_all_quest(self):
        # Get the current quests.
        quests_df = self.get_current_quests()

        if quests_df is not None:
            # Format the time to know when is the completion time of the quests.
            quests_df['current_time'] = time.time()

            # Look which quest are already done.
            isDone = (quests_df['current_time'] - quests_df["completed_time"]) > 0

            if isDone.any():
                # Complete the quests that are done.
                for heroes in quests_df.loc[isDone, "heroes"].values:
                    tx_receipt = self.quest_routine(heroes, "complete")       

    def start(self, profession):
        # Get current quests.
        quests_df = self.get_current_quests()
        
        if quests_df is not None:
            # Only keep profession quest.
            quests_df = quests_df.loc[quests_df.quest_type == profession, :]
        
        # Load the hero data to know the stamina of heroes.
        hero_data = self.get_heroes_data()
        
        # If heroes are already questing, take them out of the hero_data.
        if quests_df is not None:
            areQuesting = list(chain.from_iterable(quests_df.heroes.tolist()))
            hero_data = hero_data.loc[~hero_data.id.isin(areQuesting), :]
        
        # Look which heroes have more or exactly 25 stamina.
        isReady = hero_data.current_stamina > 24
        
        # Find gangs.
        isProfession = hero_data.profession == profession
        hero_ids = hero_data.loc[isReady & isProfession, 'id'].tolist()
            
        if hero_ids:
            # Split the list in <max_questers>.
            iterable = range(0, len(hero_ids), self.MAX_QUESTERS)
            gangs = [hero_ids[x:x+self.MAX_QUESTERS] for x in iterable]
                
            # Loop through the gang and send them questing.
            for g in gangs:
                # Start quests.
                tx_receipt = self.quest_routine(g, "start", profession, self.MAX_ATTEMPTS)
