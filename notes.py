def search_process(driver, trademark_name, nice_class, vienna_class=None):
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

    time.sleep(5)   # Wait till the database content loads
    print('Searched through successfully for TM {}'.format(trademark_name))
    html_source = driver.page_source
    with open('sourcefile.html', 'w', encoding='utf-8') as f:
        f.write(html_source)
    filename = 'sourcefile.html'
    return filename