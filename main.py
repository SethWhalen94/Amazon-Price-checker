import requests
from bs4 import BeautifulSoup
import smtplib
from string import Template
import os
#======================================
# GLOBALS
#======================================
URL = 'https://www.amazon.ca/TCL-Dolby-Vision-QLED-Smart/dp/B088517GLM'             # URL for TCL Series 5 50 inch TV, CHANGE AS NEEDED
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
ATTEMPTS = 10
CONTACTS = os.getcwd() + '\\contacts.txt'
SENDER = 'sender_email@email.com'           # Place the email you wish to send from
SENDER_PASSWORD = 'password123'             # Password for sender email
NO_SALE_PRICE = 529.99                      # Set the current price or max price or no sale price of the item

#======================================
# Method to get contacts from file
#======================================
def get_contacts(filename):
    emails = []

    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for contact in contacts_file:
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
def check_price():

    page = requests.get(URL, headers = headers, timeout=None)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find(id='productTitle').getText().strip()              # NOTE: This is depended on what website you are wanting to parse, check Chrome console for appropriate id, class, etc
    price = soup.find(id="priceblock_ourprice").getText().strip()[5:]   # Price of product as string, see above note
    price = float(price)                                                # Convert price string to float
    print(title)
    print(price)

    if (price < NO_SALE_PRICE):            # Send an email if the product is on sale
        send_email(title, price)
    else:                           # send email even if product isn't on sale
        send_email(title, price)

#======================================
# Method to send email to contacts.
# params::
# title - Item title (string)
# price - reduced price of item (float)
# error - exception message (string)
#======================================
def send_email(title, price = 0.0, error = None):
    server = smtplib.SMTP('smtp.gmail.com', port=587, timeout=None) # Connect to mail server
    emails = get_contacts(CONTACTS)
    # message_template = read_message_template('message.txt')
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(SENDER, SENDER_PASSWORD)   # Login to sender's email

    # there must have been an error, send an email
    if(title == 'ERROR'):
        subject = 'Error in Amazon Price Python Script'
        body = ('There was an error when calling check_price() function\n%s' %error)
        message = f"Subject: {subject}\n\n{body}"

    # Send a daily email anyways if product isn't on sale
    elif(price >= NO_SALE_PRICE):
        subject = 'No Sale Today - TCL 50" 5-Series'
        body = ("The price of the %s is still $%s.\nCheck the Amazon link if you want: %s" % (title, price, URL))

        message = f"Subject: {subject}\n\n{body}"

    # No error, price reduced, send regular email
    else:
        subject = 'TV Price Reduced!!!! - TCL 50" 5-Series'
        body = ("The price of the %s reduced to $%s!\nCheck the Amazon link %s" % (title, price, URL))

        message = f"Subject: {subject}\n\n{body}"

    for email in emails:
        server.sendmail(
            from_addr=SENDER,
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
    for attempt in range(ATTEMPTS):             # Try getting the page content several times since page may return
        try:                                    # Status = 200 if page skeleton is loaded before all content
            sent = True
            check_price()
            break

        except AttributeError as err:
            print("An exception was raised")
            sent = False

    if(not sent):
        send_email('ERROR')


