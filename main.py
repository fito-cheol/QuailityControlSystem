import os
from tkinter import *
import datetime

from tkinter import scrolledtext, messagebox, filedialog
from widgetModel.cell import Cell

"""
결과물은 Serial No, 지정된 GPS 채널(4개), GLONASS 채널(2개)의 1분간의 SNR 평균값, 테스트결과(PASS, FAIL)이 포함되었으면 합니다.
ex) CLBX-20010 GP 36 36 36 35, GL 33 36 PASS

"""

class Application(Frame):
    log_to_show = []
    cell_object_list = []

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.data_directory = "./data"

        self.create_widgets()

    def create_widgets(self):

        # 시작 정지
        img = PhotoImage(file="image/play.jpg")
        self.play = Button(self, command=self.process_data, image=img)
        self.play.image = img
        self.play.grid(row=0, column=0, rowspan=2)

        img = PhotoImage(file="image/stop.jpg")
        self.stop = Button(self,  command=self.stop_process, image=img)
        self.stop.image = img
        self.stop.grid(row=0, column=1, rowspan=2)

        # 로그관련
        self.text_display = scrolledtext.ScrolledText(self, width=120, height=10)
        self.text_display.grid(row=8, column=4, columnspan=10)

        self.clear_text_display_button = Button(self, text="CLEAR LOGS", command=self.clear_text_display)
        self.clear_text_display_button.grid(row=7, column=4)

        self.save_text_display_button = Button(self, text="SAVE LOGS", command=self.save_text_display)
        self.save_text_display_button.grid(row=7, column=5)

        # 셀모양을 배치할 예정 6 X 6
        for i in range(6):
            for j in range(6):
                tmp_widget = Button(self, text="Waiting", fg="black")
                row = 0+i
                column = 4+j
                tmp_widget.grid(row=row, column=column)
                cell_object = Cell(tmp_widget)
                self.cell_object_list.append(cell_object)

    def save_text_display(self):
        print(self.text_display.get(1.0, END))
        pass

    def clear_text_display(self):
        self.text_display.delete(1.0, END)
        pass

    def process_data(self):
        
        # 각 셀 돌면서 초기화
        for cell in self.cell_object_list:
            cell.initialize()
            
        # Cell에 Gp파일 할당하기
        cell_index = 0
        for file_name in os.listdir(self.data_directory):
            try:
                if not file_name.endswith('.gp'):
                    continue
                file_path = os.path.join(self.data_directory, file_name)
                self.cell_object_list[cell_index].set_file(file_path)
                cell_index += 1

            except Exception as e:
                self.save_log("Error - " + e)

        # 각 셀을 순회하면서 process하라고 명령어 날리기
        for cell in self.cell_object_list:
            if cell.serial_number:
                cell.process()
                string_result = cell.get_stringify_result()
                self.save_log(string_result)


    def stop_process(self):
        print('need to develop')

    def save_log(self, log_string):
        dt_now = datetime.datetime.now()
        # string_now = dt_now.strftime("%H  %M  %S ")

        log = log_string + "\n"
        self.log_to_show.append(log)
        self.text_display.insert(INSERT, log)
        print(log_string)

    def show_MessageBox(self, message):
        messagebox.showinfo('Info', message)
        # 여러가지 messagebox type이 있음
        # messagebox.askyesno('Message title','Message content')

    def open_directory_path(self):
        file = filedialog.askdirectory()
        print(file)

    def quit(self):
        self.master.destroy()


if __name__ == '__main__':
    window = Tk()
    window.title("Fitogether Quaility Control System")
    window.geometry("1280x860+100+100")
    app = Application(master=window)
    app.mainloop()