import os


from helper.gpsParser import NmeaGsvMessage


class Cell:

    def __init__(self, widget):
        self.widget = widget
        self.serial_number = 0
        self.file_path = ""
        self.status = "WAITING"
        self.result_dict = None
        self.snr_criteria = 30

    def initialize(self):
        self.serial_number = 0
        self.file_path = ""
        self.status = "WAITING"
        self.result_dict = None
        self.widget["bg"] = 'white'

        self.update_widget()

    def __eq__(self, number):
        return self.serial_number == number

    def set_file(self, file_path):
        self.file_path = file_path
        base = os.path.basename(file_path)
        filename = os.path.splitext(base)[0]
        self.serial_number = int(filename.split('_')[0])
        self.update_widget()

    def process_GPGSV(self):
        return self.process({'GPGSV': [1, 3, 22, 50]})

    def process_GLGSV(self):
        return self.process({'GLGSV': [71, 86]})

    def process(self, accepted_satellite=None):
        if not self.file_path:
            return None

        with open(self.file_path, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            object_nmea = NmeaGsvMessage()
            if accepted_satellite:
                object_nmea.accepted_satellite = accepted_satellite
            object_nmea.set_data(lines)
            self.result_dict = object_nmea.get_result()

    def get_stringify_result(self):
        # ex) CLBX-20010 GP 36 36 36 35, GL 33 36 PASS
        result_string = "CLBX-{}".format(str(self.serial_number).zfill(5))
        is_pass = True
        for channel in self.result_dict:
            added_string = " " + channel
            for satellite_num in self.result_dict[channel]:
                selected_satellite = self.result_dict[channel][satellite_num]
                snr_average = round(selected_satellite['snr_sum'] / selected_satellite['line_num'], 2)
                added_string += " " + str(snr_average)
                if snr_average < self.snr_criteria:
                    is_pass = False
            result_string += added_string

        if is_pass:
            result_string += " PASS"
        else:
            result_string += " FAIL"

        return result_string

    def get_table_parsed_result(self):
        #
        # [serial_number, channel, satellite_num, snr_average]
        result_table = []
        self.serial_number

        for channel in self.result_dict:
            for satellite_num in self.result_dict[channel]:
                selected_satellite = self.result_dict[channel][satellite_num]
                snr_average = round(selected_satellite['snr_sum'] / selected_satellite['line_num'], 2)
                row = [self.serial_number, channel, satellite_num, snr_average]
                result_table.append(row)

        return result_table

    def change_status(self, status="Waiting"):
        self.status = status
        self.update_widget()

    def update_widget(self):
        # 위젯의 글자와 색을 바꿔준다
        if self.serial_number:
            self.widget["text"] = "CLBX-" + str(self.serial_number) + "\n" + self.status
        else:
            self.widget["text"] = "\n" + self.status

        if self.status == 'WAITING':
            self.widget["bg"] = 'white'
        elif self.status == 'Pass':
            self.widget["bg"] = 'blue'
        else:
            self.widget["bg"] = 'red'
