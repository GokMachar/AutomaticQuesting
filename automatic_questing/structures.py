from typing import NamedTuple


# Server Structures
class AccountData(NamedTuple):
    private_key: str = "",
    pools: list = ["JEWEL-ONE"],
    address: str = "",
    blocks: int = 25


class Contract:
    IQuest = '0x5100bd31b822371108a0f63dcfb6594b9919eaf4'
    Hero = '0x5f753dcdf9b1ad9aabc1346614d1f4746fd6ce5c'
    AuctionSale = '0x13a65B9F8039E2c032Bc022171Dc05B30c3f2892'
    Empty = "0x0000000000000000000000000000000000000000"
    Foraging = "0x3132c76acF2217646fB8391918D28a16bD8A8Ef4"
    Fishing = "0xE259e8386d38467f0E7fFEdB69c3c9C935dfaeFc"
    Gardening = "0xe4154B6E5D240507F9699C730a496790A722DF19"
    Mining = '0x6FF019415Ee105aCF2Ac52483A33F5B43eaDB8d0'


QuestContracts = [
    ("Foraging", Contract.Foraging),
    ("Fishing", Contract.Fishing),
    ("Gardening", Contract.Gardening),
    ("Mining", Contract.Mining)
]
