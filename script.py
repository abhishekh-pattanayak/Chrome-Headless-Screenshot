import os
import time
import numpy as np
import cv2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# Command for running chrome headless on docker
# docker run -d -p 4444:4444 --shm-size=2g selenium/standalone-chrome


def wait_for_ajax(driver):
    """ Function to wait for all ajax calls to end with a maximum limit of 15s """

    wait = WebDriverWait(driver, 15)
    try:
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except Exception as e:
        pass

def createDriver():
    """ Function for creating a new instance of chrome headless browser """
    # headless browser settings
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("start-maximized"); # open Browser in maximized mode
    chrome_options.add_argument("disable-infobars"); # disabling infobars
    chrome_options.add_argument("--disable-extensions"); # disabling extensions
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage"); # overcome limited resource problems
    driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=chrome_options)
    return driver

def remove_whitespace(path, filename):
    """Function to remove white space from y axis of downloaded images"""
    print(path + filename)
    img = cv2.imread(path + "uncropped/" + filename) # Read in the image and convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = 255*(gray < 128).astype(np.uint8) # To invert the text to white
    coords = cv2.findNonZero(gray) # Find all non-zero points (text)
    x, y, w, h = cv2.boundingRect(coords) # Find minimum spanning bounding box
    rect = img[y:y+h] # Crop the image - note we do this on the original image
    # cv2.imshow("Cropped", rect) # Show it
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    cv2.imwrite(path  + "cropped/" + filename, rect) # Save the image

def scroll_down(driver):
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load the page.
        time.sleep(2)
        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height
    # driver.execute_script("window.scrollTo(0, 0);")    

def take_screenshot(url, path, width="1920", height=None):
    """ Function for taking a screenshot. Default width is 1920 and minimum width is 1280. Default height is the website's scrollable height. """

    print("Visiting: {}".format(url))
    
    driver = createDriver()
    driver.get(url)
    scroll_down(driver)
    wait_for_ajax(driver)
    original_size = driver.get_window_size()
    
    if (int(width)>=1280):
        required_width = width
    else:
        required_width = 1280

    if height is None:
        required_height = driver.execute_script('return document.body.scrollHeight + 2000')
    else:
        required_height = height
    # print(required_width, required_height)

    driver.set_window_size(required_width, required_height)

    filepath = os.getcwd() + path
    filename = "screen_shot_{}.png".format(url.split("/")[2])
    driver.find_element_by_tag_name('body').screenshot(filepath+"uncropped/"+filename)
    remove_whitespace(filepath, filename)
    print("Saving screenshot: {}".format(filename))
    
    driver.close()



### Driver Function
if __name__=="__main__":
    
    path = "/screenshots/"
    
    ## Test links
    links = ["https://accordably.com/","https://www.bbc.com/", "https://nytimes.com/", "https://www.linkedin.com/", "https://pyup.io/", "https://news.ycombinator.com/"]
    # url = links[0]
    
    ## Testing on the 5 test links
    
    for link in links:
        take_screenshot(link, path)

    ## Ad Hoc screenshots
    
    # take_screenshot(links[0], path)