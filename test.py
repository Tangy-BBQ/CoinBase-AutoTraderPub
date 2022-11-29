import cbpro, time, json, decimal, matplotlib.pyplot as plt
from authCredentials import (apiSecret, apiKey, apiPass)
D = decimal.Decimal

class TextWebsocketClient(cbpro.WebsocketClient):
    def on_open(self):
        self.url = 'wss://ws-feed-public.sandbox.pro.coinbase.com'
        self.message_count = 0
        
    def on_message(self,msg):
        self.message_count += 1
        msg_type = msg.get('type',None)
        if msg_type == 'ticker':
            time_val   = msg.get('time',('-'*27))
            price_val  = msg.get('price',None)
            if price_val is not None:
                price_val = float(price_val)
            product_id = msg.get('product_id',None)
            
            print(f"{time_val:30} \
                {price_val:.3f} \
                {product_id}\tchannel type:{msg_type}")
    def on_close(self):
        print(f"<---Websocket connection closed--->\n\tTotal messages: {self.message_count}")

#coinbase api url, use 'https://api-public.sandbox.pro.coinbase.com' to test
url='https://api-public.sandbox.pro.coinbase.com'

client = cbpro.AuthenticatedClient(
    apiKey,
    apiSecret,
    apiPass,
    api_url=url
)

#get account info and account history
accounts = client.get_accounts()
for acc in accounts:
    currency = acc.get('currency')
    if currency=='BTC':
        acc_id = acc.get('id')
acc_history = client.get_account_history(acc_id)
for hist in acc_history:
    print(json.dumps(hist,indent=1))


#trade testing
def continuousTrade(inputs):
    wsClient = TextWebsocketClient()
    wsClient.start()
    currentInfo = client.get_product_ticker(product_id='BTC-USD')
    lastPrice = D(currentInfo['price'])
    startTime = time.time()
    plt.show()
    while inputs != 'x' :
        currentInfo = client.get_product_ticker(product_id='BTC-USD')
        price = D(currentInfo['price'])
        percentChange = (1 - price/lastPrice)*100
        print ('price $' + str(price))
        print ('last price $' + str(lastPrice))
        print ('percent change ' + str(percentChange) + '%')
        if percentChange > .01 :
            client.place_market_order(product_id='BTC-USD',side='sell',funds=10000)
            lastPrice = price
            print ('sold $10000 of BTC')
        elif percentChange < -.01 :
            client.place_market_order(product_id='BTC-USD',side='buy',funds=10000)
            lastPrice = price
            print ('bought $10000 of BTC')
        currentTime = time.time() - startTime
        plotPoints(price, currentTime)
        time.sleep(3)
        #inputs = input()
    wsClient.close()

def plotPoints(x,y) :
    plt.plot(x,y)
    plt.draw()

if input("type 'start' to initiate trades\n") == 'start' :
    continuousTrade('start')
    plt.figure(figsize=(10,5))
    plt.title('Bitcoin Prices')
    plt.xlabel('price')
    plt.ylabel('time')

