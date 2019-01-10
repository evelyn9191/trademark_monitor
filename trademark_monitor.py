# Trademark monitor fills out search form at www.tmnd.org with provided data,
# and sends the results as html text within an email to receiver's email address.
# Script is then run once a month via Cron.
#
# There has to be module :email_data with the variable named 'receiver'.
# The variable contains email address of the monitoring receiver.
# There has to be module recaptcha_solved.py. For the detailed data on the code
# see: http://scraping.pro/recaptcha-solve-selenium-python/#whole_code
# TODO: Chrome should not be seen working if send_results function will be fixed.
# If it won't be fixed, opening in new window is needed to be planned.

import platform
import time
import re
import os

from selenium import webdriver
from bs4 import BeautifulSoup
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import glob

import email_data


class OSNotRecognized(Exception):
    """Raise if OS is not recognized."""


def check_os():
    """Check operation system to install correct driver for Chrome.

    :return Correct driver needed for Selenium module.
    """
    operation_system = platform.system()
    if 'linux' in operation_system.lower():
        driver = webdriver.Chrome('chromedriver\chromedriver_linux64')
    elif 'darwin' in operation_system.lower():
        driver = webdriver.Chrome('chromedriver\chromedriver_mac64')
    elif 'win' in operation_system.lower():
        driver = webdriver.Chrome('chromedriver\chromedriver_win32.exe')
    else:
        raise OSNotRecognized('Couldn\'t find out your operation system. Program will stop.')
    return driver


def access_search_form(driver):
    """Open advanced search form.

    Opens website and advanced search form. The URL of the form will later be used
    to return to the main page (and not the form particularly, because the URL on the
    website doesn't change with actions performed).

    :param driver: Chrome webdriver needed for Selenium module to work properly.
    :return: URL of the main page.
    """
    driver.get('https://www.tmdn.org/tmview/welcome')
    while True:
        try:
            driver.find_element_by_id('buttonBox').click()    # Accept cookies
        except selenium.common.exceptions.NoSuchElementException:
            driver.close()
        break
    # NameError: name 'selenium' is not defined
    driver.find_element_by_id('lnkAdvancedSearch').click()    # Access advanced search form
    main_page_url = driver.current_url
    return main_page_url


def search_process(driver, trademark_name, nice_class, searched_id, vienna_class=None):    # TODO: last search 9/1/2019
    """Fill out the search form.

    :param driver: Chrome webdriver needed for Selenium module to work properly.
    :param trademark_name: Search query for similar trademark names.
    :param nice_class: Search query for registered Nice classes of company trademark.
    :param vienna_class: Search query for registered Vienna classes of company logo.
    :return: None.
    """
    driver.find_element_by_class_name('DesignatedTerritoriesControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Select all EU member states')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Select all Non-EU member states')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Trade mark offices')]").click()    # Click away

    driver.find_element_by_class_name('SelectedOfficesControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Select All')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Trade mark offices')]").click()    # Click away

    driver.find_element_by_id('TrademarkName').send_keys(trademark_name)

    driver.find_element_by_class_name('TrademarkStatusControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Filed')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Trade mark offices')]").click()    # Click away

    driver.find_element_by_id('NiceClass').send_keys(nice_class)

    if vienna_class is not None:
        driver.find_element_by_id('ViennaClass').send_keys(vienna_class)
    else:
        pass

    driver.find_element_by_class_name('SortControl').click()
    driver.find_element_by_xpath("//select[@name='cmbSortField']/option[text()='Application date']").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Trade mark offices')]").click()    # Click away

    driver.find_element_by_class_name('cmbOrderControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Descending')]").click()

    driver.find_element_by_id('SearchCopy').click()    # Start searching

    time.sleep(10)   # Wait till the database content loads
    print('Searched through successfully for TM {}'.format(trademark_name))
    html_source = driver.page_source
    searched_name = searched_id
    with open('tm_{}.html'.format(searched_name), 'w', encoding='utf-8') as f:
        downloaded_doc = f.write(html_source)
    driver.find_element_by_id('btnClear').click()
    driver.find_element_by_id('lnkAdvancedSearch').click()  # Get back to advanced search form
    return downloaded_doc


