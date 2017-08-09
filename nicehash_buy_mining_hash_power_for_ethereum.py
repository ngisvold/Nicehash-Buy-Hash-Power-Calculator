# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 14:22:13 2017

@author: Nathan Gisvold Twitter: @NathanGisvold

This script calculates potential profit/loss buying Ethereum mining hashing power from Nicehash.com
Please use only for demonstration as the calculation is basic and does not include pool fees, luck, or nicehash's fee etc.

"""
import json
import urllib.request
from urllib.request import urlopen
from pandas.io.json import json_normalize

#My Ether Hashrate @ 1 Gigahash per day from Nicehash
eth_hashrate = 1000000000
#Hardcode ether block reward 
eth_block_reward = 5
eth_pool_luck = .04 #Luck Percent / +Uncles
eth_pool_stale = .015 #percent stale shares
eth_beta_shrinkage = .02 #percent loss misc
eth_pool_fee = .01
nice_hash_buying_fee = .031

#______________________________________________________________________________________________________
# Calculate mining profit from hashrate, network hash, and blocktime for Ethereum
#

def calc_mining_profit():
    request = urllib.request.Request(url='https://etherchain.org/api/miningEstimator', 
                                 data=None,
                                 headers={
                                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4'
                                })
    
    r_mining_est_eth = urllib.request.urlopen(request).read().decode('UTF-8')
    
    mining_est_eth_data = json.loads(r_mining_est_eth)
    
    df_mining_est_eth = json_normalize(mining_est_eth_data['data'])
    
    #Set Ether Variables
    eth_block_time_sec = df_mining_est_eth['blockTime'].iloc[0]
    #eth_difficulty = df_mining_est_eth['difficulty'].iloc[0]
    eth_network_hashrate = df_mining_est_eth['hashRate'].iloc[0]
    
    #print(f'ETH Blocktime in SEC: {eth_block_time_sec}')
    #print(f'ETH Difficulty: {eth_difficulty}')
    #print(f'ETH Network HashRate: {eth_network_hashrate}')
    
    return btc_day(eth_block_time_sec, eth_hashrate, eth_network_hashrate, eth_block_reward) 

#______________________________________________________________________________________________________
#How many blocks per day @ 86400 blocks/s:
#

def blocks_per_day(blocktime):
    blocks = 86400 / blocktime 
    return blocks

#______________________________________________________________________________________________________
#How many BTC per day at hashrate/network_hashrate:
#blocks/day * hashrate/network_hashrate * 5 Ether/block
#

def btc_day(blocktime, eth_hashrate, network_hashrate, reward):
    profit = blocks_per_day(blocktime) * ((eth_hashrate)/(network_hashrate)) * reward
    return profit


#______________________________________________________________________________________________________
#Request Nicehash market data for USA
#

def call_NiceHash():
    r_niceHash_usa = urlopen('https://api.nicehash.com/api?method=stats.global.current&location=1').read().decode('UTF-8')
    
    niceHash_usa_data = json.loads(r_niceHash_usa)
    
    df_niceHash_usa = json_normalize(niceHash_usa_data['result'], 'stats')
    
    #20 = DaggerHashimoto
    return df_niceHash_usa[20:21]['price'].iloc[0]

#______________________________________________________________________________________________________
#Request Poloniex Exchange for coin prices
#

def call_Poloniex():
    r_poloniex = urlopen('https://poloniex.com/public?command=returnTicker').read().decode('UTF-8')
    
    poloniex_data = json.loads(r_poloniex)
    
    return poloniex_data['BTC_ETH']['last']

#______________________________________________________________________________________________________
#Print out ether profit buying hashpower on Nicehash
#

n = call_Poloniex()
p = (((calc_mining_profit() *(1 + eth_pool_luck))*(1-eth_beta_shrinkage))*(1-eth_pool_stale))*(1-eth_pool_fee)
usa_eth_cost = float(call_NiceHash()) * (1 + nice_hash_buying_fee)

print(f'POLONIEX BTC_ETH: $ {n}')
print(f'Nicehash BTC_ETH: $ {usa_eth_cost} - nicehash mining fee @ {nice_hash_buying_fee * 100}%')
print(f'Revenue from Mining ETH in ETH: $ {p} @ pool luck {eth_pool_luck * 100}% - {eth_beta_shrinkage * 100}% Eth Loss Misc - {eth_pool_stale * 100}% Eth stale shares - {eth_pool_fee * 100}% Eth pool fee')
print(f'Revenue from Mining ETH in BTC: $ {p*float(n)}')
print(f'Gross Profit/Loss from Mining ETH in BTC: $ {(p*float(n))-float(usa_eth_cost)} or {(((p*float(n))-float(usa_eth_cost))/float(usa_eth_cost)*100)}%')










