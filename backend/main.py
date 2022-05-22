#!/usr/bin/env python
import deso
import math
import pprint
import sys
from utils.Utils import Utils
from sklearn import preprocessing
import pickle
import json
import requests
import deso
import time
import asyncio
from pyppeteer import launch
import json

print(sys.path)
with open('model.pkl', 'rb') as f:
    clf2 = pickle.load(f)

def run_model(x):
    f = preprocessing.normalize([x], norm='l2')
    return clf2.predict(f), clf2.predict_proba(f)

def main2():
    block = Utils.queryMostRecentBlock().json()
    transactions = block['Transactions']
    for transaction in transactions:
        #print(transaction)
        Utils.queryProfile(transaction['Outputs'][0]['PublicKeyBase58Check'])


def transactionDetails(tnxKey):
    results = {}
    results['Pkeys'] = []
    results['Usernames'] = []
    results['ProfilePicURL'] = []
    trans = Utils.queryUserTransaction(tnxKey).json()

    input_trans = trans["Transactions"][0]["Inputs"]
    output_trans = trans["Transactions"][0]["Outputs"]

    '''
    for inp in input_trans:
        results['Pkeys'].append(inp["PublicKeyBase58Check"])
    '''

    for out in output_trans:
        results['Pkeys'].append(out["PublicKeyBase58Check"])

    #print(results['Pkeys'])
    i = 0
    n = len(results['Pkeys'])
    while i < n:
        pKey = results['Pkeys'][i]
        #print(i,n)
        try:
            x=deso.Users.getSingleProfile(pKey)
            #print(x)
            if('error' in x):
                results['Pkeys'].pop(i)
                n-=1
                continue
            #print("--------------", x)
            x=x['Profile']['Username']
            #print(x)
            results['Usernames'].append(x)
            results['ProfilePicURL'].append(deso.Users.getProfilePic(pKey))
            i+=1
        except Exception as e:
            #print(e)
            i+=1
            continue
    return results


# n int
def main(n):
    results = {}

    block = Utils.queryMostRecentBlock().json()
    # Get offset if necessary
    if n != 0:
        block = Utils.queryBlock(block["Header"]["Height"]-n).json()
    timeStamp = block["Header"]["TstampSecs"]
    for trans in block['Transactions']:
        if trans['TransactionType'] == 'BASIC_TRANSFER':
            max_received = -math.inf
            min_received = math.inf
            average_received = 0
            n1 = 0
            tID = trans['TransactionIDBase58Check']
            for input_transaction in trans['Inputs']:
                input_trans = Utils.queryUserTransaction(input_transaction['TransactionIDBase58Check']).json()
                input_trans = input_trans['Transactions'][0]['TransactionMetadata']
                max_received = max(max_received, input_trans['BasicTransferTxindexMetadata']['TotalOutputNanos'])
                min_received = min(min_received, input_trans['BasicTransferTxindexMetadata']['TotalOutputNanos'])
                average_received = average_received + input_trans['BasicTransferTxindexMetadata']['TotalOutputNanos']
                n1 += 1
            average_received = average_received / n1

            sent_tnx = len(trans['Inputs'])
            received_tnx = len(trans['Outputs'])

            sum_sent = 0
            min_sent = math.inf
            max_sent = -math.inf
            n = 0
            for out in trans['Outputs']:
                min_sent = min(min_sent, out['AmountNanos'])
                max_sent = max(max_sent, out['AmountNanos'])
                sum_sent = sum_sent + out['AmountNanos']
                n += 1
            avg_sent = sum_sent / n

            total_sent = trans['TransactionMetadata']['BasicTransferTxindexMetadata']['TotalInputNanos']
            total_received = trans['TransactionMetadata']['BasicTransferTxindexMetadata']['TotalOutputNanos']
            balance = total_received - total_sent + trans['TransactionMetadata']['BasicTransferTxindexMetadata']['FeeNanos']
            x = [sent_tnx, received_tnx, min_received/1e9, max_received/1e9, average_received/1e9, min_sent/1e9, max_sent/1e9, avg_sent/1e9, total_sent/1e9, total_received/1e9, balance/1e9]
            resC, resX = run_model(x)
            results[tID] = [timeStamp, resC, resX]
    #print(results)
    return results

async def post_it(s):
        url = f"https://www.diamondapp.com"
        browser = await launch()
        page = await browser.newPage()
        await page.goto(url)
        time.sleep(5)
        await page.screenshot({'path': 'example.png'})
        content = await page.content()
        await browser.close()
        return content

from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as Keyboard
def post(s):
    mouse = Controller()
    keyboard = Keyboard()
    mouse.position = (1470, 700)
    mouse.click(Button.left, 1)
    mouse.position = (1196, 416)
    mouse.click(Button.left, 1)
    keyboard.type(s)
    mouse.position = (1196, 416)
    mouse.click(Button.left, 1)
    time.sleep(1)
    mouse.position = (1400, 530)
    mouse.click(Button.left, 1)
    #for i in range(10):
    #    mouse.position = (1400, 416 + 5 * i)
    #    mouse.click(Button.left, 1)
if __name__ == "__main__":
    posted = set()
    while True:
        try:
            transactions = main(0)
            for t in transactions.keys():
                if transactions[t][1] == 1:
                    s = ''
                    for user in transactionDetails(t)['Usernames']:
                        s = s + user+', '
                    if 'Possible fradulent transaction in $DESO Blockchain: Transaction ID:'+t not in posted:
                        print('Possible fradulent transaction in $DESO Blockchain: Transaction ID:', t)
                        print(transactions[t][2])
                        print(transactions[t][1])
                        post('Possible fraudulent transaction in $DESO Blockchain: Transaction ID:' + t + ' Participants: '+ s[:-2] + ' Confidence: '+str(int(transactions[t][2][0][1]*100))+'%')
                        posted.add(t)
                    time.sleep(3)
                else:
                    if t not in posted:
                        posted.add(t)
                        print('Not fraudulent')
            time.sleep(10)
        except KeyError:
            pass
    #print(transactionDetails("3JuETDb8fDqmttC9HXw4bTwv2gbTTzYCpbArpuWb4iFt5EQuyr62xf"))


