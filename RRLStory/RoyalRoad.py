import logging
from selenium import webdriver
from urllib.parse import urlparse
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
from bs4 import BeautifulSoup
from os import path

logging.basicConfig(level=logging.WARNING)

class Story:
    """
    Represent the whole Stroy Object
    """

    def __init__(self,url):
        self.url = url
        self.storyPage = Fetcher(url)
        if not self.storyPage.type == "Story":
            raise ValueError("Not a story page")
        #self.author = self.storyPage.page.find("meta",  property="books:author")
        self.author = getMetaValue(self.storyPage.page, "books:author")
        #self.ratingValue = self.storyPage.find("meta",  property="books:rating:value")
        self.ratingValue = getMetaValue(self.storyPage.page, "books:rating:value")
        #self.ratingScale = self.storyPage.find("meta",  property="books:rating:scale")
        self.ratingScale = getMetaValue(self.storyPage.page, "books:rating:scale")
        self.isbn = getMetaValue(self.storyPage.page, "books:isbn")
        t = getMetaValue(self.storyPage.page, "og:title")
        self.title = t if t else getMetaValue(self.storyPage.page, "twitter:title")
        self.description = getMetaValue(self.storyPage.page, "og:description")
        self.__get_chapters_list__()
        print(self.chaptersUrl)

    def __get_chapters_list__(self):
        source = self.storyPage.page
        links = source.select("table#chapters td > a[href]")
        self.chaptersUrl = list()
        for a in links:
            if a.text.strip().startswith("Chapter"):
                self.chaptersUrl.append(urljoin(self.url, a['href']))
        
        

class Fetcher:
    """
    The Webpage content fetcher class
    """
    print("Fetching the content of a Webpage...", end='\t')
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    LOGGER.setLevel(logging.WARNING)
    driver = webdriver.Chrome( path.dirname(path.realpath(__file__)) + "/chromedriver", options=options)
    def __init__(self, url):
        parsedURL = urlparse(url)
        if not parsedURL.scheme:
            raise ValueError("Invalid URL Specified!!")
        elif not parsedURL.netloc == "royalroadl.com":
            raise ValueError("Not a Royal Road Legends Page")
        self.driver.get(url)
        self.driver.implicitly_wait(5)
        self.driver.find_element_by_css_selector("div#chapters_length > label > select option[value='-1']").click()
        self.contents = self.driver.page_source
        self.page = BeautifulSoup(self.contents, "lxml")
        #ogType =self.page.find("meta",  property="og:type")
        ogType = getMetaValue(self.page, "og:type")
        #ogTitle = self.page.find("meta",  property="og:title")
        ogTitle = getMetaValue(self.page, "og:title")
        if ogType == "books.book":
            self.type = "Story"
        elif ogType == "article" and ogTitle.startswith("Chapter "):
            self.type = "Chapter"
        else:
            raise ValueError("Not a supported Page Type. Must be a Story or Chapter")
        self.driver.close()
        print("[Done]")

def getMetaValue(soup: BeautifulSoup, prop:str):
    temp = soup.find("meta",  property=prop)
    p =  temp if temp else soup.find("meta",  attrs={"name":prop})
    return p["content"] if p else ""


