import math
import time
from tqdm.notebook import tqdm
from sqlitedict import SqliteDict
from zimcoin_miner import ZimcoinMiner
from blocks import Block
from blocks import mine_block
from persistence import Persistence, dict_to_block
from node import Node
from connections import run_server, remote_connection
from blockchain_state import BlockchainState, verify_reorg

REMOTE_NODES = ["ws://node.zimcoin.org:46030/"]
node = Node.start("./0x00_connecting.sqlite").proxy()
for remote in REMOTE_NODES:
    remote_connection(node, remote)


def get_target_blocks(start_height : int,
                      file_name : str) -> list:
    """
    Get a list of the blocks to attack.
    """
    attack_blocks = []
    blocks = Persistence.start(file_name).proxy().get_blocks().get()

    for block in tqdm(blocks, 'Getting target attack blocks'):
        if block.height >= start_height:
            attack_blocks.append(block)

    return attack_blocks

# get the attack blocks
height = 1638
attacked_blocks = []
db = SqliteDict('/Users/foulds/code/dsm070-2022-apr/topic_07/0x01_attack.sqlite', autocommit=True)
while True:
    block_dict = db.get(height)
    if block_dict is None:
        break
    attacked_blocks.append(dict_to_block(block_dict))
    height += 1

print(f'Attacked Block Count : {len(attacked_blocks)}')
print(f'First Block Height : {attacked_blocks[0].height}')
print(f'First block difficulty : {attacked_blocks[0].difficulty}')
print(f'Last block height : {attacked_blocks[-1].height}')

# get the existing list
existing_list = get_target_blocks(0, '/Users/foulds/code/dsm070-2022-apr/topic_07/0x00_connecting.sqlite')
existing_list = existing_list[:attacked_blocks[0].height]
print(f'Existing List last block height : {existing_list[-1].height}')
print(f'Attack List first block height : {attacked_blocks[0].height}')

# # mine a new block to add next to the attacked blocks
# new_block = mine_block(
#     previous= attacked_blocks[-1].block_id,
#     height=attacked_blocks[-1].height + 1,
#     miner=MINER_ADDRESS,
#     transactions=[],
#     timestamp=int(time.time()),
#     difficulty=target_difficulty)

# add to the attacked blocks
# attacked_blocks.append(new_block)

# send the blocks to the nodes
existing_list.extend(attacked_blocks)
print(f'Existing List Block Count : {len(existing_list)}')


# create a new state
new_state = BlockchainState([], dict(), 0)
for block in tqdm(existing_list, 'Building New State'):
    #print(block.height)
    new_state.verify_and_apply_block(block)