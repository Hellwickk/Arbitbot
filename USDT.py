from coinswitch import get_portfolio, get_depth, place_order, get_min, get_max


def main():
    try:
        exchange = "WAZIRX"
        symbol = "USDT/INR"

        while True:
        print("Getting portfolio information...")
        portfolio_data = get_portfolio()
        # print("Portfolio data:", portfolio_data)

        usdt_balance = 0
        inr_balance = 0

        for entry in portfolio_data['data']:
            currency = entry['currency']
            main_balance = float(entry.get('main_balance', 0))

            if currency == 'USDT':
                usdt_balance = main_balance
            elif currency == 'INR':
                inr_balance = main_balance

        print("USDT Balance:", usdt_balance)
        print("INR Balance:", inr_balance)

        usdt_threshold = 11
        inr_threshold = 1000

        # Get depth information
        depth_data = get_depth({"symbol": symbol, "exchange": exchange})
        # print("Depth Data:", depth_data)

        resp = get_depth({"symbol": "USDT/INR", "exchange": exchange})
        usdt_data = resp['data']
        usdt_buy_data = usdt_data['asks']
        usdt_sell_data = usdt_data['bids']
        buy_price = get_min(usdt_buy_data)
        sell_price = get_max(usdt_sell_data)
        print(resp)

        if usdt_balance < usdt_threshold and buy_price > 0:
            print(f"USDT balance ({usdt_balance}) is below threshold. Creating buy order at {buy_price}...")
            buyorder_resp = place_order("buy", buy_price, "wazirx", "USDT/INR", 11)
            print(buyorder_resp)

        if inr_balance < inr_threshold and sell_price > 0:
            print(f"INR balance ({inr_balance}) is below threshold. Creating sell order at {sell_price}...")
            buyorder_resp = place_order("sell", sell_price, "wazirx", "USDT/INR",
                                        1000 / sell_price)
            print(buyorder_resp)
        print("End of the main function.")
        time.sleep(10)
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
