import sys
import queue
import requests

from selenium.webdriver.common.by import By
from selenium import webdriver

from ebooklib import epub

# When running the program from commandline, the -v or -V argument allows you to choose how much information is printed into the command line.
if "-V" in sys.argv:
    VERBOSE = 2
elif "-v" in sys.argv:
    VERBOSE = 1
else:
    VERBOSE = 0

# Argument that allows you to start at a later book in the comic.
if "-b" in sys.argv:
    URLS = [
        "https://www.schlockmercenary.com/2000-06-12",
        "https://www.schlockmercenary.com/2001-11-11",
        "https://www.schlockmercenary.com/2003-03-09",
        "https://www.schlockmercenary.com/2003-08-24",
        "https://www.schlockmercenary.com/2004-03-15", # Book 5
        "https://www.schlockmercenary.com/2004-09-12",
        "https://www.schlockmercenary.com/2005-07-24",
        "https://www.schlockmercenary.com/2006-08-17",
        "https://www.schlockmercenary.com/2007-05-20",
        "https://www.schlockmercenary.com/2008-02-29", # Book 10
        "https://www.schlockmercenary.com/2009-03-02",
        "https://www.schlockmercenary.com/2010-11-29",
        "https://www.schlockmercenary.com/2011-11-13",
        "https://www.schlockmercenary.com/2013-01-01",
        "https://www.schlockmercenary.com/2014-03-16", # Book 15
        "https://www.schlockmercenary.com/2015-03-30",
        "https://www.schlockmercenary.com/2016-12-05",
        "https://www.schlockmercenary.com/2017-09-18",
        "https://www.schlockmercenary.com/2018-07-25",
        "https://www.schlockmercenary.com/2019-06-16"  # Book 20
    ]
    try:
        URL = URLS[sys.argv[sys.argv.index("-b") + 1] - 1]
    except:
        print("Please enter a number between 1 and 20 when using the -b argument.")
        exit()
else:
    URL = "https://www.schlockmercenary.com/2000-06-12"

def clean_unicode(text: str) -> str:
    """Function used to clean text before saving to a file that may not
    support Unicode text."""
    text = text.encode(
        encoding="ascii",
        errors="xmlcharrefreplace"
    ).decode()
    text = text.replace("&#180;", "'")
    text = text.replace("&#8216;", "'")
    text = text.replace("&#8217;", "'")
    text = text.replace("&#8220;", "\"")
    text = text.replace("&#8221;", "\"")
    text = text.replace("&#8222;","\"")
    text = text.replace("&#8230;","...")
    text = text.replace("--","-")
    return text

opt = webdriver.FirefoxOptions()
opt.add_argument('-headless')

