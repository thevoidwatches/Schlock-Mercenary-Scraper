# Schlock Mercenary Scraper
This is a simple webscraper, designed to download the comic images and footnotes available on https://www.schlockmercenary.com and convert them to .epubs for convenient transport.

## How to use
After installing the dependencies (python, selenium, and ebooklib), simply open the run.bat file while connected to the internet. The scraper will create 20 .epub files, one for each of the 20 books of *Schlock Mercenary*'s 20-year run.

To download only a single book at a time, edit the run.bat file with any text editor and add the `-b` argument, followed by any numeral between 1 and 20. This will begin scraping at the specified book, and close after finishing that book.

## Disclaimer
*Schlock Mercenary* belongs to Howard Taylor. This web scraper is not intended to compete with the official releases of its books - all of which contain bonus content not available online or by using this scraper. It is only intended to serve as a convenient way to take the freely-available comics on-the-go to areas without internet access. Please support Howard Taylor and the official release of *Schlock Mercenary*.