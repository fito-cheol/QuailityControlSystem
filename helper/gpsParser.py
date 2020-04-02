import re

class NmeaGsvMessage:

    strings_to_remove = ['start', ' ', '@', '\n']
    strings_to_contain = ['$', '*']
    delimiters = [",", "\*"]

    accepted_satelite = {'GPGSV': [1,3,22,50],
                         'GLGSV': [71, 86]}
    result = {
        'GPGSV': {
            "sum_snr": 0,
            "num_line":0,
        },
        'GLGSV': {
            "sum_snr": 0,
            "num_line":0,
        },
    }

    def __init__(self, lines=None):
        self.current_line = ""
        self.satelite_buffer_list = []
        self.parsed_satelite_data = []

        if lines:
            self.set_data(lines)

    def set_data(self, lines):
        self.current_line = ""
        self.satelite_buffer_list = []
        self.parsed_satelite_data = []
        for line in lines:
            self.analyze_line(line)

        if self.satelite_buffer_list:
            self.flush_out_buffer()


    def analyze_line(self, line):
        self.current_line = line
        self.filter_line()

        if self.is_valid_line():
            if self.should_flush_before():
                self.flush_out_buffer()

            self.add_buffer()

            if self.should_flush_after():
                self.flush_out_buffer()

    def filter_line(self):
        line_to_filter = self.current_line

        for string_to_remove in self.strings_to_remove:
            line_to_filter.replace(string_to_remove, '')

        self.current_line = line_to_filter

    def is_valid_line(self):
        line_to_check_valid = self.current_line

        is_message_accepted = False
        for accepted_channel in self.accepted_satelite:
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
                satelite_num = int(splited_line[i-3])
                snr_num = int(splited_line[i])
                if satelite_num in self.accepted_satelite[channel]:
                    satelite_buffer = Satelite(channel, satelite_num, snr_num)
                    self.satelite_buffer_list.append(satelite_buffer)
            except:
                continue

    def should_flush_before(self):
        splited_line = re.split("|".join(self.delimiters), self.current_line)
        if self.satelite_buffer_list and splited_line[2] == 1:
            return True
        return False

    def should_flush_after(self):
        splited_line = re.split("|".join(self.delimiters), self.current_line)
        # 마지막 줄인 경우
        if splited_line[1] == splited_line[2]:
            return True

        return False

    def flush_out_buffer(self):

        self.parsed_satelite_data.append(self.satelite_buffer_list)
        self.satelite_buffer_list = []

    def show_result(self):
        self.prepare_result()
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

    def prepare_result(self):
        self.result = {}
        for channel in self.accepted_satelite:
            self.result[channel] = {}
            for satelite_num in self.accepted_satelite[channel]:
                self.result[channel][satelite_num] = {
                    "snr_sum": 0,
                    "line_num": 0,
                }

        for satelite_list in self.parsed_satelite_data:
            for satelite_object in satelite_list:
                self.add_satelite_to_result(satelite_object)


    def add_satelite_to_result(self, satelite_object):

        channel = satelite_object.channel
        satelite_num = satelite_object.satelite_num
        snr_num = satelite_object.snr_num

        existing_result = self.result[channel][satelite_num]

        existing_result['snr_sum'] += snr_num
        existing_result['line_num'] += 1


class Satelite:

    def __init__(self, channel, satelite_num, snr_num):
        self.channel = channel
        self.satelite_num = satelite_num
        self.snr_num = snr_num

    def __eq__(self, other_number):
        return self.satelite_num == other_number



if __name__ == '__main__':
    pass