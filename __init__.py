import ccxtclass.ccxtClass as ccxtClass
import markets.marketObj as markets
import telegrambot.telegramBot as tel
import exceldb.excelDB as DB

test1 = ccxtClass.ccxtClass(markets.list, markets.obj, 'ETC/KRW')





if __name__ == '__main__':
    test1.get_coin_price()
    test1.calculate_per()
    test1.get_account_info()
    test1.count_sell_coin()
    test1.count_buy_coin()
    test1.print_all()


    print('start')