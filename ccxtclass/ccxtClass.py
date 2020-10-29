import ccxt

class ccxtClass():

    def __init__(self, site_list, site_apikey, coinname):
        self.gap = 2
        self.now_gap = 0
        ##################################
        self.markets_list = site_list            ## 거래소 리스트
        self.markets_apikey = site_apikey        ## 거래소 api 키 딕셔너리
        self.markets_obj_dict = {}               ## 거래소 load 후 객체 할당
        self.coin_name = coinname                ## 거래 할 코인 이름
        ##################################
        self.buy_market_name = ''                ## 구매 해야 할 거래소 이름
        self.buy_price = 0                       ## 구매 시 코인 가격
        self.buy_order_info = {}                 ## 구매 주문 정보 --> 구조 {'marketname': ['id',...]}
        self.buy_coin_amount = 0                 ## 구매 코인량
        ##################################
        self.sell_market_name = ''               ## 판매 해야 할 거래소 이름
        self.sell_price = 0                      ## 판매 시 코인 가격
        self.sell_order_info = {}                ## 판매 주문 정보 --> 구조 {'marketname': ['id',...]}
        self.sell_coin_amount = 0                ## 판매 코인량
        ##################################
        self.init_account = {}                   ## 초기 계좌 정보 --> 구조 {'marketname': [시드,코인]}
        self.account = {}                        ## 거래 후 계좌 정보 --> 구조 {'marketname': [시드,코인]}
        ##################################
        self.trade_check_telbot = [True, True]   ## 텔레그램 메세지 체그 [시드 차이, 코인 차이]
        self.trade_gap_check = False             ## 2% 갭 확인 후 거래 체크
        ##################################
        self._init_account_setting()             ## 처음 계좌 셋팅 함수
        self._init_load_coin_markets()           ## 거래소 load 함수
        self._init_get_account_info()            ## 거래 시작 시 계좌 정보

######################################################################


    #계좌, 주문내역 리스트 초기 설정
    def _init_account_setting(self):
        for market in self.markets_list:
            self.init_account[market] = [0, 0]  #[시드, 코인]
            self.account[market] = [0, 0]       #[시드, 코인]
            self.buy_order_info[market] = []
            self.sell_order_info[market] = []
    #거래소 api 오픈 초기 설정
    def _init_load_coin_markets(self):
        for list in self.markets_list:
            market = getattr(ccxt, list)(self.markets_apikey[list])
            self.markets_obj_dict[list] = market
        if len(self.markets_obj_dict) > 0:
            print('load markets')


######################################################################

    ####@ step 1 @####
    def get_coin_price(self):
        small_dict = dict()
        for key, val in self.markets_obj_dict.items():
            fetch_info = val.fetch_order_book(self.coin_name)
            '''
            buy_first = fetch_info['bids'][0][0] #매도 1호
            sell_first = fetch_info['asks'][0][0] #매수 1호
            small_dict[key] = {
                'buy': buy_first,
                'sell': sell_first
            }
            '''
            if len(fetch_info['bids']) > 0:
                buy_first = fetch_info['bids'][0][0]  ## 매도 1호
                sell_first = fetch_info['asks'][0][0]  ## 매수 1호

            else:
                buy_first = val.fetch_trades(self.coin_name, limit=1)[0]['price']  ## 매도 1호
                sell_first = val.fetch_trades(self.coin_name, limit=1)[0]['price']  ## 매수 1호
            small_dict[key] = {
                "buy": buy_first,
                "sell": sell_first
            }
        self.buy_market_name = min(small_dict, key=lambda k: small_dict[k]["sell"])  ##제일 싸게 파는 거래소
        self.sell_market_name = max(small_dict, key=lambda k: small_dict[k]["buy"])  ##제일 비싸게 사는 거래소
        if self.buy_market_name == self.sell_market_name:
            self.sell_market_name = sorted(small_dict, key=lambda k: small_dict[k]["sell"], reverse=True)[1]
        self.buy_price = small_dict[self.buy_market_name]['buy']
        self.sell_price = small_dict[self.sell_market_name]['sell']
        #per = (small_dict[sell_max_site]["sell"] - small_dict[buy_min_site]["buy"]) / small_dict[sell_max_site]["sell"] * 100


######################################################################
    ####@ step 2 @####
    def calculate_per(self):
        per = (self.sell_price-self.buy_price)/self.sell_price * 100
        self.now_gap = per
        if per > self.gap:
            self.trade_gap_check = True
        else:
            self.trade_gap_check = False

    ####@ step 3 @####
    def count_buy_coin(self):
        cnt = float(self.init_account[self.buy_market_name][0]) / self.buy_price / 2   ## 살 때는 계좌 잔액의 절반
        self.buy_coin_amount = cnt

    ####@ step 3 @####
    def count_sell_coin(self):
        cnt = float(self.init_account[self.sell_market_name][0]) / self.sell_price ## 팔 때는 전부
        self.sell_coin_amount = cnt

