import os
import sys

import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem
from PyQt5.QtWidgets import QApplication


form_class = uic.loadUiType("main.ui")[0]
#test

class cloud_analysis(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.main()

        self.filepath_list = []

        self.mft_filepath = ""
        self.mftcsv_filepath = ""


    def main(self):


        self.comboBox.activated.connect(self.on_combobox_select)

        self.radio_MFT.clicked.connect(self.select_but)
        self.radio_MFTcsv.clicked.connect(self.select_but2)

        self.search_line_edit.textChanged.connect(self.filterandnext)
        self.tableWidget.itemClicked.connect(self.get_selected_item_path)



        self.enter.clicked.connect(self.assignValue)


    def select_but(self):
        self.anlysis_result.setText('')

        try:
            self.fileSelect.clicked.disconnect(self.mftcsv)
        except:
            pass
        self.fileSelect.clicked.connect(self.input_mft)
        self.mftdescriptor.setText("If there is no MFT extracted to csv file")

    def select_but2(self):
        self.anlysis_result.setText('')
        try:
            self.fileSelect.clicked.disconnect(self.input_mft)
        except:
            pass
        self.fileSelect.clicked.connect(self.mftcsv)

        self.mftdescriptor.setText("csv")


    def input_mft(self):
        mft_filename = QFileDialog.getOpenFileName(self, 'File Load', '', 'All File(*)')
        mftfile = mft_filename[0]

        if mftfile:
            self.mft_filepath = mftfile.replace('/', '\\')
            self.fileInput1.setText(self.mft_filepath)
            if self.mft_filepath not in self.filepath_list:
                self.filepath_list.append(self.mft_filepath)

            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Text Files (*.csv);;All Files (*)',
                                                       options=options)

            command = f'python dfir_ntfs\\ntfs_parser --mft "{self.mft_filepath}" {file_name}'
            os.system(command)

            self.df = pd.read_csv(file_name, encoding='utf-8', sep=',', low_memory=False, usecols = ['Source', 'Path', '$SI M timestamp','$SI A timestamp','$SI C timestamp','$SI E timestamp','$SI USN value','$FN M timestamp','$FN A timestamp','$FN C timestamp','$FN E timestamp','$OBJID timestamp','File size'])
            self.open_csv(file_name)


    def mftcsv(self):
        mftcsv_filename = QFileDialog.getOpenFileName(self, 'File Load', '', 'All File(*)')
        mftcsvfile = mftcsv_filename[0]

        if mftcsvfile:
            self.mftcsv_filepath = mftcsvfile.replace('/', '\\')
            self.df = pd.read_csv(self.mftcsv_filepath, encoding='utf-8', sep=',', low_memory=False, usecols = ['Source', 'Path', '$SI M timestamp','$SI A timestamp','$SI C timestamp','$SI E timestamp','$SI USN value','$FN M timestamp','$FN A timestamp','$FN C timestamp','$FN E timestamp','$OBJID timestamp','File size'])
            self.open_csv(self.mftcsv_filepath)

    def get_selected_item_path(self, item):
        if item.column() == 1:
            selected_path = item.text()
            self.selectpath = selected_path
            self.inputvalue(self.selectpath)


    def filterandnext(self):
        self.filter_data()


    def filter_data(self):
        search_text = self.search_line_edit.text().strip()
        if search_text:
            filtered_df = self.df[self.df['Path'].str.contains(search_text, case=False, na=False)]
            self.display_dataframe(filtered_df)

        else:
            self.display_dataframe(self.df)


    def on_combobox_select(self, index):
        selected_option = self.sender().currentText()
        if selected_option == "Dropbox":
            self.selectcloud = 1

    def open_csv(self, csvfile):
        file_name = csvfile

        if file_name:
            try:
                self.display_dataframe(self.df)
            except Exception as e:
                self.tableWidget.setRowCount(0)
                self.tableWidget.setColumnCount(0)
                self.show_error_message("An error occurred while reading the CSV file.: " + str(e))

    def display_dataframe(self, df):
        filter_column = 'Source'
        filter_value = 'File record'

        # 필터링된 데이터프레임 생성
        filtered_df = df[df[filter_column] == filter_value]

        self.tableWidget.setRowCount(filtered_df.shape[0])
        self.tableWidget.setColumnCount(filtered_df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(filtered_df.columns)

        for i in range(filtered_df.shape[0]):
            for j in range(filtered_df.shape[1]):
                item = QTableWidgetItem(str(filtered_df.iat[i, j]))
                self.tableWidget.setItem(i, j, item)



    def assignValue(self):
        text = self.lineEdit.text()
        self.selectpath = text
        self.inputvalue(self.selectpath)

    def file_selected(self, index):
        file_info = self.dirModel.fileInfo(index)

        if file_info.isDir():
            self.select_all_files_in_directory(file_info.absoluteFilePath())
        else:
            file_path = file_info.absoluteFilePath()
            extension = os.path.splitext(file_path)[1]
            self.filter_files_by_extension(extension)

            if file_path not in self.file_paths:
                self.listWidget.addItem(file_path)
                self.file_paths.append(file_path)

    def fileparsetime(self, search_name):
        try:
            filtered_df = self.df.loc[self.df['Path'] == search_name]

            if filtered_df.empty:
                self.anlysis_result.setText('No such file exists.')
                return None

            timestamp_columns = ['$FN M timestamp', '$FN A timestamp', '$FN C timestamp', '$FN E timestamp',
                                 '$SI M timestamp', '$SI A timestamp', '$SI C timestamp', '$SI E timestamp']

            timelist = [filtered_df[column].iloc[0] for column in timestamp_columns]
            return timelist
        except Exception as e:
            self.anlysis_result.setText('No such file exists.')
            return None

    def set_command_value(self, command_dict, command_name, value):
        if command_name in command_dict:
            command_dict[command_name] = value
            print(f"{command_name}의 값을 {value}로 설정했습니다.")
        else:
            print(f"{command_name}은(는) 유효한 명령어가 아닙니다.")


    def inputvalue(self, filename):
        timelist = self.fileparsetime(filename)

        if timelist is None:
            return

        FN_MTime, FN_ATime, FN_CTime, FN_RTime, SI_MTime, SI_ATime, SI_CTime, SI_RTime = timelist
        FP0 = 0

        rpc_commands = {
            "Upload": 0,
            "Copy": 0,
            "Move": 0,
            "Rename": 0
        }

        lpc_commands = {
            "Upload": 0,
            "Copy": 0,
            "Move": 0,
            "Rename": 0
        }

        urpc = {
            "RPC": rpc_commands.copy(),
            "LPC": lpc_commands.copy()
        }

        ulpc = {
            "RPC": rpc_commands.copy(),
            "LPC": lpc_commands.copy()
        }

        if self.selectcloud == 1:  # cloud 가 dropbox 일때
            for i in [SI_MTime, FN_MTime]:
                a = i.split('.')
                if a[1] == '000000000':
                    FP0 = 1

            if FP0 == 1:
                if FN_MTime == FN_ATime:
                    self.set_command_value(urpc["RPC"], "Upload", 1)
                    self.set_command_value(urpc["RPC"], "Copy", 1)
                    self.set_command_value(ulpc["RPC"], "Copy", 1)
                    #result = 'remote PC(Upload or Copy) or remote PC(Copy) - Uploaded by local'
                else:
                    if SI_RTime == FN_RTime:
                        self.set_command_value(urpc["RPC"], "Move", 1)
                        self.set_command_value(urpc["RPC"], "Rename", 1)

                        result = 'remote PC(Move or Rename)'
                    else:
                        if SI_MTime == FN_MTime:
                            self.set_command_value(urpc["LPC"], "Rename", 1)
                            self.set_command_value(urpc["LPC"], "Move", 1)
                            result = 'local PC(Move or Rename)'
                        else:
                            self.set_command_value(urpc["LPC"], "Copy", 1)
                            result = 'local PC(Copy)'


            elif FP0 == 0:
                if SI_CTime == FN_MTime == FN_ATime == FN_CTime == FN_RTime:
                    self.set_command_value(ulpc["LPC"], "Upload", 1)
                    self.set_command_value(ulpc["LPC"], "Copy", 1)
                    result = 'local PC(UC)  - Uploaded by local'

                elif SI_RTime == FN_RTime:
                    self.set_command_value(ulpc["RPC"], "Move", 1)
                    self.set_command_value(ulpc["RPC"], "Rename", 1)
                    result = 'remote PC(MR)'
                else:
                    self.set_command_value(ulpc["LPC"], "Move", 1)
                    self.set_command_value(ulpc["LPC"], "Rename", 1)
                    result = 'local PC(MR)'

        elif self.selectcloud == 2:  # cloud 가 google 일때
            for i in timelist:
                a = i.split('.')
                FP0 = 1 if a[1][3:] == '0000' else 0

            if FP0 == 1:
                if SI_CTime == FN_MTime == FN_ATime == FN_CTime == FN_RTime:
                    result = 'local PC(C)'
                else:
                    if SI_MTime == FN_MTime:
                        result = 'local PC(MR) or Remote PC(M) or remote PC(C)'
                    else:
                        if FN_MTime == FN_ATime:
                            result = 'remote PC(UC)'
                        else:
                            result = 'remote PC(R)'

            elif FP0 == 0:
                if SI_CTime == FN_MTime == FN_ATime == FN_CTime == FN_RTime:
                    result = 'local PC(UC)'
                else:
                    result = 'local PC(UR) and remote PC(M)'

        elif self.selectcloud == 3:  # cloud 가 mega 일때
            for i in timelist:
                a = i.split('.')
                FP0 = 1 if a[1][3:] == '0000' else 0
        result = {}
        resultn = {}

        for key, value in ulpc.items():
            sub_result = {}
            for cmd, count in value.items():
                if count == 1:
                    sub_result[cmd] = count
            if sub_result:
                result[key] = sub_result

        result2 = ("ULPC"+str(result))
        ulpc.clear()

        for key, value in urpc.items():
            sub_result = {}
            for cmd, count in value.items():
                if count == 1:
                    sub_result[cmd] = count
            if sub_result:
                resultn[key] = sub_result
        result3 =("URPC"+str(resultn))
        self.anlysis_result.setText(result2+result3)
        urpc.clear()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = cloud_analysis()
    ex.show()
    app.exec_()