def edit_downloaded_html():
    """Delete files with no search results and remove unnecessary code from downloaded html.

    :return: str Path to all html files needed for later use.
    """
    path = glob.glob('tm_*.html')
    for tm_file in path:
        html = open(tm_file, 'r', encoding='utf-8')
        soup = BeautifulSoup(html, 'lxml')
        no_results = soup.find('span', class_='noresults')
        if no_results is not None:
            html.close()
            os.remove(tm_file)
        else:
            whole_table = soup.find_all('div', id="table_of_results")
            print(whole_table)
            to_be_kept = re.compile(('(?=<table border="0" cellpadding="0" cellspacing="0" '
                                     'class="ui-pg-table" ).*(?<=id="rs_mgrid")'), flags=re.DOTALL
                                    ).findall(str(whole_table))
            string_to_be_kept = ''.join(to_be_kept)
            with open(tm_file, 'w', encoding='utf-8') as f:
                new_html = f.write(string_to_be_kept)
    return path


def get_trademark_url(edit_downloaded_html):
    tm_name_url_list = []
    for clean_tm_file in edit_downloaded_html:

        html = open(clean_tm_file, 'r', encoding='utf-8')
        soup = BeautifulSoup(html, 'lxml')
        results_ids = soup.find_all('div', id=re.compile("flag_rowId_"))
        print(results_ids)
        all_clean_ids = list(re.compile('(?=flag_rowId_).*?\"', flags=re.MULTILINE|re.IGNORECASE).findall(str(results_ids)))
        print(all_clean_ids)

        url_dict = {}
        for i, value in enumerate(all_clean_ids):
            no_quotation = value.replace('\"', '')
            no_id = no_quotation.replace('flag_rowId_', '')
            new_value = no_id
            all_clean_ids[i] = value.replace(value, new_value)
            created_url = 'https://www.tmdn.org/tmview/get-detail?st13=%s' % new_value
            url_dict[all_clean_ids[i]] = created_url

        tm_name_url_list.append(url_dict)
    print(tm_name_url_list)
    return tm_name_url_list