######################################################################
    ####@ step 4 @####
    def order_buy_coin(self):
        if self.trade_gap_check & self.trade_check_telbot[0] & self.trade_check_telbot[1]:
            try:
                order = self.markets_obj_dict[self.buy_market_name].create_limit_buy_order(self.coin_name, self.buy_coin_amount, self.buy_price)
                self.buy_order_info[self.buy_market_name].append(order)  ####@ step 4-1 @####
            except Exception as e:
                print('erorr def count_buy_coin %s' %e)

    ####@ step 4 @####
    def order_sell_coin(self):
        if self.trade_gap_check & self.trade_check_telbot[0] & self.trade_check_telbot[1]:
            try:
                order = self.markets_obj_dict[self.sell_market_name].create_limit_sell_order(self.coin_name, self.sell_coin_amount, self.sell_price)
                self.sell_order_info[self.sell_market_name].append(order)  ####@ step 4-1 @####
            except Exception as e:
                print('erorr def count_sell_coin %s' %e)

######################################################################


    ########################계좌 관련 데이터는 거래소별로 다르기때문에 거래소가 바뀔경우 수정해야함 ############################


    ##계좌 조회
    def _init_get_account_info(self):
        for marketname, marketobj in self.markets_obj_dict.items():
            bal = marketobj.fetch_balance()
            if 'data' in bal['info']:
                _bal = [bal['info']['data']['total_krw'], bal['info']['data']['total_etc']]
            else:
                _bal = [bal['KRW']['total'], bal['ETC']['total']]
            self.init_account[marketname] = _bal

    ####@ step 1 @####
    def get_account_info(self):
        for marketname, marketobj in self.markets_obj_dict.items():
            bal = marketobj.fetch_balance()
            if 'data' in bal['info']:
                _bal = [bal['info']['data']['total_krw'], bal['info']['data']['total_etc']]
            else:
                _bal = [bal['KRW']['total'], bal['ETC']['total']]
            self.account[marketname] = _bal

    ####@ step 2 @####
    def account_gap_check(self):
        buy_curr = self.init_account[self.buy_market_name][0]
        sell_curr =self.account[self.sell_market_name][0]
        if buy_curr/2 <= sell_curr:
            self.trade_check_telbot[0] = False
        else:
            self.trade_check_telbot[0] = True
        #buy_coin = self.init_account[self.buy_market_name][1]
        sell_coin = self.account[self.sell_market_name][1]
        if sell_coin<5:
            self.trade_check_telbot[1] = False
        else:
            self.trade_check_telbot[1] = True


######################################################################
    ####@ step 5 @####
    #주문 체결 확인하기
    def book_order_check_fail_success(self, order_info):
        for list in self.markets_list:
            if len(order_info[list]) > 0:
                for id in order_info[list]:
                    info = self.markets_obj_dict[list].fetch_order(id, self.coin_name)['info']
                    if 'order_status' in info:
                        check = info['order_status']
                        if check == 'Completed':
                            order_info[list].remove(id)
                        else:
                            pass
                    else:
                        check = info['state']
                        if check == 'done':
                            order_info[list].remove(id)
                        else:
                            pass

    ####@ step 5-1 @####
    #주문 취소 수정
    def book_check_cancel_edit(self):
        for marketname, marketobj  in self.markets_obj_dict.items():
            #주문량이 5보다 작으면 주문수정
            if len(self.buy_order_info[marketname]) < 5:                              #'limit'대신'market'일경우 시장가로들어감
                marketobj.edit_order(self.buy_order_info[marketname][0], self.coin_name, 'limit', 'buy', '갯수', '가격')
            else:
                marketobj.cancel_order(self.buy_order_info[marketname][0], self.coin_name)
            if len(self.sell_order_info[marketname]) < 5:                              #'limit'대신'market'일경우 시장가로들어감
                marketobj.edit_order(self.sell_order_info[marketname][0], self.coin_name, 'limit', 'sell', '갯수', '가격')
            else:
                marketobj.cancel_order(self.sell_order_info[marketname][0], self.coin_name)

# if self.account[self.buy_market_name][0] > self.init_account[self.buy_market_name][0]/2:


###########################################################################
    def print_all(self):
        print(
        ' 갭 :', self.gap, '\n',
        '현재 갭 :' ,self.now_gap, '\n',
        '거래소 리스트 :', self.markets_list, '\n',
        '거래소 api키 :', self.markets_apikey, '\n',
        '거래소 오브젝트 :', self.markets_obj_dict, '\n',
        '코인 이름 :', self.coin_name, '\n',
        '사는 거래소 이름 :', self.buy_market_name, '\n',
        '살 때 코인 가격 :', self.buy_price, '\n',
        '산 주문 내역 :', self.buy_order_info, '\n',
        '사야하는 코인 양 :', self.buy_coin_amount, '\n',
        '파는 거래소 이름 :', self.sell_market_name, '\n',
        '팔 때 코인 가격 :', self.sell_price, '\n',
        '판 주문 내역 :', self.sell_order_info, '\n',
        '팔아야하는 코인 양 :', self.sell_coin_amount, '\n',
        '처음 계좌 잔액 :', self.init_account, '\n',
        '거래 후 계좌 잔액 :', self.account, '\n',
        '트레이드 체크 :', self.trade_check_telbot, '\n',
        '갭 체크 :', self.trade_gap_check, '\n',
        )

