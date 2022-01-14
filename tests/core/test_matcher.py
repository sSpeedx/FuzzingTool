import unittest
import operator

from src.fuzzingtool.core.matcher import Matcher
from src.fuzzingtool.objects.result import Result
from src.fuzzingtool.exceptions.main_exceptions import BadArgumentType
from ..mock_utils.response_mock import ResponseMock


class TestMatcher(unittest.TestCase):
    def test_build_allowed_status_without_status(self):
        return_expected = {
            'is_default': True,
            'list': [200],
            'range': []
        }
        returned_allowed_status_dict = Matcher._Matcher__build_allowed_status(Matcher, None)
        self.assertIsInstance(returned_allowed_status_dict, dict)
        self.assertDictEqual(returned_allowed_status_dict, return_expected)

    def test_build_allowed_status_with_list_and_range(self):
        return_expected = {
            'is_default': False,
            'list': [401, 403],
            'range': [200, 399]
        }
        returned_allowed_status_dict = Matcher._Matcher__build_allowed_status(Matcher, "200-399,401,403")
        self.assertIsInstance(returned_allowed_status_dict, dict)
        self.assertDictEqual(returned_allowed_status_dict, return_expected)

    def test_build_allowed_status_with_inverted_range(self):
        return_expected = {
            'is_default': False,
            'list': [],
            'range': [200, 399]
        }
        returned_allowed_status_dict = Matcher._Matcher__build_allowed_status(Matcher, "399-200")
        self.assertIsInstance(returned_allowed_status_dict, dict)
        self.assertDictEqual(returned_allowed_status_dict, return_expected)

    def test_build_allowed_status_with_invalid_status_type(self):
        test_status = "200-399a"
        with self.assertRaises(BadArgumentType) as e:
            Matcher._Matcher__build_allowed_status(Matcher, test_status)
        self.assertEqual(str(e.exception), f"The match status argument ({test_status}) must be integer")

    def test_get_comparator_and_callback_with_operator_ge(self):
        return_expected = ('25', operator.ge)
        returned_data = Matcher._Matcher__get_comparator_and_callback(Matcher, '>=25')
        self.assertIsInstance(returned_data, tuple)
        self.assertTupleEqual(returned_data, return_expected)

    def test_get_comparator_and_callback_with_operator_le(self):
        return_expected = ('25', operator.le)
        returned_data = Matcher._Matcher__get_comparator_and_callback(Matcher, '<=25')
        self.assertIsInstance(returned_data, tuple)
        self.assertTupleEqual(returned_data, return_expected)

    def test_get_comparator_and_callback_with_operator_gt(self):
        return_expected = ('25', operator.gt)
        returned_data = Matcher._Matcher__get_comparator_and_callback(Matcher, '>25')
        self.assertIsInstance(returned_data, tuple)
        self.assertTupleEqual(returned_data, return_expected)

    def test_get_comparator_and_callback_with_operator_lt(self):
        return_expected = ('25', operator.lt)
        returned_data = Matcher._Matcher__get_comparator_and_callback(Matcher, '<25')
        self.assertIsInstance(returned_data, tuple)
        self.assertTupleEqual(returned_data, return_expected)

    def test_get_comparator_and_callback_with_operator_eq(self):
        return_expected = ('25', operator.eq)
        returned_data = Matcher._Matcher__get_comparator_and_callback(Matcher, '==25')
        self.assertIsInstance(returned_data, tuple)
        self.assertTupleEqual(returned_data, return_expected)

    def test_get_comparator_and_callback_with_operator_ne(self):
        return_expected = ('25', operator.ne)
        returned_data = Matcher._Matcher__get_comparator_and_callback(Matcher, '!=25')
        self.assertIsInstance(returned_data, tuple)
        self.assertTupleEqual(returned_data, return_expected)

    def test_get_comparator_and_callback_without_operator(self):
        return_expected = ('25', operator.gt)
        returned_data = Matcher._Matcher__get_comparator_and_callback(Matcher, '25')
        self.assertIsInstance(returned_data, tuple)
        self.assertTupleEqual(returned_data, return_expected)

    def test_instance_comparator(self):
        return_expected = (25, operator.gt)
        returned_data = Matcher()._Matcher__instance_comparator(int, None, '25')
        self.assertIsInstance(returned_data, tuple)
        self.assertTupleEqual(returned_data, return_expected)

    def test_instance_comparator_with_invalid_integer(self):
        test_name = "test_name"
        test_value = "25test"
        with self.assertRaises(BadArgumentType) as e:
            Matcher()._Matcher__instance_comparator(int, test_name, test_value)
        self.assertEqual(str(e.exception), f"The {test_name} comparator must be an integer, not '{test_value}'!")

    def test_instance_comparator_with_invalid_number(self):
        test_name = "test_name"
        test_value = "25test"
        with self.assertRaises(BadArgumentType) as e:
            Matcher()._Matcher__instance_comparator(float, test_name, test_value)
        self.assertEqual(str(e.exception), f"The {test_name} comparator must be a number, not '{test_value}'!")

    def test_build_comparator(self):
        return_expected = {
            'time': 15,
            'size': 1500,
            'words': 50,
            'lines': 100,
        }
        returned_comparator = Matcher(
            time="15",
            size=">1500",
            words="!=50",
            lines="<100"
        )._Matcher__build_comparator(
            time="15",
            size=">1500",
            words="!=50",
            lines="<100"
        )
        self.assertIsInstance(returned_comparator, dict)
        self.assertDictEqual(returned_comparator, return_expected)

    def test_comparator_is_set_with_set(self):
        return_expected = True
        returned_data = Matcher(size='55').comparator_is_set()
        self.assertIsInstance(returned_data, bool)
        self.assertEqual(returned_data, return_expected)

    def test_comparator_is_set_without_set(self):
        return_expected = False
        returned_data = Matcher().comparator_is_set()
        self.assertIsInstance(returned_data, bool)
        self.assertEqual(returned_data, return_expected)

    def test_match_status_with_match(self):
        return_expected = True
        test_result = Result(response=ResponseMock())
        returned_match_flag = Matcher(
            allowed_status="200",
        ).match(test_result)
        self.assertIsInstance(returned_match_flag, bool)
        self.assertEqual(returned_match_flag, return_expected)

    def test_match_status_without_match(self):
        return_expected = False
        test_result = Result(response=ResponseMock())
        returned_match_flag = Matcher(
            allowed_status="401",
        ).match(test_result)
        self.assertIsInstance(returned_match_flag, bool)
        self.assertEqual(returned_match_flag, return_expected)

    def test_match_time(self):
        return_expected = True
        test_result = Result(response=ResponseMock(), rtt=3.0)
        returned_match_flag = Matcher(
            allowed_status="200",
            time="<=4"
        ).match(test_result)
        self.assertIsInstance(returned_match_flag, bool)
        self.assertEqual(returned_match_flag, return_expected)

    def test_match_size(self):
        return_expected = True
        test_result = Result(response=ResponseMock())
        returned_match_flag = Matcher(
            allowed_status="200",
            size=">=10",
        ).match(test_result)
        self.assertIsInstance(returned_match_flag, bool)
        self.assertEqual(returned_match_flag, return_expected)

    def test_match_words(self):
        return_expected = False
        test_result = Result(response=ResponseMock(), rtt=3.0)
        returned_match_flag = Matcher(
            allowed_status="200",
            words="<=4"
        ).match(test_result)
        self.assertIsInstance(returned_match_flag, bool)
        self.assertEqual(returned_match_flag, return_expected)

    def test_match_lines(self):
        return_expected = True
        test_result = Result(response=ResponseMock(), rtt=3.0)
        returned_match_flag = Matcher(
            allowed_status="200",
            lines="==2"
        ).match(test_result)
        self.assertIsInstance(returned_match_flag, bool)
        self.assertEqual(returned_match_flag, return_expected)
