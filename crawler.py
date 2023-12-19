# Python Substrate Interface Library
#
# Copyright 2018-2020 Stichting Polkascan (Polkascan Foundation).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from substrateinterface import SubstrateInterface, Keypair, ExtrinsicReceipt
import time
import json
from substrateinterface.exceptions import SubstrateRequestException

# import logging
# logging.basicConfig(level=logging.DEBUG)


# 回调函数重连接
def connect_substrate(url: str):
    try:
        substrate = SubstrateInterface(
            url=url,
        )
        return substrate
    except ConnectionRefusedError:
        print("⚠️ No local Substrate node running, try running 'start_local_substrate_node.sh' first")
        time.sleep(6)
        return connect_substrate(url)


def main(url: str, start: int, end: int):
    substrate = connect_substrate(url)
    # if start < 6:
    #     exit(0)
    while True:
        # print("head: ", substrate.get_chain_finalised_head())
        # print("block: ", substrate.get_block_number(substrate.get_chain_finalised_head()))
        #
        # print("head: ", substrate.get_chain_head())
        # print("block: ", substrate.get_block_number(substrate.get_chain_head()))
        try:
            # block_hash = substrate.get_block_hash(start)
            # if block_hash is None or start >= end:
            #     time.sleep(6)
            #     continue
            # trusted_block = start - 6
            block_hash = substrate.get_chain_finalised_head()
            txs = substrate.get_extrinsics(block_hash)
            tx_hash = None
            for tx in txs:
                if tx.value.get("call").get("call_function") == "batch_all" and len(
                        tx.value.get("call").get("call_args")[0].get("value")) == 2:

                    try:
                        if tx.value.get("call")["call_args"][0]["value"][0]['call_function'] == "transfer_keep_alive" and \
                                tx.value.get("call")["call_args"][0]["value"][1]['call_function'] == "remark":
                            tx_hash = tx.value['extrinsic_hash']
                            receipt = ExtrinsicReceipt(substrate, tx_hash, block_hash)
                            if receipt.is_success:

                                memo = json.loads(tx.value.get("call")["call_args"][0]["value"][1]['call_args'][0]["value"])
                                if memo["p"] == "dot-20": # and memo["tick"] == "dota":
                                    from_ = tx.value.get("address")
                                    print("from: ", from_)
                                    print("区块高度是：{}".format(substrate.get_block_number(receipt.block_hash)))
                                    # receipt.block_hash
                                    memo = tx.value.get("call")["call_args"][0]["value"][1]['call_args'][0]["value"]
                                    print("tx hash: ", tx_hash)
                                    print("memo: ", memo)
                    except Exception as e:
                        print(e)
            # start += 1
            # print("block num: ", trusted_block)
        except ConnectionRefusedError:
            substrate = connect_substrate(url)


if __name__ == "__main__":
    
    url = "wss://rpc-polkadot.luckyfriday.io"
    # url = "ws://127.0.0.1:9944"
    # url = "wss://eosla.com"
    end = 2**32 - 1
    main(url, 52300, end)