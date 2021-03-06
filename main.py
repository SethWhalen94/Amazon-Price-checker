from bs4 import BeautifulSoup
import smtplib
from string import Template
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
#======================================
# GLOBALS
#======================================
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
ATTEMPTS = 10
CONTACTS = os.path.join(os.path.dirname(__file__), 'contacts.txt')
SENDER = {'email': 'email2@gmail.com', 'password': '123456'}                      # Place the email credentials here that you wish to send from
URLS = os.path.join(os.path.dirname(__file__), 'URLS.txt')

#======================================
# Method to get contacts from file
#======================================
def get_contacts(filename):
    emails = []

    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        lines = (line.rstrip() for line in contacts_file)  # All lines including the blank ones
        lines = (line for line in lines if line)  # Non-blank lines
        for contact in lines:
            if(len(contact) > 0):
                emails.append(contact.split()[0])

    return emails
#======================================
# Method to read from message template
#======================================
def read_message_template(filename):
    with open(filename, mode='r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()

    return Template(template_file_content)

#=============================================
# Method to retrieve URL info and check price
#==============================================
def check_price(url, no_sale_price, browser):

    browser.get(url)
    page = browser.page_source
    soup = BeautifulSoup(page, 'html.parser')
    title = soup.find(id='productTitle').getText().strip()              # NOTE: This is depended on what website you are wanting to parse, check Chrome console for appropriate id, class, etc


    price = soup.find(id="priceblock_ourprice")
    if(price != None):
        price = price.getText().strip()[5:]                             # Price of product as string, see above note
        price = float(price)                                            # Convert price string to float

    coupon = None
    try:
        coupon = browser.find_element_by_css_selector(
            "#vpcButton > div > label > span > span")  # Check if there is a coupon
    except:
        print("There is no coupon")
    if(coupon):
        print("There is a coupon")
        coupon = browser.find_element_by_css_selector(
            "#vpcButton > div > label > span > span")  # Check if there is a coupon
        coupon = re.search('[0-9]{0,3}\.[0-9]{0,2}',coupon.text)        # Parse the coupon string for the price
        coupon = float(coupon.group(0))                             # Get text from re.match object, set to float


    deal_price = soup.find(id='priceblock_dealprice')                   # Check if there is a deal price

    if (deal_price != None):                                            # If the deal price exists, then parse it from the HTML element
        #print("There is a deal!!!!!!")
        deal_price = float(deal_price.getText().strip()[5:])            # Get text from span element, and convert price to a float

    #print(title)
    #print(price)
    #print(deal_price)

    if (deal_price != None):                               # Send an email if the product is on sale
        send_email(title=title, price=deal_price, no_sale_price=no_sale_price, url=url)
    elif (coupon != None):  # send email if there is a coupon
        send_email(title=title, price=no_sale_price, no_sale_price=no_sale_price, url=url, coupon=coupon)
    elif(price != None):                                                  # send email even if product isn't on sale
        send_email(title=title, price=price, no_sale_price=no_sale_price, url=url)
    else:
        send_email(title=title, price=no_sale_price, no_sale_price=no_sale_price, url=url)

#======================================
# Method to send email to contacts.
# params::
# title - Item title (string)
# price - reduced price of item (float)
# error - exception message (string)
#======================================
def send_email(title, url='', price = 0.0, error = None, no_sale_price = 0.0, coupon=0.0):
    server = smtplib.SMTP('smtp.gmail.com', port=587, timeout=None) # Connect to mail server
    emails = get_contacts(CONTACTS)
    # message_template = read_message_template('message.txt')
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(SENDER['email'], SENDER['password'])   # Login to sender's email

    # there must have been an error, send an email
    if(title == 'ERROR'):
        subject = 'Error in Amazon Price Python Script'
        body = ('There was an error when calling check_price() function\n%s' %error)

    # Send a daily email anyways if product isn't on sale
    if(price >= no_sale_price):
        subject = 'No Sale Today - ' + title
        body = ("The price of the %s is still $%s.\nCheck the Amazon link if you want: %s" % (title, price, url))

    # there is a coupon
    if(coupon > 0):
        subject = ('There Is A Coupon For $%s : %s' %(coupon, title))
        body = ("%s has a coupon worth $%s!\nCheck the Amazon link %s" % (title, coupon, url))
    # No error, price reduced, send regular email
    if(price < no_sale_price):
        subject = 'Price Reduced!!!! - ' + title
        body = ("The price of the %s reduced to $%s!\nCheck the Amazon link %s" % (title, price, url))

    message = ("Subject: %s\n\n%s" % (subject, body))

    for email in emails:
        server.sendmail(
            from_addr=SENDER['email'],
            to_addrs=email,
            msg=message
        )
        print("Email has been sent to %s" %email)

    server.quit()               # Quit the server


#======================================
# try to send an email, create .bat file and windows task to run this daily
# or simply run in a loop
# Can also use crontab in Linux to schedule this to run as an .exe daily, weekly, etc
#======================================

if(__name__ == '__main__'):

    urls = []                                   # Array to hold URLs from URLS.txt
    no_sale_prices = []                         # Array to hold no sale prices
    sent = False

    with open(URLS, mode='r', encoding='utf-8') as url_file:
        lines = (line.rstrip() for line in url_file)        # All lines including the blank ones
        lines = (line for line in lines if line)            # Non-blank lines
        for url in lines:
                urls.append(url.split()[0])                 # add url to urls array
                no_sale_prices.append(url.split()[1])       # add 'no sale price' to array

    # Set options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(ChromeDriverManager().install())  # Start selenium session

    for prod in range(len(urls)):                   # Since the 2 arrays (urls and no_sale_prices) are the same length, have an iterator so we can pass them as seperate arguments to chack_price
        for attempt in range(ATTEMPTS):             # Try getting the page content several times since page may return
            try:                                    # Status = 200 if page skeleton is loaded before all content
                sent = True
                check_price(urls[prod], float(no_sale_prices[prod]), browser)
                break

            except AttributeError as err:
                print("An exception was raised")
                sent = False

        if(not sent):
            send_email('ERROR')

    browser.close()                         # Close the Selenium browser
