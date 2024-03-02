from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import ElementNotInteractableException
from selenium import webdriver

from Class.Scraper import Scraper

class PlazaveaScraper(Scraper):
    name = 'plazavea'
    current_category = ''
    current_page = 1
    css_selectors = {
        'products': 'div.HA.Showcase.Showcase--food',
        'images': 'figure.Showcase__photo img',
        'brand': 'div.Showcase__brand a',
        'name': 'a.Showcase__name',
        'presentation': 'div.Showcase__units-reference',
        'price': 'div.Showcase__salePrice',
        'next_page': 'span.pagination__item.page-control.next '
    }
    base_urls = [
        { 'category': 'Carnes, aves y pescados', 'url': 'https://www.plazavea.com.pe/carnes-aves-y-pescados' },
        { 'category': 'Frutas y verduras', 'url': 'https://www.plazavea.com.pe/frutas-y-verduras' },
        { 'category': 'Congelados', 'url': 'https://www.plazavea.com.pe/congelados' },
        { 'category': 'Lacteos y Huevos', 'url': 'https://www.plazavea.com.pe/lacteos-y-huevos' },
        { 'category': 'Quesos y fiambres', 'url': 'https://www.plazavea.com.pe/quesos-y-fiambres' },
        { 'category': 'Abarrotes', 'url': 'https://www.plazavea.com.pe/abarrotes' },
        { 'category': 'Cuidado del Bebe', 'url': 'https://www.plazavea.com.pe/bebe-e-infantil' },
        { 'category': 'Cuidado Personal', 'url': 'https://www.plazavea.com.pe/cuidado-personal-y-salud' },
        { 'category': 'Limpieza', 'url': 'https://www.plazavea.com.pe/limpieza' },
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

        # Si son 2 imagenes tomar la segunda por ser la estandar
        # La primera imagen tiene el logo de Tottus
        if len(images) == 2:
            tottus_image, free_image = images 
            return free_image if free_image else tottus_image
        
        return images[0]
    
    def get_pagination_btn(self, driver: webdriver = None) -> WebElement:
        """Funcion que obtiene los botones de paginacion de la pagina"""

        # Obtengo los botones de atras y adelante de la paginacion
        # solo me interesa el boton de adelante
        pagination_btn = self.get_element(css=self.css_selectors['next_page'], driver=driver)
        return pagination_btn

    
    def remove_modal_from_screen(self) -> None:
        """Funcion para remover el modal de valoracion"""
        pass

    
