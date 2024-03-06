import time
from types import GeneratorType
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

class Scraper:
    def __init__(self) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless=new")
        self.drv = webdriver.Chrome(options = self.options)
        self.drv.implicitly_wait(5)
        self.current_url = ''
        self.first_time_saving = True
        self.data_recollected = []

        # start_requests esta definida aqui como funcion vacia y es suplantada por
        # la definida en las otras clases ( TottusScraper ) que tiene las urls
        self.generator = self.start_requests()

        self.url_generator()

    def url_generator(self):
        """Funcion que recorre una a una las urls, extrae la data y luego llama a
        extracting_page_data"""

        for gen in self.generator:
            data_page_generator = self.parse(gen)
            self.extracting_page_data(generator=data_page_generator, current_url = gen)

    def extracting_page_data(self, generator: GeneratorType = None, current_url: str = '') -> None:
        """Funcion que guarda los valores obtenidos de cada producto o
        se ejecuta recursivamente"""

        for data in generator:

                if isinstance(data, GeneratorType):
                    new_data_generator = next(data)
                    self.extracting_page_data(generator=new_data_generator)
                else:
                    self.data_recollected.append(data)
        
    def start_requests(self):
        """Funcion dentro del scraper para obtener las url a scrapear"""

    def parse(self, response):
        """Funcion dentro del scraper para recibir Response"""

    def get_page(self, url: str = '') -> webdriver:
        """Funcion que direcciona a la pagina objetivo"""

        self.current_url = url
        self.drv.get(url)
        return self.drv

    def get_element(self, css: str = '', driver: WebElement = '') -> WebElement | None:
        """Funcion que busca un web element usando el selector
        css"""

        try:
            el = driver.find_element(By.CSS_SELECTOR, css)
            return el
        except NoSuchElementException:
            print("!!!"*50)
            print(f"No se encontro elemento con selector css = {css}")
            print("!!!"*50)
            return None
        
    def get_elements(self, css: str = '', driver: WebElement = '') -> list[WebElement] | list:
        """Funcion que busca todos los web elements usando el selector
        css"""

        try:
            els = driver.find_elements(By.CSS_SELECTOR, css)
            return els
        except NoSuchElementException:
            print("!!!"*50)
            print(f"No se encontraron elementos para el selector css = {css}")
            print("!!!"*50)
            return []
        
    def save_data(self, file_name: str = '') -> None:
        """Funcion para guardar en archivo .csv los datos obtenidos"""
        
        print(f'{len(self.data_recollected)} productos guardados')

        df = pd.DataFrame(self.data_recollected)

        file_path = self.get_saving_path(file_name=file_name)

        if self.first_time_saving:
            df.to_csv(file_path, index=False, mode='w')
            self.first_time_saving = False
        else:
            df.to_csv(file_path, index=False, mode='a', header=False)

        self.data_recollected = []

    def get_saving_path(self, file_name:str = '') -> Path:
        """Funcion para obtener la ruta donde se guardara el archivo"""

        root_path = Path.cwd()
        target_dir = Path('results')
        return Path(root_path, target_dir, f'{file_name}.csv')

    def scroll_page(self) -> None:
        """Funcion para hacer scroll a toda la pantalla para que aparezcan
        todos los elementos"""

        wait_time = 0.8
        page_height = int(self.drv.execute_script("return document.body.scrollHeight"))
        vertical_gap = int(page_height / 8)

        # desde 0 hasta page_height con incrementos de vertical_gap
        for i in range(0, page_height, vertical_gap):
            self.drv.execute_script("window.scrollTo(0, {});".format(i))
            time.sleep(wait_time)

    def next_page(self, pagination_forward: WebElement = None, callback: callable = None, next_page_number: str = ''):
        """Funcion para ir a la siguiente pagina si existe"""

        try:
            pagination_forward.click()
            yield callback(self.drv)
        except ElementClickInterceptedException:
            print("!"*20)
            print("El boton de la paginacion no pudo ser presionado")
            print("Otro elemento lo ha interceptado")
            print("!"*20)

            url = f'{self.current_url}?page={next_page_number}'
            print(url)
            self.get_page(url=url)
            yield callback(self.drv)
        
