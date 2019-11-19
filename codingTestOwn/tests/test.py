import sys
from os import path
import unittest
from decimal import Decimal
from creditcardsystem.core import Core

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

class Testing(unittest.TestCase):
    def setUp(self):
        self.core = Core()

    # event 파싱
    def test_event_is_string(self):
        self.assertRaises(ValueError, self.core.parse_event, 0)

    def test_parse_event_can_upack_string(self):
        self.assertRaises(ValueError, self.core.parse_event, 'Add')

    def test_parse_event_has_vaild_args(self):
        self.assertRaises(Exception, self.core.parse_event, 'Add Evan')

    def test_parse_dollars_has_valid_number(self):
        self.assertRaises(ValueError, self.core.parse_dollar, '$fail')

    def test_parse_dollars_returns_valid_card_number(self):
        self.assertTrue(self.core.parse_dollar('4111111111111111').isdigit())


    #Luhn10
    def test_card_number_is_numeric_in_luhn_checksum(self):
        self.assertRaises(ValueError, self.core.luhn_checksum, 'fail')

    def test_card_number_is_numeric_in_is_luhn_valid(self):
        self.assertRaises(ValueError, self.core.is_luhn_valid, 'fail')

    def test_luhn_catches_invalid_invalid_number(self):
        self.assertFalse(self.core.is_luhn_valid('1234567890123456'))


    # Add
    def test_invalid_card_balance_equals_error(self):
        self.core.add('User', '1234567890123456', '$4000')
        self.assertEqual(self.core.db['User']['balance'], 'error')

    def test_balance_type_is_decimal(self):
        self.core.add('User', '4111111111111111', '$4000')
        self.assertIsInstance(self.core.db['User']['balance'], Decimal)


    # about Account
    def test_nonexistant_account_name_raises_key_error(self):
        self.assertRaises(KeyError, self.core.get_account_details, '계정이 존재하지 않음.')

    def test_missing_param_raises_key_error(self):
        self.core.db['User'] = {'card_number': '4111111111111111', 'limit': '$5000', 'balance': None}
        self.assertRaises(KeyError, self.core.get_account_details, 'User')


    # Charge
    def test_charge_with_bad_params_raises_type_error(self):
        self.core.db['User'] = {
            'card_number': '4111111111111111', 'limit': Decimal('9000'), 'balance': Decimal('9000')
        }

        self.assertRaises(TypeError, self.core.charge, 'User', '$1000')

    def test_amount_over_limit_doesnt_charge(self):
        self.core.db['User'] = {
            'card_number': '4111111111111111', 'limit': Decimal('9000'), 'balance': Decimal('9000')
        }

        self.assertEqual(self.core.charge('User', Decimal('1')), Decimal('9000'))

    def test_invalid_card_is_not_charged(self):
        self.core.add('User', '1234567890123456', Decimal('9000'))
        self.assertEqual(self.core.charge('User', Decimal('1')), 'error')

    def test_credit_correctly_decreases_balance(self):
        self.core.add('User', '4111111111111111', Decimal('9000'))
        self.core.credit('User', Decimal('9000'))


    # Credit
    def test_credit_with_bad_params_raises_type_error(self):
        self.core.db['User'] = {
            'card_number': '4111111111111111', 'limit': Decimal('9000'), 'balance': Decimal('9000')
        }
        self.assertRaises(TypeError, self.core.credit, 'User', '$1000')

    def test_invalid_card_is_not_credited(self):
        self.core.add('User', '1234567890123456', Decimal('9000'))
        self.assertEqual(self.core.credit('User', Decimal('1')), 'error')

if __name__ == '__main__':
    unittest.main()