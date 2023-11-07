import os
import sys

import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtWidgets import QApplication
import Mft2Csv

df = pd.read_csv('Mft.csv', sep='|')
df.head()

form_class = uic.loadUiType("main.ui")[0]
class cloud_analysis(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


    def main(self):
        print('분석대상 클라우드를 선택하세요')
        self.comboBox.activated.connect(self.on_combobox_select)

        self.fileSelect.clicked.connect(self.input_mft)

    def input_mft(self):
        mft_filename = QFileDialog.getOpenFileName(self, 'File Load', '',
                                                     'All File(*)')
        mftfile = mft_filename[0]
        self.mft_filepath = mftfile.replace('/', '\\')
        self.mftInput.setText(self.mft_filepath)
        if self.mft_filepath not in self.filepath_list:
            self.filepath_list.append(self.mft_filepath)



    def file_selected(self, index):
        file_info = self.dirModel.fileInfo(index)
        if file_info.isDir():  # If a directory is selected
            self.select_all_files_in_directory(file_info.absoluteFilePath())
        else:
            file_path = file_info.absoluteFilePath()
            extension = os.path.splitext(file_path)[1]
            self.filter_files_by_extension(extension)
            if file_path not in self.file_paths:
                self.listWidget.addItem(file_path)
                self.file_paths.append(file_path)

    def on_combobox_select(self, index):
        selected_option = self.sender().currentText()
        if selected_option == "Dropbox":
            self.cloudnum == 1

    def fileparsetime(self, search_name):
        search_name = search_name
        filtered_df = df.loc[df['FN_FileName_2']==search_name]
        timelist = []

        FN_MTime = filtered_df['FN_MTime_2'].iloc[0]
        FN_ATime = filtered_df['FN_ATime_2'].iloc[0]
        FN_CTime = filtered_df['FN_CTime_2'].iloc[0]
        FN_RTime = filtered_df['FN_RTime_2'].iloc[0]
        SI_MTime = filtered_df['SI_MTime'].iloc[0]
        SI_ATime = filtered_df['SI_ATime'].iloc[0]
        SI_CTime = filtered_df['SI_CTime'].iloc[0]
        SI_RTime = filtered_df['SI_RTime'].iloc[0]

        timelist.append(FN_MTime)
        timelist.append(FN_ATime)
        timelist.append(FN_CTime)
        timelist.append(FN_RTime)
        timelist.append(SI_MTime)
        timelist.append(SI_ATime)
        timelist.append(SI_CTime)
        timelist.append(SI_RTime)


        return timelist, FN_MTime, FN_ATime, FN_CTime, FN_RTime, SI_MTime, SI_ATime, SI_CTime, SI_RTime


    def inputvalue(self, inputcloud, filename):

        timelist, FN_MTime, FN_ATime, FN_CTime, FN_RTime, SI_MTime, SI_ATime, SI_CTime, SI_RTime = fileparsetime(filename)
        inputcloud = inputcloud
        FP0 = -1

        if inputcloud == 1: # cloud 가 dropbox 일때
            for i in timelist:
                a = i.split('.')
                if a[1] == '0000000':
                    FP0 = 1
                    print('FP0이 나타남')
                else :
                    FP0 = 0


            if FP0 == 1:
                if FN_MTime == FN_ATime :
                    print('remote PC(Upload or Copy)')
                    print('remote PC(Copy)')
                else :
                    if SI_RTime == FN_RTime:
                        print('remote PC(Move or Rename)')
                    else :
                        if SI_MTime == FN_MTime:
                            print('local PC(Move or Rename)')
                        else :
                            print('local PC(Copy)')

            elif FP0 == 0 :
                if SI_CTime == FN_MTime == FN_ATime == FN_CTime == FN_RTime:
                    print('local PC(UC)')
                elif SI_RTime == FN_RTime:
                    print('remote PC(MR)')
                else :
                    print('local PC(MR)')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = cloud_analysis()
    ex.show()
    app.exec_()