def create_email(get_trademark_url, email_data):
    """Send email with links to articles.

    Put class with articles into email as HTML language and send it.

    :param [str] check_articles: List with extracted article titles and links.
    :param module email_data: Module with variables with email access info.
    """
    url_dict = get_trademark_url()
    tm_database_files = glob.glob('tm_*.html')
    fromaddr = email_data.sender
    toaddr = email_data.receiver
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Trademark monitoring results"

    msg_intro = MIMEText("Dears,\nPlease see the results from the trademark monitoring "
                         "made for last month. Attached find the tables of results for "
                         "particular keywords. In case you would like to investigate "
                         "suspicious applications, click on the relevant link depending "
                         "on the trademark application number:\n\n", 'plain')
    msg.attach(msg_intro)

    msg_urls = MIMEText('\n\n'.join('{}\n{}'.format(key, value) for key, value in url_dict.items()), 'plain')
    msg.attach(msg_urls)

    for file in tm_database_files:
        with open(file, "rb") as f:
            msg_attachments = MIMEApplication(f.read(), name=basename(file))
        msg_attachments['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(msg_attachments)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.connect('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(fromaddr, email_data.openkeyword)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    print("Email successfully sent!")


def reset_search(driver):
    driver.find_element_by_id('btnClear').click()
    driver.find_element_by_id('lnkAdvancedSearch').click()

'''
def send_results(driver, email_data, trademark_name):
    """Fill out the send form.

    Fills out the send form, solves recaptcha and send email with link to search results.

    :param driver: Chrome webdriver needed for Selenium module to work properly.
    :param email_data: Contains email address of receiver or the email with search results.
    :return: None.
    """
    driver.find_element_by_xpath('.//input[@id="name"]').send_keys('Trademark Monitor for {}'.format(trademark_name))
    driver.find_element_by_xpath('.//input[@id="email"]').send_keys(email_data.receiver)
    driver.find_element_by_id("captchaBox").click()
    time.sleep(3)
    driver.find_element_by_id('btnSubmitUserForm').click()
    #driver.find_element_by_id('lnkAdvancedSearch').click()    # Get back to advanced search form
    print('Sent successfully for {}'.format(trademark_name))

        
    
    < a

    class ="ui-pg-div" id="inviteFriend" title="Share with a friend" onclick="InviteFriend.open();" > < / a >
    driver.find_element_by_id('btnClear').click()
    driver.find_element_by_id('lnkAdvancedSearch').click()  # Get back to advanced search form
'''

def finish_search(driver):
    driver.close()
    driver.quit()


def main(driver, access_search_form, search_process, edit_downloaded_html, get_trademark_url):
    driver = check_os()
    access_search_form = access_search_form(driver=driver)
    trezor_tm = search_process(driver=driver, trademark_name='*trez*r*', nice_class='9,36,38,42', searched_id='trezor')
    tresor_tm = search_process(driver=driver, trademark_name='*tres*r*', nice_class='9,36,38,42', searched_id='tresor')
    satoshilabs_tm = search_process(driver=driver, trademark_name='*satoshi*', nice_class='9,35,36,38,42',
                                    searched_id='satoshi')
    logo_trezor_tm = search_process(driver=driver, trademark_name='*trez*r*', nice_class='9,35,36,38,42',
                                    vienna_class='14.05.21,14.05.23', searched_id='trezorlogo')
    logo_tresor_tm = search_process(driver=driver, trademark_name='*tres*r*', nice_class='9,35,36,38,42',
                                    vienna_class='14.05.21,14.05.23', searched_id='tresor_logo')
    logo_satoshi_tm = search_process(driver=driver, trademark_name='*satoshi*', nice_class='9,35,36,38,42',
                                     vienna_class='14.05.21,14.05.23', searched_id='satoshilogo')
    finish_search(driver)
    edit_downloaded_html = edit_downloaded_html()
    get_trademark_url = get_trademark_url(edit_downloaded_html=edit_downloaded_html)

if __name__ == '__main__':
    edit_downloaded_html = edit_downloaded_html()
    get_trademark_url = get_trademark_url(edit_downloaded_html=edit_downloaded_html)
    #main(check_os, access_search_form, search_process, edit_downloaded_html, get_trademark_url)
    # create_email(get_trademark_url, email_data)
    #trezor_tm = search_process(driver=driver, trademark_name='*tres*r*', nice_class='9,36,38,42', searched_id='tresor')
    #send_results(driver=driver, email_data=email_data, trademark_name='*tres*r*')
    #satoshilabs_tm = search_process(driver=driver, trademark_name='*satoshi*', nice_class='9,35,36,38,42', searched_id='satoshi')
    #send_results(driver=driver, email_data=email_data)
    #logo_trezor_tm = search_process(driver=driver, trademark_name='*trez*r*', nice_class='9,35,36,38,42',
                             #vienna_class='14.05.21,14.05.23', searched_id='trezorlogo')
    #send_results(driver=driver, email_data=email_data)
    #logo_tresor_tm = search_process(driver=driver, trademark_name='*tres*r*', nice_class='9,35,36,38,42',
                                    #vienna_class='14.05.21,14.05.23', searched_id='tresor_logo')
    #send_results(driver=driver, email_data=email_data)
    #logo_satoshi_tm = search_process(driver=driver, trademark_name='*satoshi*', nice_class='9,35,36,38,42', vienna_class='14.05.21,14.05.23', searched_id='satoshilogo')
    #send_results(driver=driver, email_data=email_data, trademark_name='*satoshi*')
    #finish_search(driver=driver)
