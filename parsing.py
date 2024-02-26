import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup

from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service               
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.common.action_chains import ActionChains 
import time

#Класс для парсинга
class Parser:
    def __init__(self):
        self.search = None
        #Переменные для ввода квартиры
        self.buy_or_rent = None
        self.min_square_m = None
        self.max_square_m = None
        self.min_floor = None
        self.max_floor = None
        self.min_room = None
        self.max_room = None
        #Переменные для ввода авто
        self.brand = None
        self.make = None
        self.min_year = None
        self.max_year = None
        self.min_volume = None
        self.max_volume = None
        self.mileage = None
        self.transmission = None
        self.body = None
        #Массив для вывода информации 
        self.outout_data = []

    #Метод для вызова нужного метода, в зависимости что придет в search. 
    #В массив values приходят даныые ввода всплывающего окна
    def input_for_search(self,values):
        if self.search == "flat":
            self.buy_or_rent = values[0]
            self.min_square_m = values[3]
            self.max_square_m = values[4]
            self.min_floor = values[5]
            self.max_floor = values[6]
            self.min_room = values[1]
            self.max_room = values[2]
            asyncio.run(self.parsing_krisha())

        elif self.search == "car":   
            self.brand = values[0]
            self.make = values[1]
            self.min_year = values[2]
            self.max_year = values[3]
            self.min_volume = values[4]
            self.max_volume = values[5]
            self.mileage = values[6]
            self.transmission = values[7]
            self.body = values[8]
            asyncio.run(self.parsing_kolesa())

        else: 
            self.parsing_kaspi()

    #Mетода для парсинга Krisha.kz
    async def parsing_krisha(self):
        #очистка массива
        self.outout_data.clear() 
        chose_buy_rent = "arenda" if self.buy_or_rent == "аренда" else "prodazha"
        url_krisha = (f"https://krisha.kz/{chose_buy_rent}/kvartiry/astana/?das[flat.floor][from]={self.min_floor}"
                      f"&das[flat.floor][to]={self.max_floor}&das[live.rooms][]={self.min_room}&das[live.rooms][]={self.max_room}"
                      f"&das[live.square][from]={self.min_square_m}&das[live.square][to]={self.max_square_m}"
                      f"&rent-period-switch=%2Farenda%2Fkvartiry&sort_by=price-asc")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url_krisha) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    divs = soup.find_all('div', class_='a-card__header')
                    for div in divs:
                        try:
                            a = div.find('a', class_='a-card__title')
                            href = f"https://krisha.kz{a.get('href')}"
                            title = a.get_text()
                            price = div.find('div', class_='a-card__price')
                            price = price.get_text().strip()
                            adress = div.find('div', class_='a-card__subtitle')
                            adress = adress.get_text().strip()
                            info = div.find('div', class_='a-card__text-preview')
                            info = info.get_text().strip()
                            #Сохраняет все полученные данные в массив. А далее в глобальный массив
                            save_mas = [f"Заголовок:  {title}\n", 
                                        f"Ссылка:     {href}\n", 
                                        f"Цена:       {price}\n",
                                        f"Адрес:      {adress}\n", 
                                        f"Информация: {info}\n", "  "]
                            self.outout_data.append(save_mas)
                        except Exception:pass
        except Exception as outer_exception:
            print(f"Произошла ошибка при запросе к сайту: {outer_exception}")

    #Метод для парсинга Kolesa.kz
    async def parsing_kolesa(self):
        self.outout_data.clear()
        #В зависимости что впишет пользователь идет в ссылку
        body_mapping = {"седан": "sedan",
        "универсал": "station-wagon",
        "хэтчбек": "hatchback",
        "пикап": "body-pickup",
        "купе": "body-coupe"}

        self.body = body_mapping.get(self.body.lower(), self.body)
        transmission_mapping = {"механика": "1","автомат": "2345"}

        self.transmission = transmission_mapping.get(self.transmission.lower(), self.transmission)
        url_kolesa = (f"https://kolesa.kz/cars/{self.brand}/{self.body}/{self.make}/astana/"
         f"?auto-car-transm={self.transmission}&auto-run[to]={self.mileage}&auto-car-volume[from]={self.min_volume}"
         f"&auto-car-volume[to]={self.max_volume}&year[from]={self.min_year}&year[to]={self.max_year}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url_kolesa) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    divs = soup.find_all('div', class_='a-card__info')
                    for div in divs:
                        try:
                            a = div.find('a', class_='a-card__link')
                            href = f"https://kolesa.kz{a.get('href')}"
                            title = a.get_text().strip()
                            price = div.find('span', class_='a-card__price')
                            price = price.get_text().strip()
                            credit = div.find('button', class_='month-payment__amount js__month-payment')
                            credit = credit.get_text().strip()
                            info = div.find('p', class_='a-card__description')
                            info = info.get_text().strip()

                            save_mas = [f"Название:   {title}", 
                                        f"Ссылка:     {href}", 
                                        f"Цена:       {price}", 
                                        f"Кредит:     {credit}",
                                        f"Информация: {info}", " "]
                            self.outout_data.append(save_mas)
                        except Exception: pass
        except Exception as outer_exception:
            print(f"Произошла ошибка при запросе к сайту: {outer_exception}")

    #Медот для парсинга Kaspi.kz через Selenium
    def parsing_kaspi(self):
        self.outout_data.clear()

        try:
            service = Service(ChromeDriverManager().install())
            option = Options()
            option.add_argument('--headless')
            option.add_experimental_option("detach", False)
            driver = webdriver.Chrome(options=option, service=service)
            driver.get("https://kaspi.kz/shop/")

            city = driver.find_element(By.LINK_TEXT, "Астана")
            city.click()

            #Находит поисковую строку,вставляет туда данные и нажимает Enter
            search_input = driver.find_element(By.CLASS_NAME, "search-bar__input")
            search_input.clear()
            search_input.send_keys(self.search)
            search_input.send_keys(Keys.RETURN)
            #Сортирует по цене
            select_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "select__title")))
            select_dropdown.click()
            cheap_option = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//li[@data-id='price-asc']")))
            cheap_option.click()
            time.sleep(3)

            divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "item-card__info")))
            for div in divs:
                try:
                    card = div.find_element(By.CLASS_NAME, "item-card__name-link")
                    href = card.get_attribute("href")
                    name = card.text
                    price = div.find_element(By.CLASS_NAME, "item-card__prices-price")
                    price = price.text
                    save_mas = [f"Название: {name}",
                                f"Ссылка:   {href}",
                                f"Цена:     {price}", " "]
                    self.outout_data.append(save_mas)
                except: pass
        except Exception as e:
            print(f"Произошла ошибка: {e}")

        finally:
            driver.quit()

                 