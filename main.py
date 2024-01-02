import threading
import time
from coinswitch import get_depth, get_min, get_max, place_order, get_order, cancel_order, get_portfolio, \
    get_active_coins
from decouple import config


def main(sym):
    try:
        while True:
            params = [
                {"exchange": "binance", "symbol": f"{sym}/USDT"},
                {"exchange": "wazirx", "symbol": f"{sym}/INR"},
                {"exchange": "wazirx", "symbol": "USDT/INR"},
                {"exchange": "coinswitchx", "symbol": f"{sym}/INR"},
                {"exchange": "coinswitchx", "symbol": "USDT/INR"}
            ]

            inr_amount = config('AMOUNT_INR')
            resp = get_depth(params[4])

            if resp is not None and 'data' in resp:
                usdt_data = resp['data']
                usdt_buy_data = usdt_data['asks']
                usdt_sell_data = usdt_data['bids']
                usdt_to_inr_amount = get_min(usdt_buy_data)
                usdt_to_inr_sell_amount = get_max(usdt_sell_data)
                usdt_amount = float(inr_amount) / float(usdt_to_inr_amount)
                print(usdt_to_inr_amount, usdt_amount, inr_amount, sym)
            else:
                print("Error: Unable to fetch depth data.")

            portfolio = get_portfolio()
            result = []
            buy = {}
            sell = {}

            for param in params:
                if param["symbol"] in get_active_coins(param['exchange']):
                    response = get_depth(param)
                    data = response['data']
                    buy_data = data['asks']
                    sell_data = data['bids']
                    min_buy = get_min(buy_data)
                    max_sell = get_max(sell_data)
                    param['min_buy'] = min_buy
                    param['max_sell'] = max_sell
                else:
                    print("Symbol not available in", param['exchange'])
                result.append(param)
                time.sleep(1)

            print("results", result)

            if result[0]['min_buy'] and result[0]['max_sell']:
                buy[result[0]['exchange']] = result[0]['min_buy']
                sell[result[0]['exchange']] = result[0]['max_sell']

            for r in range(1, len(result), 2):
                if result[r]['min_buy'] and result[r]['max_sell']:
                    b1, b2 = result[r]['min_buy'], result[r + 1]['min_buy']
                    s1, s2 = result[r]['max_sell'], result[r + 1]['max_sell']
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

            buy_value = result[0]['min_buy'] if min_buy_key == 'binance' else (
                result[1]['min_buy'] if min_buy_key == 'wazirx' else result[3]['min_buy'])
            sell_value = result[0]['max_sell'] if max_sell_key == 'binance' else (
                result[1]['max_sell'] if max_sell_key == 'wazirx' else result[3]['max_sell'])

            buy_amount = usdt_amount if min_buy_key == 'binance' else inr_amount
            sell_amount = usdt_amount if max_sell_key == 'binance' else inr_amount

            delta = ((sell[max_sell_key] - buy[min_buy_key]) / buy[min_buy_key]) * 100
            print('delta', delta)

            if ((min_buy_key == 'binance' or max_sell_key == 'binance') and delta > 2.1) or (
                    (min_buy_key != 'binance' or max_sell_key != 'binance') and delta > 1.1):
                print('buy amount', buy_amount)
                buy_quantity = float(buy_amount) / float(buy_value)
                buyorder_resp = place_order("buy", buy_value, min_buy_key, buy_symbol, buy_quantity)
                print(buyorder_resp)

                time.sleep(60)

                buy_order_details = get_order(buyorder_resp['data']['order_id'])
                print(buy_order_details)
                buy_order_status = buy_order_details['data']['status']
                print('buy order status', buy_order_status)

                if buy_order_status == "OPEN":
                    buy_cancel_resp = cancel_order(buyorder_resp['data']['order_id'])
                    print(buy_cancel_resp)

                if buy_order_status == "EXECUTED":
                    executed_quantity = float(buy_order_details['data']['executed_qty'])

                    print('sell amount', sell_amount)
                    sell_quantity = executed_quantity
                    sellorder_resp = place_order("sell", sell_value, max_sell_key, sell_symbol, sell_quantity)
                    print(sellorder_resp)

                    # wait for 60 seconds
                    time.sleep(60)

                    # sell order details
                    sell_order_id = sellorder_resp['data']['order_id']
                    sell_order_details = get_order(sell_order_id)
                    print(sell_order_details)
                    sell_order_status = sell_order_details['data']['status']
                    print('sell order status', sell_order_status)

                    if sell_order_status == "OPEN":
                        sell_cancel_resp = cancel_order(sell_order_id)
                        print(sell_cancel_resp)

                    if sell_order_status == "OPEN":
                        sell_cancel_resp = cancel_order(buyorder_resp['data']['order_id'])
                        print(sell_cancel_resp)

                else:
                    print("No order placed in this round---------------------")
    except Exception as e:
        print(f"An error occurred: {e}")


def wait_for_order_execution(order_id, max_wait_time=60):
    wait_time = 0
    while wait_time < max_wait_time:
        time.sleep(5)
        order_details = get_order(order_id)
        order_status = order_details['data']['status']
        print(f'Order {order_id} status: {order_status}')

        if order_status == "EXECUTED":
            return

        wait_time += 5

    print(f"Order {order_id} was not executed within the expected time.")


def run_function_in_thread(inputs):
    threads = []

    for input_value in inputs:
        thread = threading.Thread(target=main, args=(input_value,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    input_values = {'LTC',
                    'PEPE',
                    'LINK',
                    'YFI',
                    'UNI',
                    'REQ',
                    'OGN',
                    'CHR',
                    'CRV',
                    'BNB',
                    'TRX',
                    'COMP',
                    'MKR',
                    'UMA',
                    'XLM',
                    'OMG',
                    'LRC',
                    'FTM',
                    'COTI',
                    'ALICE',
                    'CELR',
                    'DOGE',
                    'XRP',
                    'SAND',
                    'SHIB',
                    'MATIC',
                    'GALA',
                    'JASMY',
                    'BTC',
                    'ETH',
                    'ZRX',
                    'REN',
                    'NKN',
                    'SNX',
                    'BAT'}
    # input_values = {'COTI'}
    print(input_values)
    run_function_in_thread(input_values)
