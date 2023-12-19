from substrateinterface import SubstrateInterface, Keypair, ExtrinsicReceipt
import time
from substrateinterface.exceptions import SubstrateRequestException
import json
from scalecodec import ss58_encode, ss58_decode
import base58
import threading


DOT = 10**12
dot20 = 1 * 10**4
treasury_address = "13UVJyLnbVp9RBZYFwFGyDvVd1y27Tt8tkntv6Q7JVPhFsTB"


# 回调函数重连接
def connect_substrate(urls: list):
    try:
        import random
        url = random.choice(urls)
        substrate = SubstrateInterface(
            url=url,
        )
        print("连接上节点: {}".format(url))
        return substrate
    except ConnectionRefusedError:
        print("⚠️ No local Substrate node running, try running 'start_local_substrate_node.sh' first")
        time.sleep(6)
        return connect_substrate(url)


def main(urls: list, keypair: Keypair):
    try:
        substrate = connect_substrate(urls)
        transfer = substrate.compose_call(
            call_module='Balances',
            call_function='transfer_keep_alive',
            call_params={
                # 'dest': ss58_encode(ss58_decode(treasury_address, 0), ss58_format=substrate.ss58_format),
                'dest': keypair.ss58_address,
                'value': 1 * DOT * 0
            }
        )

        js = {"p": "dot-20", "op": "mint", "tick": "DOTA"}
        remark = substrate.compose_call(
            call_module='System',
            call_function='remark',
            call_params={
                'remark': json.dumps(js)
            })

        call = substrate.compose_call(
            call_module='Utility',
            call_function='batch_all',
            call_params={
                "calls": [transfer, remark]
            }
        )

        while True:

            extrinsic = substrate.create_signed_extrinsic(
                call=call,
                keypair=keypair,
            )

            receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)

            if receipt.is_success:
                print('{} 挖矿成功!, 区块高度 {}, Extrinsic "{}" included in block "{}"'.format(
                    keypair.ss58_address,
                    substrate.get_block_number(receipt.block_hash),
                    receipt.extrinsic_hash, receipt.block_hash
                ))
                continue
            else:
                print('⚠️ Extrinsic Failed: ', receipt.error_message)
                time.sleep(6)

    except Exception as e:
        print("错误: ", e)
        time.sleep(2)
        main(urls, s)


def get_keypairs(substrate: SubstrateInterface, s:str):
    keypair = Keypair.create_from_seed(s, ss58_format=substrate.ss58_format)
    print(keypair.ss58_address)
    return keypair


if __name__ == "__main__":

    ss = [
        # 填写你的私钥
        "0x你的私钥",
    ]

    urls = [
        "wss://rpc-polkadot.luckyfriday.io",
        "wss://dot-rpc.stakeworld.io",
        "wss://polkadot-rpc-tn.dwellir.com",
        "wss://polkadot-rpc.dwellir.com",
        "wss://1rpc.io/dot",
        "wss://rpc.ibp.network/polkadot",
        "wss://rpc.dotters.network/polkadot",
    ]

    # urls = [
    #     "wss://eosla.com",
    # ]

    substrate = connect_substrate(urls)
    users = []
    for s in ss:
        users.append(get_keypairs(substrate, s))
    thrs = []
    for s in users:
        t = threading.Thread(target=main, args=((urls, s)))
        thrs.append(t)
    for t in thrs:
        t.start()
    for t in thrs:
        t.join()
