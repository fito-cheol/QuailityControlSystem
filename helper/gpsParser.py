import re

class NmeaGsvMessage:

    strings_to_remove = ['start', ' ', '@', '\n']
    strings_to_contain = ['$', '*']
    delimiters = [",", "\*"]
    accepted_messages = ['GPGSV', 'GLGSV']

    def __init__(self, lines=None):
        self.current_line = ""
        self.data_buffer = []
        self.analyzed_data = []

        if lines:
            self.set_data(lines)

    def set_data(self, lines):
        self.current_line = ""
        self.data_buffer = []
        self.analyzed_data = []
        for line in lines:
            self.analyze_line(line)

        if self.data_buffer:
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
        for accepted_message in self.accepted_messages:
            if line_to_check_valid.__contains__(accepted_message):
                is_message_accepted = True;

        if not is_message_accepted:
            return False

        for string_to_contain in self.strings_to_contain:
            if not line_to_check_valid.__contains__(string_to_contain):
                return False

        return True

    def add_buffer(self):
        splited_line = re.split("|".join(self.delimiters), self.current_line)

        for i in range(4, len(splited_line)-1, 4):
            try:
                buffer = int(splited_line[i])
                self.data_buffer.append(buffer)
            except:
                continue

    def should_flush_before(self):
        splited_line = re.split("|".join(self.delimiters), self.current_line)
        if self.data_buffer and splited_line[2] == 1:
            return True
        return False

    def should_flush_after(self):
        splited_line = re.split("|".join(self.delimiters), self.current_line)
        # 마지막 줄인 경우
        if splited_line[1] == splited_line[2]:
            return True

        return False

    def flush_out_buffer(self):

        self.analyzed_data.append(self.data_buffer)
        self.data_buffer = []

    def show_result(self):

        line_count = len(self.analyzed_data)

        sum_SNR_value = 0
        sum_satellite_number = 0
        for SNR_value_list in self.analyzed_data:
            if SNR_value_list:
                sum_SNR_value += sum(SNR_value_list)/len(SNR_value_list)
                sum_satellite_number += len(SNR_value_list)

        average_SNR_value = sum_SNR_value/ line_count
        average_satellite_number = sum_satellite_number / line_count

        result = "총 라인 수, {}, 평균 SNR 값, {}, 위성 갯수 평균, {}".format(line_count, format(average_SNR_value,'.3f'),
                                                                 format(average_satellite_number,'.3f'))
        return result

