# Amazon-Price-checker
 Python script to check Amazon prices and sends an email whether there is a sale or not.

This can be used in a Windows .bat file and Windows Task Scheduler to run the task at different intervals, e.g. Daily

I have also tested it on my raspberry pi using crontab. I have it set to send an email every day ay 9AM, and on days there will most likely be sales (Cyber Monday, Black Friday, etc) I have it set to send me an email every hour so I don't miss out on any deals :)


The script is just an example of one website, it can be used on any website that bs4 works with.

In the future, I will update the code to allow for multiple products to be checked and emails sent out accordingly.
