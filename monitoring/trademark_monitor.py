# Trademark monitor fills out search form at www.tmnd.org with provided data,
# and sends the results as html text within an email to receiver's email address.
# Script is then run once a month via Cron.
#
# There has to be module :email_data with the variable named 'receiver'.
# The variable contains email address of the monitoring receiver.


import platform
import re
import os
import time
from pathlib import Path

from selenium.webdriver.chrome.webdriver import WebDriver
from seleniumwire import webdriver
from bs4 import BeautifulSoup
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import glob

from monitoring import email_data


class OSNotRecognized(Exception):
    """Raise if OS is not recognized."""


def check_os() -> WebDriver:
    """Check OS to install the correct driver for Chrome."""
    operation_system = platform.system()

    chromedriver_folder = Path(__file__).absolute().parents[1] / "chromedriver"

    if 'linux' in operation_system.lower():
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", chrome_options=options)
    elif 'darwin' in operation_system.lower():
        driver = webdriver.Chrome(executable_path=chromedriver_folder / "chromedriver_mac")
    elif 'win' in operation_system.lower():
        driver = webdriver.Chrome(executable_path=(chromedriver_folder / "chromedriver.exe"))
    else:
        raise OSNotRecognized('Couldn\'t find out your operation system. Program will stop.')
    return driver


def access_search_form(driver):
    """Open the website TrademarkView and access its advanced search form."""
    driver.get('https://www.tmdn.org/tmview/welcome')
    # Break captcha before proceeding
    driver.find_element_by_id('lnkAdvancedSearch').click()    # Access advanced search form


def search_trademarks(driver, trademark_name, nice_class, searched_id, vienna_class):
    """Fill out the advance search form with trademark parameters and download web page."""
    driver.find_element_by_class_name('DesignatedTerritoriesControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), "
                                 "'Select all EU member states')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), "
                                 "'Select all Non-EU member states')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), "
                                 "'Trade mark offices')]").click()    # Click away

    driver.find_element_by_class_name('SelectedOfficesControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Select All')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), "
                                 "'Trade mark offices')]").click()    # Click away

    driver.find_element_by_id('TrademarkName').send_keys(trademark_name)

    driver.find_element_by_class_name('TrademarkStatusControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Filed')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), "
                                 "'Trade mark offices')]").click()    # Click away

    driver.find_element_by_id('NiceClass').send_keys(nice_class)

    if vienna_class is not None:
        driver.find_element_by_id('ViennaClass').send_keys(vienna_class)

    driver.find_element_by_class_name('SortControl').click()
    driver.find_element_by_xpath("//select[@name='cmbSortField']"
                                 "/option[text()='Application date']").click()
    driver.find_element_by_xpath(".//*[contains(text(), "
                                 "'Trade mark offices')]").click()    # Click away

    driver.find_element_by_class_name('cmbOrderControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Descending')]").click()

    driver.find_element_by_id('SearchCopy').click()    # Start searching

    time.sleep(10)   # Wait till the database content loads
    print('Searched through successfully for TM {}'.format(searched_id))

    html_source = driver.page_source
    searched_name = searched_id
    with open('tm_{}.html'.format(searched_name), 'w', encoding='utf-8') as f:
        downloaded_doc = f.write(html_source)
    driver.find_element_by_id('btnClear').click()
    driver.find_element_by_id('lnkAdvancedSearch').click()  # Get back to advanced search form


def edit_downloaded_html() -> str:
    """Delete files with no search results and remove unnecessary code from downloaded html."""
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
            to_be_kept = re.compile(('(?=<table border="0" cellpadding="0" cellspacing="0" '
                                     'class="ui-pg-table" ).*(?<=id="rs_mgrid")'), flags=re.DOTALL
                                    ).findall(str(whole_table))
            string_to_be_kept = ''.join(to_be_kept)
            with open(tm_file, 'w', encoding='utf-8') as f:
                f.write(string_to_be_kept)
    path = glob.glob('tm_*.html')
    return path


def get_trademark_url(downloaded_htmls) -> list:
    """Parse the data, extract trademark application ID and url and save all in a dictionary."""
    tm_name_url_list = []
    for clean_tm_file in downloaded_htmls:

        html = open(clean_tm_file, 'r', encoding='utf-8')
        soup = BeautifulSoup(html, 'lxml')
        results_ids = soup.find_all('div', id=re.compile("flag_rowId_"))
        all_clean_ids = list(re.compile('(?=flag_rowId_).*?\"', flags=re.MULTILINE | re.IGNORECASE)
                             .findall(str(results_ids)))
        map(lambda value: re.sub('(\"|flag_rowId)', '', value), all_clean_ids)
        for i, value in enumerate(all_clean_ids):
            no_quotation = value.replace('\"', '')
            no_id = no_quotation.replace('flag_rowId_', '')
            include_name = 'for code ' + no_id + ' in file ' + clean_tm_file + ': '
            new_value = include_name
            all_clean_ids[i] = value.replace(value, new_value)
            created_url = 'https://www.tmdn.org/tmview/get-detail?st13=%s' % no_id
            one_link_url_dict = dict()
            one_link_url_dict[new_value] = created_url
            tm_name_url_list.append(one_link_url_dict)
    return tm_name_url_list


def send_email(get_trademark_url, email_data):
    """Send email with web page with search results in email attachment
    and urls of each trademark."""
    urls_list = get_trademark_url

    tm_database_files = glob.glob('tm_*.html')
    fromaddr = email_data.sender
    toaddr = email_data.receiver
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Trademark monitoring results"

    msg_intro = MIMEText("Dears,\n\nbelow see the results from the trademark monitoring "
                         "made after a month. Attached find the tables of results for "
                         "particular keywords. In case you would like to investigate "
                         "suspicious applications, click on the relevant link depending "
                         "on the trademark application number:\n", 'plain')
    msg.attach(msg_intro)

    msg_urls = MIMEText(('\n'.join('{}\n'.format(value) for value in urls_list))
                        .replace('{', '').replace('}', '').replace('\'', ''), 'plain')
    msg.attach(msg_urls)

    for file in tm_database_files:
        with open(file, "rb") as f:
            msg_attachments = MIMEApplication(f.read(), name=os.path.basename(file))
        msg_attachments['Content-Disposition'] = 'attachment; filename="%s"' % \
                                                 os.path.basename(file)
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
    print("Email sent!")


def finish_search(driver):
    """Close browser."""
    driver.close()
    driver.quit()


def run_trademark_check():
    driver = check_os()
    access_search_form(driver=driver)

    trademarks_to_check = [
        ('*trez*r*', '9,36,38,42', 'trezor', None),
        ('*tres*r*', '9,36,38,42', 'tresor', None),
        ('*satoshi*', '9,35,36,38,42', 'satoshi', None),
        ('*trez*r*', '9,35,36,38,42', 'trezor logo', '14.05.21,14.05.23'),
        ('*tres*r*', '9,35,36,38,42', 'tresor logo', '14.05.21,14.05.23'),
        ('*satoshi*', '9,35,36,38,42', 'satoshi logo', '14.05.21,14.05.23')
        ]

    for trademark in trademarks_to_check:
        trademark_name, nice_class, searched_id, vienna_class = trademark
        search_trademarks(driver, trademark_name, nice_class, searched_id, vienna_class)

    edited_html = edit_downloaded_html()
    trademark_url = get_trademark_url(edited_html)
    send_email(trademark_url, email_data)
    finish_search(driver)


if __name__ == '__main__':
    run_trademark_check()
