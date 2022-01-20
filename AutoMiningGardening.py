# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 17:37:45 2022
Automatic questing for mining and gardening quest (only mining)
@author: Gok
"""
import time
from itertools import chain
from UserWeb3 import UserWeb3

class SlowQuest(UserWeb3):
    
    def __init__(self, user, blocks = 16):
        UserWeb3.__init__(self, user)
        self.blocks = blocks if blocks == "MAX" else int(blocks)
        
    def complete_all_quest(self):
        # Get the current quests.
        quests_df = self.get_current_quests()

        if not quests_df.empty:
            # Only keep gardening and mining quest.
            quests_df = quests_df.loc[quests_df.quest_type.isin(["mining", "gardening"]), :]

            # Format the time to know when is the completion time of the quests.
            quests_df['current_time'] = time.time()

            # Find which quest are ready to be completed.
            if self.blocks == "MAX":
                isDone = (quests_df['current_time'] - quests_df["completed_time"]) > 0
            else:
                quests_df["elapse"] = quests_df['current_time'] - quests_df["start_time"]
                isDone = (quests_df["elapse"]/60) >= (self.blocks * 10)

            # Complete the quests that are done.
            if isDone.any():
                for heroes in quests_df.loc[isDone, "heroes"].values:
                    if self.blocks == "MAX":
                        tx_receipt = self.quest_routine(heroes, "complete")
                    else:
                        tx_receipt = self.quest_routine(heroes, "cancel")
    
    def start(self, profession):
        # Get current quests.
        quests_df = self.get_current_quests()
        
        if not quests_df.empty:
            # Only keep profession quest.
            quests_df = quests_df.loc[quests_df.quest_type == profession, :]
        
        # Only start if there aren't heroes on the quest.
        if quests_df.empty:
        
            # Load the hero data to know the stamina of heroes.
            hero_data = self.get_heroes_data()
            
            # If heroes are already questing, take them out of the hero_data.
            if not quests_df.empty:
                areQuesting = list(chain.from_iterable(quests_df.heroes.tolist()))
                hero_data = hero_data.loc[~hero_data.id.isin(areQuesting), :]
            
            # Look which heroes have more then self.blocks.
            isReady = hero_data.current_stamina > self.blocks
        
            # Sort by profession level, to get the best miner/gardener first.
            hero_data = hero_data.sort_values(profession, ascending = False)

            # Find gangs.
            isProfession = hero_data.profession == profession
            hero_data = hero_data.loc[isReady & isProfession, :]
            
            # Select the first hero then sort ascendingly, so only the lead
            # is always as best as possible for all rotation.            
            hero_ids = hero_data.id.tolist()[:1]
            
            # Will be changed once gardening takes 6 heroes as well.
            if profession == "mining":
                # Drop the first row not to have duplicates.
                hero_data = hero_data.iloc[1:, :]
            
                # Sort by profession level, to get the worst miner/gardener first.
                hero_data = hero_data.sort_values(profession, ascending = True)
                
                # Add the rest fo the heroes.
                hero_ids.extend(hero_data.id.tolist()[:5])

            # Start the quest.
            if hero_ids:
                method = "start" if profession == "mining" else "start_w_data"
                tx_receipt = self.quest_routine(hero_ids, method, profession, 1)

    
