import threading
import time
from coinswitch import get_depth, get_min, get_max, place_order, get_order, cancel_order, get_portfolio, \
    get_active_coins
from decouple import config

# get active coins

coinswitchx_coins = get_active_coins('coinswitchx')
binance_coins = get_active_coins('binance')
wazirx_coins = get_active_coins('wazirx')


def main(sym):
    while True:
        params = [
            {
                "exchange": "binance",
                "symbol": f"{sym}/USDT",
            }, {
                "exchange": "wazirx",
                "symbol": f"{sym}/INR",
            }, {
                "exchange": "wazirx",
                "symbol": "USDT/INR",
            }, {
                "exchange": "coinswitchx",
                "symbol": f"{sym}/INR"
            }, {
                "exchange": "coinswitchx",
                "symbol": "USDT/INR"
            }
        ]
        # calculation of usdt amount based on INR input
        inr_amount = config('AMOUNT_INR')
        resp = get_depth(params[4])
        usdt_data = resp['data']
        usdt_buy_data = usdt_data['asks']
        usdt_sell_data = usdt_data['bids']
        usdt_to_inr_amount = get_min(usdt_buy_data)
        usdt_to_inr_sell_amount = get_max(usdt_sell_data)
        print(resp)
        usdt_amount = float(inr_amount) / float(usdt_to_inr_amount)
        print(usdt_to_inr_amount, usdt_amount, inr_amount, sym)

        # get portfolio and adjust inr and usdt values
        portfolio = get_portfolio()
        print(portfolio)

        for e in portfolio['data']:
            if e['currency'] == 'INR' and float(e['main_balance']) < float(inr_amount):
                sellorder_resp = place_order("sell", usdt_to_inr_sell_amount, "wazirx", "USDT/INR",
                                             usdt_to_inr_sell_amount * 16)
                print(sellorder_resp)
                usdt_amount = 16
                time.sleep(10)

            if e['currency'] == 'USDT' and float(e['main_balance']) < float(usdt_amount):
                buyorder_resp = place_order("buy", usdt_to_inr_amount, "wazirx", "USDT/INR",
                                            1500 / usdt_to_inr_amount)
                print(buyorder_resp)
                inr_amount = 1500
                time.sleep(10)

        result = []
        buy = {}
        sell = {}

        for param in params:
            # check coin availability
            if param["symbol"] in get_active_coins(param['exchange']):
                response = get_depth(param)
                print(response)
                data = response['data']
                buy_data = data['asks']
                sell_data = data['bids']
                min_buy = get_min(buy_data)
                max_sell = get_max(sell_data)
                param['min_buy'] = min_buy
                param['max_sell'] = max_sell
            else:
                print("Symbol not available in ", param['exchange'])

            print(param)
            result.append(param)
            time.sleep(1)

        print("results", result)

        if result[0]['min_buy'] and result[0]['max_sell']:
            buy[result[0]['exchange']] = result[0]['min_buy']
            sell[result[0]['exchange']] = result[0]['max_sell']

        for r in range(1, len(result), 2):
            if result[r]['min_buy'] and result[r]['max_sell']:
                b1 = result[r]['min_buy']
                b2 = result[r + 1]['min_buy']
                s1 = result[r]['max_sell']
                s2 = result[r + 1]['max_sell']
                print(b1, b2)
                print(s1, s2)
                buy[result[r]['exchange']] = float(b1) / float(s2)
                sell[result[r]['exchange']] = float(s1) / float(b2)

        print('buy', buy)
        print('sell', sell)

        min_buy_key = min(buy, key=lambda k: buy[k])
        print(min_buy_key)
        max_sell_key = max(sell, key=lambda k: sell[k])
        print(max_sell_key)

        buy_symbol = params[0]['symbol'] if min_buy_key == 'binance' else params[1]['symbol']
        sell_symbol = params[0]['symbol'] if max_sell_key == 'binance' else params[1]['symbol']

        if min_buy_key == 'binance':
            buy_value = result[0]['min_buy']
        elif min_buy_key == 'wazirx':
            buy_value = result[1]['min_buy']
        else:
            buy_value = result[3]['min_buy']

        if max_sell_key == 'binance':
            sell_value = result[0]['max_sell']
        elif min_buy_key == 'wazirx':
            sell_value = result[1]['max_sell']
        else:
            sell_value = result[3]['max_sell']

        buy_amount = usdt_amount if min_buy_key == 'binance' else inr_amount
        sell_amount = usdt_amount if max_sell_key == 'binance' else inr_amount

        delta = ((sell[max_sell_key] - buy[min_buy_key]) / buy[min_buy_key]) * 100

        print('delta', delta)

        if ((min_buy_key == 'binance' or max_sell_key == 'binance') and delta > 2.1) or (
                (min_buy_key != 'binance' or max_sell_key != 'binance') and delta > 1.1):
            # place buy order
            print('buy amount', buy_amount)
            buy_quantity = float(buy_amount) / float(buy_value)
            buyorder_resp = place_order("buy", buy_value, min_buy_key, buy_symbol, buy_quantity)
            print(buyorder_resp)

            # wait for 60 seconds
            time.sleep(60)

            # buy order details
            buy_order_details = get_order(buyorder_resp['data']['order_id'])
            print(buy_order_details)
            buy_order_status = buy_order_details['data']['status']
            print('buy order status', buy_order_status)

            if buy_order_status == "OPEN":
                buy_cancel_resp = cancel_order(buyorder_resp['data']['order_id'])
                print(buy_cancel_resp)

            if buy_order_status == "EXECUTED":
                # place sell order
                print('sell amount', sell_amount)
                sell_quantity = float(sell_amount) / float(sell_value)
                sellorder_resp = place_order("sell", sell_value, max_sell_key, sell_symbol, sell_quantity)
                print(sellorder_resp)

                # wait for 60 seconds
                time.sleep(60)

                # sell order details
                sell_order_details = get_order(buyorder_resp['data']['order_id'])
                print(sell_order_details)
                sell_order_status = sell_order_details['data']['status']
                print('sell order status', sell_order_status)

                if sell_order_status == "OPEN":
                    sell_cancel_resp = cancel_order(buyorder_resp['data']['order_id'])
                    print(sell_cancel_resp)

        else:
            print("No order placed in this round---------------------")


def run_function_in_thread(inputs):
    threads = []

    for input_value in inputs:
        thread = threading.Thread(target=main, args=(input_value,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    input_values = ['BNB',
                    'CHR',
                    'COMP',
                    'COTI',
                    'CRV',
                    'DYDX',
                    'FTM',
                    'GALA',
                    'JASMY',
                    'LRC',
                    'MATIC',
                    'MKR',
                    'NKN',
                    'OGN',
                    'PEPE',
                    'REN',
                    'REQ',
                    'SAND',
                    'SHIB',
                    'SNX',
                    'TRX',
                    'XLM',
                    'XRP',
                    'YFI']
    print(input_values)
    run_function_in_thread(input_values)
