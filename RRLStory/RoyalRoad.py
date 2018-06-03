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

    def __init__(self,url:str):
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

    def __get_chapters_list__(self):
        source = self.storyPage.page
        links = source.select("table#chapters td > a[href]")
        self.chaptersUrl = list()
        for a in links:
            self.chaptersUrl.append([a.text, urljoin(self.url, a['href'])])
                
class Chapter:
    """
    Represent a Chapter from the story
    """
    def __init__(self, url:str):
        self.url = url
        #print(url)
        self.chapterPage = Fetcher(url)
        if not self.chapterPage.type == "Chapter":
            raise ValueError("Not a chapter page")
        t = getMetaValue(self.chapterPage.page, "og:title")
        self.title = t if t else getMetaValue(self.chapterPage.page, "twitter:title")
        d = getMetaValue(self.chapterPage.page, "description")
        self.description = d if d else getMetaValue(self.chapterPage.page, "twitter:description")
        next = getLink(self.chapterPage.page, "next")
        self.nextChapter = urljoin(self.url, next) if next else None
        prev = getLink(self.chapterPage.page, "prev")
        self.prevChapter = urljoin(self.url, prev) if prev else None
        source = self.chapterPage.page
        self.content = source.select(".chapter-inner.chapter-content")[0]
        
        
        

class Fetcher:
    """
    The Webpage content fetcher class
    """
    def __init__(self, url:str):
        #print("Fetching the content of a Webpage...", end='\t',flush=True)
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        options.add_argument('--disable-gpu')
        LOGGER.setLevel(logging.WARNING)
        self.driver = webdriver.Chrome( path.dirname(path.realpath(__file__)) + "/chromedriver", options=options,service_log_path="chrome_logs.log")
        parsedURL = urlparse(url)
        if not parsedURL.scheme:
            raise ValueError("Invalid URL Specified!!")
        elif not parsedURL.netloc == "royalroadl.com":
            raise ValueError("Not a Royal Road Legends Page")
        self.driver.get(url)
        self.driver.implicitly_wait(5)
        try:
            self.driver.find_element_by_css_selector("div#chapters_length > label > select option[value='-1']").click()
        except Exception:
            pass
        try:
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chapter-inner.chapter-content")))
        except:
            pass
        self.contents = self.driver.page_source
        self.page = BeautifulSoup(self.contents, "lxml")
        #ogType =self.page.find("meta",  property="og:type")
        ogType = getMetaValue(self.page, "og:type")
        #ogTitle = self.page.find("meta",  property="og:title")
        #ogTitle = getMetaValue(self.page, "og:title")
        if ogType == "books.book":
            self.type = "Story"
        elif ogType == "article":   #TODO: Find a more specific condition to filter chapter
            self.type = "Chapter"
        else:
            raise ValueError("Not a supported Page Type. Must be a Story or Chapter")
        self.driver.close()
        #print("[Done]")

def getMetaValue(soup: BeautifulSoup, prop:str):
    temp = soup.find("meta",  property=prop)
    p =  temp if temp else soup.find("meta",  attrs={"name":prop})
    return p["content"] if p else ""
def getLink(soup: BeautifulSoup, rel:str):
    link =  soup.find("link",  attrs={"rel":rel})
    return link["href"] if link else None


