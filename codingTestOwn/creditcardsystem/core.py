# -*- coding: utf-8 -*-
import re
import sys
from creditcardsystem.logger import loggers
from decimal import Decimal

loggings = loggers("Hansangyoon")

class Core(object):

    def __init__(self, *args, **kwargs):
        self.db = kwargs.get("db", {})

        if not isinstance(self.db, dict):
            raise TypeError("데이터베이스는 딕셔너리 형태이어야 합니다.")

    def parse_event(self, event):
        '''
        하나의 event 값을 3개의 구성 요소(event_type, name, numbers)로 분리.
        :param event:
        :return:
        '''
        if not isinstance(event, str):
            raise ValueError("이벤트 타입은 string 타입이어야 합니다")

        # *numbers: 인자의 갯수가 명확하지 않을 때, 가변적 파라미터를 넘겨야 하는 경우 사용.
        event_type, name, *numbers = event.split()

        if not numbers:
            raise Exception(
                "numbers 구문 분석에서 오류가 발생했습니다. "
                "이벤트 타입, 이름, 그리고 추가 정보: {0}가 필요합니다. ".format(numbers))

        args = map(self.parse_dollar, numbers)

        # 이벤트 타입에 따른 core 함수 호출
        method = getattr(self, event_type.lower())
        method(name, *args)


    @staticmethod
    def parse_dollar(number):

        '''
        number 값에 어떤 값이 들어올지 모르는 상황에서(카드번호, 또는 한도금액)
        한도 금액이 들어 올 경우, '$' 표시를 제거하고 반환,
        카드 번호가 들어올 경우, numeric type인지를 검증 후 반환.

        :param number:
        :return:
        '''

        if not re.match(r'[$+-]?(\d+(\.\d*)?|\.\d+)', number):
            raise ValueError("number는 숫자(numberic)이어야 합니다.")

        if '$' in number:
            return Decimal(number.strip('$'))
        else:
            return number



    #Add, Charge, Credit
    def add(self, name, card_number, limit):
        '''
        새로운 카드 번호를 등록한다.
        카드 번호가 유효한 번호인지 luhn 알고리즘을 통해서 검증한다.

        :param name:
        :param card_number:
        :param limit:
        :return:
        '''

        loggings.info("신규 카드 등록, 번호:{0}, 이름:{1}, 한도:{2}".format(card_number, name, limit))

        if self.is_luhn_valid(card_number):
            balance = Decimal(0)
        else:
            loggings.warning("유효하지 않은 카드번호: {0}".format(card_number))
            balance = 'error'


        self.db[name] = {'card_number': card_number, 'limit': limit, 'balance': balance}

    def charge(self, name, amount):
        '''
        특정 사용자에게 일정 금액을 계좌를 통해서 부과한다.
        카드 번호 유효성을 검증한다.

        :param name:
        :param amount:
        :return:
        '''

        loggings.info("Charging {0} {1}".format(name, amount))

        self.check_amount(amount)

        account, balance, card_number, limit = self.get_account_details(name)

        if not self.is_luhn_valid(card_number) or amount + balance > limit:
            return balance

        account['balance'] += amount


    def credit(self, name, amount):
        '''
        특정 사용자의 계좌에 일정 금액을 보장하여 보전함.

        :param name:
        :param amount:
        :return:
        '''
        loggings.info("{0}에게 {1}를 보장함.".format(name, amount))
        self.check_amount(amount)

        account, balance, card_number, limit = self.get_account_details(name)

        if not self.is_luhn_valid(card_number):
            return balance

        account = self.db.get(name, None)
        account['balance'] -= amount


    @staticmethod
    def check_amount(amount):
        '''
        금액 값이 Decimal 타입인지를 검증
        :param amount:
        :return:
        '''
        if not isinstance(amount, Decimal):
            raise TypeError(
                "유효하지 않은 파라미터 타입임. amount={0} 는 반드시 Decimal 타입이어야 함.".format(type(amount))
            )

    def get_account_details(self, name):
        '''
        사용자의 계좌에 대한 상세 내용을 추출.
        account, balance, card_number, limit = self.get_account_details(name)

        :param name:
        :return:
        '''

        try:
            account = self.db[name]
        except KeyError as e:
            loggings.error("계좌가 존재하지 않습니다.")

            raise

        if not isinstance(name, str):
            raise TypeError(
                "유효하지 않은 파라미터 타입입니다. name={0} 은 반드시 string타입이어야 합니다.".format(type(name))
            )

        balance = account.get('balance', None)
        card_number = account.get('card_number', None)
        limit = account.get('limit', None)

        # 놓친 파라미터 있는지를 확인
        if any(param is None for param in [balance, card_number, limit]):
            raise KeyError(
                '카드값을 부과하기 위해 필요한 파라미터들 즉, 잔액={0}, 카드번호={1}, 한도={2} 들 중 '
                '누락 된 것을 확인하세요.'.format(balance, card_number, limit)
            )

        return account, balance, card_number, limit

    def generate_totalInfo(self):

        '''
        output을 위한 string 결과값을 생성.
        name은 알파벳 순서.
        dollar 값에는 $ 기호 붙여서 기록.
        한줄 한줄 기록됨.
        :return:
        '''

        totinfo = ''
        for key in sorted(self.db.keys()):
            balance = '${0}'.format(self.db[key].get('balance'))

            if 'error' in balance:
                balance = balance.strip('$')

            totinfo += '{0}: {1}\n'.format(key, balance)

        return totinfo


    @staticmethod
    def write_outputStringVal(totalStringValueInfo):
        '''
        STDOUT 값을 출력하기 위한 함수

        :param totalStringValueInfo:
        :return:
        '''
        sys.stdout.write(totalStringValueInfo)


    @staticmethod
    def luhn_checksum(card_number):
        '''
        Luhn algorithm
        :param card_number:
        :return:
        '''

        def digit_of(n):
            return [int(d) for d in str(n)]

        digits = digit_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]

        check_sum = 0

        check_sum += sum(odd_digits)

        for a in even_digits:
            check_sum += sum(digit_of(a * 2))

        return check_sum % 10


    def is_luhn_valid(self, card_number):
        '''
        카드 번호가 유효한지를 테스트

        :param card_number:
        :return:
        '''

        return self.luhn_checksum(card_number) == 0











