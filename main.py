import multiprocessing

from Class.Tottus import TottusScraper
from Class.Plazavea import PlazaveaScraper
from Class.Metro import MetroScraper

if __name__ == '__main__':
    # tottus = TottusScraper()
    # plazavea = PlazaveaScraper()
    # metro = MetroScraper()
    scrappers = [TottusScraper, PlazaveaScraper, MetroScraper]
    processes = []
    for scrapper in scrappers:
        process = multiprocessing.Process(target=scrapper)
        processes.append(process)
        process.start()

    for pro in processes:
        pro.join()
