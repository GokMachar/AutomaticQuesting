import os
import pickle
from logging import getLogger
import pandas as pd
import numpy as np

from web3 import Web3, providers
from collections import defaultdict
from automatic_questing.utils import parse_stat_genes, POOLS

from automatic_questing.structures import AccountData, Contract, QuestContracts

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Load hero ABI.
QUEST_ABI = pickle.load(open(f"{__location__}\\..\\ABIs\\quest_abi.pk", "rb"))
HERO_ABI = pickle.load(open(f"{__location__}\\..\\ABIs\\hero_abi.pk", "rb"))
AUCTION_ABI = pickle.load(open(f"{__location__}\\..\\ABIs\\auction_abi.pk", "rb"))


class UserWeb3:
    def __init__(self, config, account):
        self.config = config
        self.account_data = account
        self.address = Web3.toChecksumAddress(account.address)
        self.private_key = self.account_data.private_key
        self.my_pools = [POOLS.index(p) for p in account.pools]
        self.w3 = Web3(providers.HTTPProvider(self.config.rpc))
        self.gas_price = self.w3.eth.gas_price
        self.method_dict = {
            "start": self.start_quest,
            "start_w_data": self.start_quest_with_data,
            "cancel": self.cancel_quest,
            "complete": self.complete_quest
        }
        account = self.w3.eth.account.privateKeyToAccount(self.private_key)
        self.w3.eth.default_account = account.address

        # Set up contracts.
        self.contracts = {}
        zipped = zip(
            ["quest", "hero", "auction"],
            [Contract.IQuest, Contract.Hero, Contract.AuctionSale],
            [QUEST_ABI, HERO_ABI, AUCTION_ABI]
        )

        for name, address, abi in zipped:
            self.contracts[name] = self.set_up_contract(address, abi)

        self.logger = getLogger()

        self.logger.info(f"Using RPC server {self.config.rpc}")

    def set_up_contract(self, address, abi):
        contract_address = Web3.toChecksumAddress(address)
        contract = self.w3.eth.contract(contract_address, abi=abi)
        return contract
        
    def log_transaction(self, tx):
        self.logger.info("Signing transaction")
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        self.logger.info(f"Sending transaction {tx}")
        _ = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.logger.info("Transaction successfully sent !")
        self.logger.info(f"Waiting for transaction https://explorer.harmony.one/tx/{signed_tx.hash.hex()} to be mined")
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(
            transaction_hash=signed_tx.hash,
            timeout=24 * 3600,
            poll_latency=3
        )
        self.logger.info("Transaction mined !")
        self.logger.info(str(tx_receipt))

        return tx_receipt
        
    def complete_quest(self, heroes, profession=None, attempts=None, gas=None):
        # Make sure we have integers as heroes ids.
        heroes = [int(h) for h in heroes]
        
        # Build transaction.
        self.logger.info(f"Completing quest with hero ids {heroes}")
        tx = self.contracts["quest"].functions.completeQuest(heroes[0]).buildTransaction({
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'from': self.address})
        if isinstance(gas, int):
            tx["gas"] = gas
        
        # Log and return transaction.
        return self.log_transaction(tx)
        
    def cancel_quest(self, heroes, profession=None, attempts=None, gas=None):
        # Make sure we have integers as heroes ids.
        heroes = [int(h) for h in heroes]
        
        # Build transaction.
        self.logger.info(f"Cancelling quest with hero ids {heroes}")
        tx = self.contracts["quest"].functions.cancelQuest(heroes[0]).buildTransaction({
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'from': self.address})
            
        if isinstance(gas, int):
            tx["gas"] = gas

        # Log and return transaction.
        return self.log_transaction(tx)
        
    def start_quest(self, heroes, profession, attempts, gas=None):
        # Make sure we bundle integers as heroes ids with the other function inputs.
        heroes = [int(h) for h in heroes]
        start_quest_inputs = [heroes, getattr(Contract, profession.capitalize()), int(attempts)]

        self.logger.info(f"Starting quest with hero ids {heroes}")
        tx = self.contracts["quest"].functions.startQuest(*start_quest_inputs).buildTransaction({
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'from': self.address})
        if isinstance(gas, int):
            tx["gas"] = gas
            
        # Log and return transaction.
        return self.log_transaction(tx)
    
    def start_quest_with_data(self, heroes, profession, _, gas=None):
        # Make sure we bundle integers as heroes ids with the other function inputs.
        heroes = [int(h) for h in heroes]
        
        # Get the gardening pool.
        pool = self.my_pools[0]
        
        # Set inputs.
        data = (pool, 1, 1, 1, 1, 1, "", "", Contract.Empty, Contract.Empty, Contract.Empty, Contract.Empty)
        start_quest_inputs = [heroes, getattr(Contract, profession.capitalize()), 1, data]

        self.logger.info(f"Starting quest with hero ids {heroes}")
        tx = self.contracts["quest"].functions.startQuestWithData(*start_quest_inputs).buildTransaction({
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'from': self.address})
        if isinstance(gas, int):
            tx["gas"] = gas
            
        # Log and return transaction.
        return self.log_transaction(tx)
        
    def quest_routine(self, heroes, method, profession=None, attempts=None, gas=None):
        # First attempt at the transaction.
        tx_receipt = self.method_dict[method](heroes, profession, attempts, gas)

        # If the transaction was unsuccessful try it again.
        if tx_receipt["status"] == 0:
            # Complete the quest again.
            tx_receipt = self.method_dict[method](heroes, profession, attempts, gas)
            if tx_receipt["status"] == 0:
                print("Unsuccessful")
        return tx_receipt    
    
    def unlist_hero(self, hero_id):
        """ Get the heroes for a specific address (not in tavern) """
        self.logger.info(f"Unlisting hero {hero_id} from the tavern")
        tx = self.contracts['auction'].functions.cancelAuction(hero_id).buildTransaction({
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'from': self.address})
        return self.log_transaction(tx)  
    
    def list_hero(self, hero_id, price):
        """ Get the heroes for a specific address (not in tavern) """
        self.logger.info(f"Listing hero {hero_id} in the tavern")
        price_wei = self.w3.toWei(price, "ether")
        list_inputs = [hero_id, price_wei, price_wei, 60, Contract.Empty]
        tx = self.contracts['auction'].functions.createAuction(*list_inputs).buildTransaction({
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'from': self.address})
        return self.log_transaction(tx)  
    
    def get_user_heroes(self):
        """ Get the heroes for a specific address (not in tavern) """
        heroes = self.contracts['hero'].functions.getUserHeroes(self.address).call()
        return heroes
    
    def get_auction_data(self, hero_id):
        result = self.contracts['auction'].functions.getAuction(hero_id).call()
        auction = {"id": result[0], "owner": result[1], "startingPrice": result[2],
                   "endingPrice": result[3], "duration": result[4], "startedAt": result[5]}
        return auction
        
    def get_user_auctions(self):
        result = self.contracts['auction'].functions.getUserAuctions(self.address).call()
        return result

    def get_heroes_data(self):
        # Get user's heroes.
        heroes = self.get_user_heroes()
        
        # Get user's heroes on sales.
        heroes_on_auction = self.get_user_auctions()
        
        # Query directly from the rpc to update the stamina of heroes.
        data_dict = defaultdict(list)
        
        # Loop over heroes to get their information.
        for i in heroes + heroes_on_auction:
            hero_info = self.contracts["hero"].functions.getHero(i).call()
            data_dict["id"].append(i)
            data_dict["stamina"].append(hero_info[4][10])
            data_dict["staminaFullAt"].append(hero_info[3][0])
            data_dict["profession"].append(parse_stat_genes(hero_info[2][0])['profession'])
            data_dict["mining"].append(hero_info[7][0])
            data_dict["gardening"].append(hero_info[7][1])
            data_dict["foraging"].append(hero_info[7][2])
            data_dict["fishing"].append(hero_info[7][3])
            
        # Add identifier for heroes in the tavern.
        for i in heroes:
            data_dict["onSales"].append(False)
        for i in heroes_on_auction:
            data_dict["onSales"].append(True)
            
        # Create the hero DataFrame.
        hero_data = pd.DataFrame(data_dict)
                                                 
        # Get stamina full in pd.DateTime. 
        hero_data["staminaFullAtTime"] = pd.to_datetime(hero_data.staminaFullAt, unit='s') 
        
        # Get the current stamina of heroes.
        hero_data["staminaFullAtTime"] = pd.to_datetime(hero_data.staminaFullAt, unit='s') 
        hero_data['time'] = hero_data["staminaFullAtTime"] - pd.to_datetime('now') 
        condition = hero_data['time'] < pd.Timedelta(days=0)
        hero_data["current_stamina"] = 0
        hero_data.loc[condition, "current_stamina"] = hero_data.loc[condition, "stamina"]
        hero_data.loc[~condition, "current_stamina"] = hero_data.loc[~condition, "stamina"] - (hero_data.loc[~condition, "time"] / pd.Timedelta("20 minutes")).apply(np.ceil)
        hero_data["current_stamina"] = hero_data["current_stamina"].astype(int)
        return hero_data
        
    def get_current_quests(self):
        """ Get the current quests for a specific address """
        # Change the time if the operation was successful.
        current_quests = self.contracts["quest"].functions.getActiveQuests(self.address).call()
        
        if current_quests:
            # Create a dataframe out of the current quests.
            quests_dict = defaultdict(list)
            for q in current_quests:
                quests_dict["id"].append(q[0])
                quests_dict["quest_address"].append(q[1])
                quests_dict["heroes"].append(q[2])
                quests_dict["address"].append(q[3])
                quests_dict["start_time"].append(q[4])
                quests_dict["start_block"].append(q[5])
                quests_dict["completed_time"].append(q[6])
                quests_dict["attempts"].append(q[7])
                quests_dict["status"].append(q[8])
            quests_df = pd.DataFrame(quests_dict)
    
            # Add the quest type.
            for q, a in QuestContracts:
                is_quest = quests_df.quest_address == a
                quests_df.loc[is_quest, "quest_type"] = q
    
            return quests_df






