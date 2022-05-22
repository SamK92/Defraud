import requests
import deso
import time
import asyncio
from pyppeteer import launch
import json
API_URL = "https://node.deso.org/api/v1"
API_HEADER = {"Content-Type": "application/json; charset=utf-8"}

class Utils:
    # Post request to get block at height or blockHash h
    @staticmethod
    def queryBlock(h):
        payload = {"Height": h, "FullBlock": True,}
        return requests.post(f"{API_URL}/block", headers=API_HEADER, json=payload)

    # Gets user's transactions or transactionIdx query
    @staticmethod
    def queryUserTransaction(pubKey):
        #return deso.Users.getTransactionInfo(publicKey=pubKey)
        payload = {"TransactionIDBase58Check": pubKey,}
        return requests.post(f"{API_URL}/transaction-info", headers=API_HEADER, json=payload)

    @staticmethod
    async def _getTransaction(transaction_id):
        url = f"https://explorer.deso.org/?transaction-id={transaction_id}"
        browser = await launch()
        page = await browser.newPage()
        await page.goto(url)
        time.sleep(5)
        await page.screenshot({'path': 'example.png'})
        content = await page.content()
        await browser.close()
        return content

    @staticmethod
    def getTransaction(transaction_id):
        transaction_id
        content = asyncio.get_event_loop().run_until_complete(Utils._getTransaction(transaction_id))
        content = content[content.find('Raw Metadata'):]
        content = content[content.find('{'):content.find('</pre>')]
        return json.loads(content)

    @staticmethod
    def queryProfile(pubKey):
        prof = deso.Users.getSingleProfile(pubKey)
        #print(prof['Profile'])
        return deso.Users.getTransactionInfo(publicKey=pubKey)

    # Gets the most recent block (useful for getting height of most recent)
    @staticmethod
    def queryMostRecentBlock():
        return requests.get(API_URL)

    # Returns None if it's not safe to access, else the value
    @staticmethod
    def safeMapAccess(m, k):
        if k in m:
            return m[k]
        return None

    # User profile pub key
    @staticmethod
    def getProfilePicture(pubKey):
        return userdeso.Users.getProfilePic(pubKey)

