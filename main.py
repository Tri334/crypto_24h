import requests
import math
def getFeeFuture(actual_usdt,funding_fee,cycle,leverage):
    fee = (funding_fee)/100
    total = actual_usdt * fee * cycle * leverage
    return float(total)

def binanceProfitFuture(actual_usdt,funding_fee,cyle_pay,leverage,tp_percent,fee_maker_taker,
                        stop_loss):
        get_fee = getFeeFuture(actual_usdt=actual_usdt,funding_fee=funding_fee,cycle=cyle_pay,leverage=leverage)
        fee_buy = (actual_usdt * leverage * fee_maker_taker/100)
        profit = (actual_usdt) * tp_percent/100
        fee_sell = (profit * leverage * fee_maker_taker/100)
        clean_profit =  profit - fee_buy - get_fee
        stop_loss_have =  actual_usdt * stop_loss/100 * leverage
        print('\n')
        print('Actual Margin:')
        print(actual_usdt)
        print('Maintenance Margin:')
        print(round(actual_usdt * 70/100,5))
        print('Size:')
        print(round(actual_usdt*leverage,5) )
        print('Total Usdt Must Have:')
        print(round(actual_usdt * 70/100 + actual_usdt + actual_usdt * 0.5,5))
        print('Buy & Sell Fee:')
        print(round(fee_buy,5))
        print('----------------')
        print(round(fee_sell,5))
        print('Funding Fee:')
        print(round(get_fee,5))
        print('Total Funding')
        print(round(get_fee + fee_buy,5))
        print('================')
        print('Stop Loss:')
        print(round(stop_loss_have+get_fee+fee_buy,5))
        print('Profit Sebelum Fee:')
        print(round(profit,5))
        print('Profit:')
        print(round(clean_profit,5))


def tokoProfitSpot(toko_usdt,tp):
    toko_trading_fee = 0.31/100
    toko_buy_fee = toko_usdt * toko_trading_fee
    toko_usdt = toko_usdt - toko_trading_fee
    tp = toko_usdt * tp/100
    toko_sell_fee = (toko_usdt+tp) * toko_trading_fee
    toko_final_asset = toko_usdt + tp - toko_sell_fee
    print('Tokocryto Buy Fee:')
    print(round(toko_buy_fee,5))
    print('Asset Now:')
    print(round(toko_usdt,5))
    print('Tokocryto Sell Fee:')
    print(round(toko_sell_fee,5))
    print('Sell Loss/Profit:')
    print(round(toko_final_asset,5))
    
if __name__ == "__main__":
    actual_usdt = 5
    funding_fee = 0.01
    leverage = 125
    fee_maker_taker = 0.05
    
    hourly_funding_fee = 8
    hour_sell = 24 * 3
    
    cyle_pay = hour_sell//hourly_funding_fee
    
    tp_percent = 3
    stop_loss = 1
    tp_lv_percentage = tp_percent * leverage
    
    binanceProfitFuture(actual_usdt,funding_fee,cyle_pay,leverage,tp_lv_percentage,fee_maker_taker,stop_loss)
    
    tp = 10

    toko_usdt = 100
    # tokoProfitSpot(toko_usdt,tp)
    
    
    
    