if VERBOSE > 1: print("Opening webdriver...")
with webdriver.Firefox(options = opt) as driver:
    if VERBOSE: print("Webdriver opened.")
    
    pages = queue.Queue()
    pages.put(URL)

    # Sets up basic variables for the page loop.
    # The loop tracks the chapter number per book, page number per book, and page number per chapter.
    # It also tracks data related to what book from the comic is currently being produced.
    chapNum = 1
    pageNum = 1 
    chapPageNum = 1
    oldBookNum = 0
    oldBookTitle = ""
    oldChapterTitle = ""
    currChapter = ""
    end = False

    # toc and spine are needed for ebooklib's generation of ebooks.
    toc = []
    spine = ["nav"]

    while not pages.empty():
        # Moves you to the next page.
        page = pages.get()
        if page != driver.current_url:
            if VERBOSE > 1:
                print("Navigating to next page...")
            driver.get(page)
            if VERBOSE > 1:
                print("Arrived at page " + page)

        # Finds the current book and chapter name
        if VERBOSE > 1: print("Acquiring book and chapter...")
        titles = driver.find_element(By.CSS_SELECTOR,".strip-book").text
        if "Book" in titles:
            # The titles block for each page of the comic is formatted as:
            #   Book BOOKNUMBER: BOOKNAME - CHAPTERNAME
            # The following acquires the book number, name, and chapter name from strings following that format.

            newBookNum = int("".join([s for s in titles.split(": ", 1)[0] if s.isdigit()])) # Finds the number for the current page's book, by joining together all numerals in the titles string that come before the first colon.
            titles = titles.split(": ", 1)[1].split(" — ") # Drops the Book BOOKNUMBER part of the titles string, and splits the BOOKNAME - CHAPTER string on the dash.
            newBookTitle = titles[0].replace(": ", " - ") # Acquires the name of the book, and replaces any colons with a dash so as not to break filenames.
            newChapterTitle = titles[1].replace(": ", " - ") # Acquires the name of the chapter, and replaces any colons with a dash so as not to break filenames.
            if VERBOSE > 1: print(newBookTitle + ": Chapter " + newChapterTitle + ", page " + str(chapPageNum))
        else:
            # If the titles block doesn't include "Book", the current page is an extra after the completion of the comic, and the program should be concluded.
            end = True

        # If the current page belongs to a new chapter and we already have a chapter built, add the previously built chapter to the currently-selected book.
        if (newChapterTitle != oldChapterTitle or end) and currChapter:
            if VERBOSE:
                print(
                    "   Finished Chapter " + str(chapNum)
                    + " of Book " + str(oldBookNum) + ", with "
                    + str(chapPageNum-1) + " pages."
                )
            chap = epub.EpubHtml(
                title = oldChapterTitle,
                file_name = oldChapterTitle + ".xhtml",
                lang="en"
            )
            chap.set_content(currChapter)
            book.add_item(chap)
            spine.append(chap)
            toc.append(chap)
            chapNum += 1
            chapPageNum = 1
            currChapter = ""

        # If the current page belongs to a new book, set the details for that book and save it to a new file.
        # zfill(2) is used to make sure that all books are numbered with 2 digits, even books 1-9.
        if newBookTitle != oldBookTitle or end:
            # This if is needed to make sure that the program doesn't save an empty book when checking through the first page.
            if oldBookTitle:
                if VERBOSE:
                    print(
                        "Finished Book " + str(oldBookNum) + ", with "
                        + str(pageNum) + " pages."
                    )
                    print(
                        "Saving Book " + str(oldBookNum) + ", "
                        + oldBookTitle + "...")
                book.set_identifier("schlock" + str(oldBookNum).zfill(2))
                book.set_title(oldBookTitle)
                book.toc = toc
                book.spine = spine
                epub.write_epub(
                    str(oldBookNum).zfill(2) + ". "
                        + oldBookTitle + ".epub",
                    book)
                if VERBOSE:
                    print(
                        "Book " + str(oldBookNum) + ": "
                        + oldBookTitle + ", saved.")
                chapNum = 1
                pageNum = 1
                toc = []
                spine = ["nav"]

            # After the previous book has been saved, or at the beginning of the programming, creates a new book to be used in the future (unless only downloading 1 book)
            if "-b" in sys.argv:
                end = True
            else:
                book = epub.EpubBook()
                book.set_language("en")
                book.add_author("Howard Taylor")
                book.add_item(epub.EpubNcx())
                book.add_item(epub.EpubNav())
                book.spine = ["nav,"]

                # The first chapter of a new book is created with the HTML code for a title block.
                currChapter += """            
    <div style="display: block; margin: auto box-shadow: 5px 5px 10px black;">
        <h1> """ + newBookTitle + """ </h1>
        <h2> <i> by Howard Taylor </i> </h2> 
    </div>

    <div class="pagebreak" style="page-break-after: always" />
"""
        if end:
            # If the program has reached the end of comic, break the while loop even if there are still pages in the queue.
            break

        if chapPageNum == 1:
            # For the first page of each chapter, add the HTML code for a title block.
            if chapNum == 1:
                print(
                    "Beginning Book " + str(newBookNum) + ": "
                    + newBookTitle + "...")
            print("   Beginning Chapter " + str(chapNum) + ": " + newChapterTitle + "...")
            currChapter += """
<div style="display: block; margin: auto box-shadow: 5px 5px 10px black;">
    <center> <h3> """ + newChapterTitle + """ </h3> </center>
</div>

<div class="pagebreak" style="page-break-after: always" />
"""

        if VERBOSE > 1:
            print(
                "      Writing page " + str(pageNum)
                + " of Book " + str(newBookNum) + ": "
                + newBookTitle
            )
        # For each page, adds the HTML code for the pagenumber.
        currChapter += """
<center>
    <p> """ + newChapterTitle + """: Page """ + str(chapPageNum) + """ <p>
"""
        
        # Find the current comic or comics.
        if VERBOSE > 1:
            print(
                "         Acquiring comic " + str(newBookNum).zfill(2)
                + "-" + str(chapNum).zfill(2) + "-"
                + str(chapPageNum).zfill(4) + "..."
            )
        comics = driver.find_elements(
            By.CSS_SELECTOR,
            ".strip-image-wrapper img"
        )
        imgNum = 1
        if VERBOSE > 1:
            print("         Acquired comic. Writing to book...")
        for c in comics:
            # For each image in the page's strip - which may have 1-3 images - download the image, construct an image ID corresponding to the book, chapter, page, and imagenumber, the nadd it to the book as well as adding a page to the chapter.
            img = requests.get(c.get_attribute("src")).content
            imgID = str(newBookNum).zfill(2)
            imgID = imgID + "-" + str(chapNum).zfill(2)
            imgID = imgID + "-" + str(chapPageNum).zfill(4)
            imgID = imgID + "-" + str(imgNum).zfill(2)
            img = epub.EpubItem(uid = "img-" + imgID, file_name = imgID + ".jpg", content = img)
            book.add_item(img)

            currChapter += '    <img src="' + imgID + """.jpg" style="max-width: 95vw" />
    <br>
"""
            if VERBOSE > 1:
                print(
                    "            Wrote image " + str(imgNum) + " to book."
                )
            imgNum += 1
        
        currChapter += """</center>"""

        # Find the current footnote, if there is one.
        if VERBOSE > 1:
            print("         Looking for footnotes...")
        footnote = driver.find_elements(
            By.CSS_SELECTOR,
            ".strip-footnote"
        )
        if footnote:
            if VERBOSE > 1:
                print("         Found footnotes. Writing to book...")
            foot = clean_unicode(footnote[0].get_attribute("innerHTML"))
            currChapter += """
<p> """ + foot + """ </p>
            """
            if VERBOSE > 1:
                print(
                    "         Finished writing footnotes for page "
                    + str(pageNum) + "."
                )
        elif VERBOSE > 1:
            print(
                "         No footnotes found for page "
                + str(pageNum) + "."
            )
                
        if VERBOSE:
            print("      Wrote page " + str(pageNum) + " to book.")
        
        next = driver.find_element(By.CSS_SELECTOR, ".next-strip")
        next = next.get_attribute("href")
        pages.put(next)

        oldBookNum = newBookNum
        oldBookTitle = newBookTitle
        oldChapterTitle = newChapterTitle
        pageNum += 1
        chapPageNum += 1

print("Scraping complete.")