# parser_factory.py
from parser_format1 import parse_format_1
from parser_format2 import parse_format_2
from parser_format3 import parse_format_3
from parser_format4 import parse_format_4
from parser_format5 import parse_format_5
from parser_format6 import parse_format_6

def get_parser(format_type):
    parsers = {
        1: parse_format_1,
        2: parse_format_2,
        3: parse_format_3,
        4: parse_format_4,
        5: parse_format_5,
        6: parse_format_6,
    }
    return parsers.get(format_type) 