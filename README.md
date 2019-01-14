# Trademark Monitor

© Michaela Ockova, 2019. Please do not copy, distribute or modify the script trademark_monitor.py.

## Purpose:
Trademark Monitor facilitates searching of trademark applications in large trademark database TMview.
It allows user to define parameters of searching and provides user with output in form of html page
containing table with trademark applications found for each search round and url links to respective
trademark detailed page.

## Script structure:
1. Check operation system to install correct driver for Chrome.
2. Access Advanced Search Form
3. Run search round for each trademark for respective parameters and download the web page with results.
4. Extract table with data without unnecessary formatting and rewrite the original file with this data.
5. Extract ID and URL of a trademark application.
6. Create email with information on the ID, URL and with web pages attached to the email.
7. Send the email and close the browser.

## Plans for the next versions:
- add and test proper logging
- handle all frequent exceptions properly
- fix appearance of output data 
- create GUI in PyQT
- use headless browser
- prepare for other browsers if necessary
