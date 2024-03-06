# Scrapping de supermercados peruanos
Este codigo extrae datos de los productos de los supermercados: Tottus, Plazavea y Metro de acuerdo a categorias ya establecidas:
- carnes-aves-y-pescados
- frutas-y-verduras
- congelados
- lacteos-y-huevos
- quesos-y-fiambres
- abarrotes
- bebidas
- cuidado-personal-y-salud
- limpieza

Los datos extraidos son:
- Nombre
- Imagen
- Precio o precio / unidad
- Presentación del producto
- Marca del producto
- Categoría

Tener en cuenta que no todos los productos presentan la misma informacion, es decir, algunos tienen presentacion mientras que otros no y otros la incluyen en el nombre.
## Como ejecutarlo
Este codigo esta hecho en `python 3.11.4` y se requieren las librerias indicadas en el archivo `requeriments.txt` y que a continuacion preciso:
- Selenium=4.11.2
- Pandas=2.2.1
- pathlib=1.0.1
### Instalar librerias
```bash
pip install -r requeriments.txt
```
### Ejecutar los tres scrappers simultaneamente
```bash
python main.py
```
### Ejecutar scrapper de Tottus
```bash
python main_tottus.py
```
### Ejecutar scrapper de Plazavea
```bash
python main_plazavea.py
```
### Ejecutar scrapper de Metro
```bash
python main_metro.py
```