from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from tkinter.filedialog import askdirectory
from windnd import hook_dropfiles
import os.path
from time import strftime, localtime
from zlib import crc32


MAX_FILE_COUNT = 20
MAX_FILE_SIZE = 0xC800000
EXCLUED_FILES = ('\\lib\\', 'tcl86t.dll', 'tk86t.dll', 'python37.dll')


class Application(Tk):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.title('文件CRC校验工具')
        self.resizable(0, 0)

        # 按钮1 按钮2
        ft = Font(family='微软雅黑', size=12)
        self.btnOfd1 = Button(self, text='点击选择文件夹\n或\n拖动文件夹到此处', font=ft, width=40, height=6,
                              command=lambda arg=1: self.btnOfd_Clicked(arg))
        hook_dropfiles(self.btnOfd1, func=self.btnOfd1_DraggedFiles)
        self.btnOfd1.grid(row=0, column=0, pady=10)

        self.btnOfd2 = Button(self, text='点击选择文件夹\n或\n拖动文件夹到此处', font=ft, width=40, height=6,
                              command=lambda arg=2: self.btnOfd_Clicked(arg))
        hook_dropfiles(self.btnOfd2, func=self.btnOfd2_DraggedFiles)
        self.btnOfd2.grid(row=0, column=1, pady=10)

        # label1 label2
        self.txtLabel1 = StringVar()
        self.label1 = ttk.Label(self, textvariable=self.txtLabel1)
        self.label1.grid(row=1, column=0, sticky=W, padx=10)

        self.txtLabel2 = StringVar()
        self.label2 = ttk.Label(self, textvariable=self.txtLabel2)
        self.label2.grid(row=1, column=1, sticky=W, padx=10)

        # treeview1 treeview2
        columns = ('文件路径', '文件创建时间', 'CRC32')
        self.treeview1 = ttk.Treeview(self, height=18, show='headings', columns=columns)
        self.treeview1.column('文件路径', width=330, anchor='w')
        self.treeview1.column('文件创建时间', width=130, anchor='center')
        self.treeview1.column('CRC32', width=70, anchor='center')
        self.treeview1.grid(row=2, column=0, padx=10, pady=12)

        self.treeview2 = ttk.Treeview(self, height=18, show='headings', columns=columns)
        self.treeview2.column('文件路径', width=330, anchor='w')
        self.treeview2.column('文件创建时间', width=130, anchor='center')
        self.treeview2.column('CRC32', width=70, anchor='center')
        self.treeview2.grid(row=2, column=1, padx=10, pady=12)

        # 绑定函数，使表头可排序
        for col in columns:
            self.treeview1.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(
                self.treeview1, _col, False))
            self.treeview2.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(
                self.treeview2, _col, False))

    def btnOfd1_DraggedFiles(self, files):
        locate = files[0].decode(encoding='gbk')
        if os.path.exists(locate):
            self.crcHandle(1, locate)

    def btnOfd2_DraggedFiles(self, files):
        locate = files[0].decode(encoding='gbk')
        if os.path.exists(locate):
            self.crcHandle(2, locate)

    def btnOfd_Clicked(self, arg):
        locate = askdirectory()
        if os.path.exists(locate):
            self.crcHandle(1 if arg == 1 else 2, locate)

    def crcHandle(self, index, locate):
        fileList = []
        if os.path.isfile(locate):
            fileList.append(locate)
        else:
            for root, dirs, files in os.walk(locate):
                if len(fileList) > MAX_FILE_COUNT:
                    break
                for f in files:
                    fileList.append(os.path.join(root, f))

        count = 0
        if index == 1:
            x = self.treeview1.get_children()
            for item in x:
                self.treeview1.delete(item)
            self.txtLabel1.set('当前文件夹： ' + locate)
        else:
            x = self.treeview2.get_children()
            for item in x:
                self.treeview2.delete(item)
            self.txtLabel2.set('当前文件夹： ' + locate)

        for file in sorted(fileList):
            if count >= MAX_FILE_COUNT:
                break
            if os.path.getsize(file) > MAX_FILE_SIZE:
                continue
            if EXCLUED_FILES[0] in file or EXCLUED_FILES[1] in file or EXCLUED_FILES[2] in file or EXCLUED_FILES[3] in file:
                continue

            try:
                with open(file, 'rb') as fs:
                    content = fs.read()
                    crc = hex(crc32(content)).upper()[2:]

                    timeStr = strftime('%Y-%m-%d %H:%M:%S', localtime(os.path.getatime(file)))
                    if index == 1:
                        self.treeview1.insert(
                            '', 'end', values=[file.replace(locate, '.'), timeStr, crc])
                    else:
                        self.treeview2.insert(
                            '', 'end', values=[file.replace(locate, '.'), timeStr, crc])

            except Exception as e:
                print(str(e))

            finally:
                count += 1

    # treeview 按表头排序
    def treeview_sort_column(self, tv, col, reverse):
        llist = [(tv.set(k, col), k) for k in tv.get_children('')]
        llist.sort(reverse=reverse)
        for index, (val, k) in enumerate(llist):
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))


if __name__ == '__main__':
    app = Application()
    app.title('文件CRC校验工具')
    app.mainloop()
