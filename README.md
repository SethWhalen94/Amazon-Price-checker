# Amazon-Price-checker
To run this script you will need the following dependancies
```
Python version >=3.6
selenium
webdriver-manager
bs4
smtplib
```
 Python script to check Amazon prices and sends an email whether there is a sale or not.

This can be used in a Windows .bat file and Windows Task Scheduler to run the task at different intervals, e.g. Daily

I have also tested it on my raspberry pi using crontab. I have it set to send an email every day ay 9AM, and on days there will most likely be sales (Cyber Monday, Black Friday, etc) I have it set to send me an email every hour so I don't miss out on any deals :)


The script is just an example of one website, it can be used on any website that bs4 works with.

In the future, I will update the code to allow for multiple products to be checked and emails sent out accordingly.


EDIT: I have updated the scripts functionality. I have parameterized some more pieces of the code for ease of use.
I also moved to using Selenium, since it waits for the front end DOM to load before grabbing the HTML of the page. This removes the problem that the requests library was having with waiting for the entire page to load before grabbing the HTML DOM.

I created a URLS.txt file where you should place the amazon product URL(s) followed by a space, then the NO SALE PRICE listed on amazon
for example, your URLS.txt file could look like:
```
https://www.amazon.ca/TCL-Dolby-Vision-QLED-Smart/dp/B088517GLM/ 529.99
https://www.amazon.ca/PERLESMITH-Universal-Stand-Table-37-55/dp/B07CNZN2B1/ 41.99
```

NOTE: blank lines at the end of the file are fine, as they are parsed out.

In order to run this on a rasberry pi, there were a couple extra things I needed to do since I have a Rasperry 3B+ that was running python 3.4, which is too old of a version to use some of the libraries needed.

Steps to use with Raspberry Pi
=

Before doing anything, make sure to update and upgrade. Run the command
```
sudo apt-get update && upgrade
```
Next, you need to download the appropriate chrome driver (it will be a .deb file) from [here](https://launchpad.net/ubuntu/bionic/armhf/chromium-chromedriver/)
To check your version of Chromium, open up a browser on your Pi and enter **about:** in the URL bar.

After downloading the .deb file, navigate to its directory in the terminal and run the command
```
sudo dpkg -i file_name.deb
```

Next you need to update and upgrade again, to allow the package to be applied
```
sudo apt-get update && upgrade
```

Now, inside the main.py file, you will need to change line 130 (I believe) which will currently be
```python
browser = webdriver.Chrome(ChromeDriverManager().install())  # Start selenium session
```
To 
```python
browser = webdriver.Chrome()  # Start selenium session
```

Now navigate to the projects directory and change the python script main.py to an executable
```
sudo chmod +x main.py
```
You should now be able to run it from command line with (command if you are in the files directory)
```
./main.py
```

To set up scheduling I used crontab, I reccommend looking at the following tutorial on how to set it up:
[how-to-automate-run-your-python-script-in-your-raspberry-pi](https://medium.com/analytics-vidhya/how-to-automate-run-your-python-script-in-your-raspberry-pi-b6fe652443db)
