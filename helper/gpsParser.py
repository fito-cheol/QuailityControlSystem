import re

class NmeaGsvMessage:

    strings_to_remove = ['start', ' ', '@', '\n']
    strings_to_contain = ['$', '*']
    delimiters = [",", "\*"]

    accepted_satellite = {'GPGSV': [1,3,22,50],
                         'GLGSV': [71, 86]}

    current_line = ""
    satellite_buffer_list = []
    parsed_satellite_data = []
    result = {
        'GPGSV': {
            1: {
                "sum_snr": 0,
                "num_line":0,
            },
            3: {
                "sum_snr": 0,
                "num_line": 0,
            }

        },
        'GLGSV': {
            71: {
                "sum_snr": 0,
                "num_line":0,
            },
            86: {
                "sum_snr": 0,
                "num_line": 0,
            },
        },
    }

    def __init__(self, lines=None):
        if lines:
            self.set_data(lines)

    def set_data(self, lines):
        self.current_line = ""
        self.satellite_buffer_list = []
        self.parsed_satellite_data = []

        self.analyze_lines(lines)

    def analyze_lines(self, lines):
        for line in lines:
            self.analyze_line(line)

        # 버퍼 남은거 정리
        if self.satellite_buffer_list:
            self.flush_out_buffer()

    def analyze_line(self, line):
        self.current_line = self.filter_line(line)

        if self.is_valid_line(self.current_line):
            if self.should_flush_before():
                self.flush_out_buffer()

            self.add_buffer()

            if self.should_flush_after():
                self.flush_out_buffer()

    def filter_line(self, line_to_filter):

        for string_to_remove in self.strings_to_remove:
            line_to_filter.replace(string_to_remove, '')

        return line_to_filter

    def is_valid_line(self, line_to_check_valid):

        is_message_accepted = False
        for accepted_channel in self.accepted_satellite:
            if line_to_check_valid.__contains__(accepted_channel):
                is_message_accepted = True;

        if not is_message_accepted:
            return False

        for string_to_contain in self.strings_to_contain:
            if not line_to_check_valid.__contains__(string_to_contain):
                return False

        return True

    def add_buffer(self):
        splited_line = re.split("|".join(self.delimiters), self.current_line)

        for i in range(7, len(splited_line)-1, 4):
            try:
                channel = splited_line[0].replace('$','')
                satellite_num = int(splited_line[i-3])
                snr_num = int(splited_line[i])
                if satellite_num in self.accepted_satellite[channel]:
                    satellite_buffer = Satellite(channel, satellite_num, snr_num)
                    self.satellite_buffer_list.append(satellite_buffer)
            except:
                continue

    def should_flush_before(self):
        splited_line = re.split("|".join(self.delimiters), self.current_line)
        if self.satellite_buffer_list and splited_line[2] == 1:
            return True
        return False

    def should_flush_after(self):
        splited_line = re.split("|".join(self.delimiters), self.current_line)
        # 마지막 줄인 경우
        if splited_line[1] == splited_line[2]:
            return True

        return False

    def flush_out_buffer(self):

        self.parsed_satellite_data.append(self.satellite_buffer_list)
        self.satellite_buffer_list = []

    def get_result(self):
        self.make_result()
        """
        {'GPGSV': {
        1: {'snr_sum': 56577, 'line_num': 1195}, 
        3: {'snr_sum': 62054, 'line_num': 1195}, 
        22: {'snr_sum': 55965, 'line_num': 1195}, 
        50: {'snr_sum': 52859, 'line_num': 1195}}, 
        'GLGSV': {
        71: {'snr_sum': 56978, 'line_num': 1194}, 
        86: {'snr_sum': 57908, 'line_num': 1194}}}
        """
        print(self.result)
        return self.result

    def make_result(self):

        self.make_result_format()

        for satellite_list in self.parsed_satellite_data:
            for satellite_object in satellite_list:
                self.add_satellite_to_result(satellite_object)

    def make_result_format(self):
        """
        input self.accepted_satellite = {'GPGSV': [1,3,22,50],
                                         'GLGSV': [71, 86]}
        output self.result = {
            'GPGSV': {
                1: {
                    "sum_snr": 0,
                    "num_line":0,
                },
                3: {
                    "sum_snr": 0,
                    "num_line": 0,
                }

            },
            'GLGSV': {
                71: {
                    "sum_snr": 0,
                    "num_line":0,
                },
                86: {
                    "sum_snr": 0,
                    "num_line": 0,
                },
            },
        }
        :return: None
        """
        self.result = {}
        for channel in self.accepted_satellite:
            self.result[channel] = {}
            for satellite_num in self.accepted_satellite[channel]:
                self.result[channel][satellite_num] = {
                    "snr_sum": 0,
                    "line_num": 0,
                }


    def add_satellite_to_result(self, satellite_object):

        channel = satellite_object.channel
        satellite_num = satellite_object.satellite_num
        snr_num = satellite_object.snr_num

        existing_result = self.result[channel][satellite_num]

        existing_result['snr_sum'] += snr_num
        existing_result['line_num'] += 1


class Satellite:

    def __init__(self, channel, satellite_num, snr_num):
        self.channel = channel
        self.satellite_num = satellite_num
        self.snr_num = snr_num

    def __eq__(self, other_number):
        return self.satellite_num == other_number

if __name__ == '__main__':
    pass