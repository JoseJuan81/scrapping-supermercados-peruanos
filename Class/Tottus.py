from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import ElementNotInteractableException
from selenium import webdriver

from Class.Scraper import Scraper

class TottusScraper(Scraper):
    name = 'tottus'
    current_category = ''
    current_page = 1
    css_selectors = {
        'products': 'div.grid-pod',
        'images': 'section.layout_grid-view img',
        'brand': '.pod-title.title-rebrand',
        'name': '.pod-subTitle.subTitle-rebrand',
        'price': 'li.prices-0 div span',
        'next_page': 'div.action-bar div.pagination div.arrow button'
    }
    base_urls = [
        { 'category': 'Desayunos', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/CATG11957/Desayunos-y-panaderia' },
        { 'category': 'Dulces y Snacks', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/cat13380485/Dulces-y-snacks' },
        { 'category': 'Lacteos y Frescos', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/CATG11959/Lacteos-y-frescos' },
        { 'category': 'Congelados', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/CATG11956/Congelados' },
        { 'category': 'Huevos', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/CATG14204/Huevos' },
        { 'category': 'Detergente y cuidados de la ropa', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/cat13920468/Detergentes-y-cuidado-para-la-ropa' },
        { 'category': 'Papel', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/cat13920469/Papeles' },
        { 'category': 'Limpiadores', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/CATG11963/Lavalozas-y-Limpiadores' },
        { 'category': 'Ambientadores y desinfectantes', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/cat13920471/Ambientales-y-desinfectantes' },
        { 'category': 'Utencilios de aseo', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/cat13920467/Utensilios-de-aseo' },
        { 'category': 'Bolsas de basura', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/CATG14250/Bolsa-de-Basura' },
        { 'category': 'Cuidado Capilar', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/cat5130510/Cuidado-capilar' },
        { 'category': 'Cuidado de la Piel', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/CATG11985/Cuidado-de-la-piel' },
        { 'category': 'Cuidado Personal', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/CATG11986/Cuidado-personal' },
        { 'category': 'Salud', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/cat2600464/Salud' },
        { 'category': 'Alimento Bebe', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/CATG14325/Alimento-de-Bebe' },
        { 'category': 'Abarrotes', 'url': 'https://tottus.falabella.com.pe/tottus-pe/category/cat13380487/Despensa' },
    ]

    def start_requests(self):
        """Funcion para recorrer todas las urls definidas para extraer datos"""

        for url in self.base_urls:
            self.current_category = url['category']
            print(f'{self.name},  categoria: {self.current_category}')

            yield self.get_page(url=url['url'])
            print("pasando a otra url")
            self.current_page = 1
            
        print(f'FIN del scraping en {self.name}')
        print("=="*50)
    
    def parse(self, response):
        """Funcion para extraer los datos de los productos.
        Esta funcion es una funcion generadora que retorna todos los productos
        y de ultimo la funcion next_page gracias al uso de yield"""

        print(f'Pagina {self.current_page}, categoria: {self.current_category}')
        self.scroll_page()
        products = self.get_elements(css=self.css_selectors['products'], driver=response)
        
        # Recorrer cada producto conseguido para extraer datos
        for product in products:
            images = self.get_elements(css=self.css_selectors['images'], driver=product)
            img_tag = self.validating_images(images=images)

            yield {
                'image': img_tag.get_attribute('src'),
                'product_brand': self.get_element(css=self.css_selectors['brand'], driver=product).text,
                'name': self.get_element(css=self.css_selectors['name'], driver=product).text,
                'price': self.get_element(css=self.css_selectors['price'], driver=product).text,
                'supermarket_name': self.name,
                'category': self.current_category
            }

        # Guardar los datos obtenidos en archivo .csv    
        self.save_data(file_name=self.name)

        # Obtener boton de paginacion "siguiente" para avanzar de pagina
        pagination_forward = self.get_pagination_btn(driver=response)
        if pagination_forward and pagination_forward.is_enabled():
            self.current_page += 1
            yield self.go_next_page(next_button=pagination_forward)

    def go_next_page(self, next_button: WebElement = None):
        try:
            return self.next_page(pagination_forward=next_button, callback=self.parse)
        except ElementNotInteractableException:
            print("Aparecio el modal")
            self.remove_modal_from_screen()
            input("Presiona enter para continuar")
            return self.next_page(pagination_forward=next_button, callback=self.parse)

    def validating_images(self, images: list = []) -> WebElement:
        """Funcion para validar la cantidad de imagenes que existe
        en cada producto"""

        if images:
            # Si son 2 imagenes tomar la segunda por ser la estandar
            # La primera imagen tiene el logo de Tottus
            if len(images) == 2:
                tottus_image, free_image = images 
                return free_image if free_image else tottus_image
            
            return images[0]
        else:
            return "No se consiguio la imagen del producto"

    
    def get_pagination_btn(self, driver: webdriver = None) -> WebElement:
        """Funcion que obtiene los botones de paginacion de la pagina"""

        # Obtengo los botones de atras y adelante de la paginacion
        # solo me interesa el boton de adelante
        pagination_btns = self.get_elements(css=self.css_selectors['next_page'], driver=driver)
        _, pagination_forward = pagination_btns

        return pagination_forward
    
    def remove_modal_from_screen(self) -> None:
        """Funcion para remover el modal de valoracion"""
        pass

    
