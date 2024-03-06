import time
import pandas as pd
from pathlib import Path
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from types import GeneratorType

class MetroScraper():
    name = 'metro'
    current_category = ''
    css_selectors = {
        'products': '#gallery-layout-container > div',
        'images': 'div.vtex-product-summary-2-x-imageContainer img',
        'name': 'div.vtex-product-summary-2-x-nameContainer > h3 > span',
        'price': 'div.vtex-flex-layout-0-x-flexRow--row-precios-shelf span:nth-child(2)',
        'more_button': 'div.vtex-search-result-3-x-buttonShowMore button',
    }
    base_urls = [
        { 'category': 'Frutas y verduras', 'url': 'https://www.metro.pe/frutas-y-verduras' },
        { 'category': 'Carnes, aves y pescados', 'url': 'https://www.metro.pe/carnes-aves-y-pescados' },
        { 'category': 'Congelados', 'url': 'https://www.metro.pe/congelados' },
        { 'category': 'Lacteos', 'url': 'https://www.metro.pe/lacteos' },
        { 'category': 'Embutidos y fiambres', 'url': 'https://www.metro.pe/embutidos-y-fiambres' },
        { 'category': 'Cuidado del Bebe', 'url': 'https://www.metro.pe/ninos-y-bebes' },
        { 'category': 'Limpieza', 'url': 'https://www.metro.pe/limpieza' },
        { 'category': 'Abarrotes', 'url': 'https://www.metro.pe/abarrotes' },
        { 'category': 'Salud, higiene y belleza', 'url': 'https://www.metro.pe/higiene-salud-y-belleza' },
    ]

    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless=new")
        self.options.add_argument("--window-size=2800,2400")
        self.drv = webdriver.Chrome(options = self.options)
        self.drv.implicitly_wait(15)
        self.first_time_saving = True
        self.data_recollected = []
        self.max_trying = 0
        self.body = None

        page_generator = self.start_requests()
        self.extract_data(page_generator=page_generator)

    def start_requests(self):
        """Funcion para recorrer todas las urls definidas para extraer datos"""

        for url in self.base_urls:
            self.current_category = url['category']
            print(f'{self.name},  categoria: {self.current_category}')

            self.drv.get(url['url'])
            time.sleep(5)
            self.body = self.drv.find_element(By.TAG_NAME, "body")
            yield self.drv

            print("pasando a otra url")
            self.max_trying = 0
            
        print(f'FIN del scraping en {self.name}')
        print("=="*30)

    def extract_data(self, page_generator: GeneratorType = None):
        """Funcion para recorrer la pagina actual y extraer los datos"""

        for page in page_generator:
            product_data_generator = self.pagination(page)

            for product_data in product_data_generator:
                print(product_data)
                self.data_recollected.append(product_data)

            # Guardar los datos obtenidos en archivo .csv    
            self.save_data(data=self.data_recollected, file_name=self.name)

    def pagination(self, page):
        """Funcion para hacer scroll y presionar el boton Cargar Mas"""

        if self.max_trying >= 3:
            self.reload_products_images()
            yield from self.parse(page)

        print('cargando productos...')
        time.sleep(5)
        scroll_height = int(page.execute_script("return document.body.scrollHeight"))
        # client_height = int(page.execute_script("return document.body.clientHeight"))
    
        # if scroll_height >= client_height:
        print("Iniciando el scroll para presionar boton Cargar Mas")
        self.scroll_down_all_page(page, scroll_height)
        try:
            print("Buscando boton Cargar Mas...")
            more_btn = self.get_element(css=self.css_selectors['more_button'], driver=page)

            if more_btn:
                print("Boton Cargar Mas encontrado...")
                more_btn.click()
                print("El boton Cargar Mas fue presionado")
                time.sleep(7)
                yield from self.pagination(page)
            else:
                print('no consiguio el boton. Terminamos de cargar los productos')
                self.reload_products_images(scroll_height)
                yield from self.parse(page)

        except TimeoutException:
            print("Se agoto el tiempo de espera y no se consiguio el elemento")
            print("Intentare nuevamente...")
            time.sleep(10)
            self.max_trying += 1
            yield from self.pagination(page)
            
        # else:
        #     print('scroll_height es menor a client_height')
        #     time.sleep(10)
        #     yield from self.pagination(page)
            
        print('este es el final de pagination')
    
    def parse(self, page):
        """Funcion para extraer los datos de los productos.
        Esta funcion es una funcion generadora que retorna todos los productos
        y de ultimo la funcion next_page gracias al uso de yield"""

        print(f'Inicio de extraccion de datos de la pagina: {self.current_category}')

        products = self.get_elements(css=self.css_selectors['products'], driver=page)
        print(f"se encontraron {len(products)} en la pagina...")
        
        # Recorrer cada producto conseguido para extraer datos
        for product in products:
            img_tag = self.get_product_image(css=self.css_selectors['images'], driver=product)
            _name = self.get_element(css=self.css_selectors['name'], driver=product)
            _price = self.get_element(css=self.css_selectors['price'], driver=product)

            yield {
                'image': img_tag.get_attribute('src'),
                'name': _name.get_attribute('textContent'),
                'price': _price.get_attribute('textContent') if _price else "Sin Precio",
                'supermarket_name': self.name,
                'category': self.current_category
            }

    def get_product_image(self, css: str = '', driver: webdriver = None) -> WebElement:
        """Funcion para obtener la imagen del producto"""

        images = self.get_elements(css=self.css_selectors['images'], driver=driver)
        img_tag = self.validating_images(images=images)
        return img_tag

    def validating_images(self, images: list = []) -> WebElement:
        """Funcion para validar la cantidad de imagenes que existe
        en cada producto"""

        # Si son 2 imagenes tomar la segunda por ser la estandar
        # La primera imagen tiene el logo de Tottus
        if len(images) == 2:
            metro_image, free_image = images 
            return free_image if free_image else metro_image
        
        return images[0]
    
    def scroll_top(self) -> None:
        """Funcion para hacer scroll al inicio de la pagina"""
        
        self.drv.execute_script("window.scrollTo(0, 0);")

    def scroll_smooth(self, scroll_height) -> None:
        """Funcion para hacer scroll lentamente hasta abajo"""

        if not scroll_height:
            scroll_height = int(self.drv.execute_script("return document.body.scrollHeight"))
        
        wait_time = 0.75
        vertical_gap = int(scroll_height / 220)

        # desde 0 hasta page_height con incrementos de vertical_gap
        for i in range(0, scroll_height, vertical_gap):
            self.drv.execute_script("window.scrollTo(0, {});".format(i))
            time.sleep(wait_time)

    def scroll_down_all_page(self, page, scroll_height) -> None:
        """Funcion para hacer scroll a toda la pagina hacia abajo"""

        # print(f"scroll_height de: {scroll_height}")
        page.execute_script("window.scrollTo(0, {});".format(scroll_height))
    
    def save_data(self, data: list = [], file_name: str = '') -> None:
        """Funcion para guardar en archivo .csv los datos obtenidos"""
        
        print('Inicio guardado de productos...')
        print(f'{len(self.data_recollected)} productos a guardar.')

        df = pd.DataFrame(data)

        file_path = self.get_saving_path(file_name=file_name)

        if self.first_time_saving:
            df.to_csv(file_path, index=False, mode='w')
            self.first_time_saving = False
        else:
            df.to_csv(file_path, index=False, mode='a', header=False)

        print(f'{len(data)} productos guardados')

    def get_saving_path(self, file_name:str = '') -> Path:
        """Funcion para obtener la ruta donde se guardara el archivo"""

        root_path = Path.cwd()
        target_dir = Path('results')
        return Path(root_path, target_dir, f'{file_name}.csv')

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
        
    def reload_products_images(self, scroll_height) -> None:
        """Funcion para recargar las imagenes de los productos"""

        self.scroll_top()
        time.sleep(2)
        print('inicio scroll_smooth...')
        print('esto puede tardar un poco...')
        self.scroll_smooth(scroll_height)
        print('fin scroll_smooth...')
        time.sleep(2)