import tkinter as tk
from parsing import Parser

#Класс интерфейса и логики
class Interface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ProductSales")
        #Цвета 
        self.clr_head = "#ADA9DB" 
        self.clr_body = "#C3C1DA" 
        self.configure(bg=self.clr_head)

        #Название
        self.lbl_title = tk.Label(self,bg=self.clr_head,text="ProductSales",font=("Impact",30))
        self.lbl_title.pack()
        self.lbl_intro = tk.Label(self,bg=self.clr_head,text="Севрвис для нахождения дешевых товаров",font=("Courier new",20))
        self.lbl_intro.pack()

        #Фрейм для ввода информации и кнопки
        self.frame_to_search = tk.Frame(self,bg=self.clr_head)
        self.frame_to_search.pack(fill=tk.X)

        self.entry = tk.Entry(self.frame_to_search,bg=self.clr_body, font=("Arial", 10))
        self.entry.pack(side=tk.LEFT,padx=100,pady=10,expand=True,fill=tk.X)

        self.btn_search = tk.Button(self.frame_to_search,bg=self.clr_body,text="Поиск",font=("Arial", 11),command=self.search)
        self.btn_search.pack(side=tk.RIGHT,padx=30,pady=10)

        #Фрейм для дополнительных данных(машины,квратиры)
        self.frame_extra = tk.Frame(self, bg=self.clr_head)
        self.frame_extra.pack()
        self.btn_find = None
        self.entry_values = []
        self.label_values = []

        #Фрейм для вывода информации
        self.frame_output = tk.Frame(self)
        self.frame_output.pack(fill=tk.BOTH, expand=1)

        self.lb = tk.Listbox(self.frame_output, background=self.clr_body, font=("Arial", 10))
        self.lb.grid(row=0, column=0, sticky=tk.NSEW)

        self.scroll = tk.Scrollbar(self.frame_output, command=self.lb.yview)
        self.scroll.grid(row=0, column=1, sticky=tk.NS)
        self.lb.config(yscrollcommand=self.scroll.set)

        self.frame_output.grid_rowconfigure(0, weight=1)
        self.frame_output.grid_columnconfigure(0, weight=1)

        self.parser = Parser()

    #Метод для кнопки "Поиск"
    def search(self):
        self.perform_cleanup()
        #2 массива для дополнительных данных ввода. Передаются в inp_extra
        extra_krisha = ["Аренда/покупка","Комнаты от:","до:","Площадь м² от:","до:","Этаж от:","до:"]
        extra_kolesa = ["Марка:","Модель:","Год выпуска от:","до:","Объем двигателя, л от","до","Пробег не более, км","Механика/автомат","Кузов"]

        text = self.entry.get()

        if text.lower() == "квартира" or text.lower() == "квартиры":
            self.parser.search = "flat"
            self.inp_extra(extra_krisha)
        elif text.lower() == "машина" or text.lower() == "машины" or text.lower() == "автомобиль" or text.lower() == "авто":
            self.parser.search = "car"
            self.inp_extra(extra_kolesa)
        else:
            self.parser.search = self.entry.get()
            self.parser.input_for_search([])
            self.output()

    #Метод для дополнительных данных(машин и квартир). Создаются столько лейблов и ентру, сколько приходит в names_lbl
    def inp_extra(self, names_lbl):   
        for row in range(len(names_lbl)):
            lbl = tk.Label(self.frame_extra,bg=self.clr_head, text=names_lbl[row])
            lbl.grid(row=row, column=0, padx=10)
            self.label_values.append(lbl)

            entry = tk.Entry(self.frame_extra,bg=self.clr_body)
            entry.grid(row=row, column=1, padx=10)
            self.entry_values.append(entry)
        
        #Кнопка берет все данные из ентри и передает их в find
        self.btn_find = tk.Button(self.frame_extra,
                                  text="Найти",
                                  bg=self.clr_body,
                                  font=("Arial", 9),
                                  command=lambda entry_values=self.entry_values: 
                                  self.find([entry.get() for entry in entry_values]))
        self.btn_find.grid(row=len(names_lbl)+1, column=1, padx=10, pady=10)

    #Удаляет все всплывшие ентри и лейблы при необходимости
    def perform_cleanup(self):
        for entry in self.entry_values:
            entry.destroy()

        for label in self.label_values:
            label.destroy()

        if self.btn_find:
            self.btn_find.destroy()
        # Очистка списков
        self.entry_values = []
        self.label_values = []

        #Уменьшение frame_extra
        self.frame_extra.config(height=10)

    #Метод отправляет данные в парсер для парсинга и выводит их
    def find(self,values):
        self.parser.input_for_search(values)
        self.output()

    #Вывод данных
    def output(self):
        self.lb.delete(0, tk.END)

        if not self.parser.outout_data:
            self.lb.insert(tk.END,"Не найдено. Проверьте корректность данных" )

        for datas in self.parser.outout_data[3:]:
            for element in datas:
                if len(element) > 200:
                    parts = [element[i:i+200] for i in range(0, len(element), 200)]
                    for part in parts:
                        self.lb.insert(tk.END, part)
                else:
                    self.lb.insert(tk.END, element)
        

inter = Interface()
inter.state("zoomed")
inter.mainloop()