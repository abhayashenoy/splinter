from splinter.driver import DriverAPI, ElementAPI
from splinter.meta import InheritedDocs
from splinter.element_list import ElementList
from splinter.cookie_manager import CookieManagerAPI
from phantomjs import Server
import os
import time
import json
import re

class PhantomJSDriver(DriverAPI):
  driver_name = 'PhantomJS'
  wait_time = 0

  def __init__(self):
    self.server = Server()
    self.server.start()
    self.client = os.spawnlp(os.P_NOWAIT, 'phantomjs', 'phantomjs', '/Users/pivotal/workspace/poltergeist/lib/capybara/poltergeist/client/compiled/main.js', '9999')
    time.sleep(2)

  def quit(self):
    self.server.stop()

  def visit(self, url):
    self.command('visit', url)

  @property
  def title(self):
    return self.find_by_tag('title').first.text

  def __enter__(self):
    """
    Context manager to use the browser safely.
    """
    raise NotImplementedError("%s doesn't support use by 'with' statement." % self.driver_name)

  def __exit__(self):
    """
    Context manager to use the browser safely.
    """
    raise NotImplementedError("%s doesn't support use by 'with' statement." % self.driver_name)

  @property
  def html(self):
    return self.command('source')

  @property
  def url(self):
    return self.command('current_url')

  def back(self):
    current_url = self.url
    self.execute_script('window.history.back()')
    while (self.url == current_url or self.url[0] != 'h'):
      pass

  def forward(self):
    current_url = self.url
    self.execute_script('window.history.forward()')
    while (self.url == current_url or self.url[0] != 'h'):
      pass

  def reload(self):
    self.execute_script('window.location.reload()')

  def get_alert(self):
    """
    Changes the context for working with alerts and prompts.

    For more details, check the :doc:`docs about iframes, alerts and prompts </iframes-and-alerts>`
    """
    raise NotImplementedError("%s doesn't support alerts." % self.driver_name)

  def get_iframe(self, name):
    """
    Changes the context for working with iframes.

    For more details, check the :doc:`docs about iframes, alerts and prompts </iframes-and-alerts>`
    """
    raise NotImplementedError("%s doesn't support frames." % self.driver_name)

  def execute_script(self, script):
    self.command('execute', script)

  def evaluate_script(self, script):
    return self.command('evaluate', script)

  def find_by_css(self, css_selector):
    from cssselect import GenericTranslator, SelectorError
    try:
      expression = GenericTranslator().css_to_xpath(css_selector)
    except SelectorError:
      raise
    return self.find_by_xpath(expression)

  def find_by_xpath(self, xpath, limit=None):
    response = self.command('find', xpath)
    page_id = response['page_id']
    if limit and response['ids']:
      response['ids'] = response['ids'][:limit]
    return ElementList([PhantomElementAPI(self, page_id, element_id) for element_id in response['ids']], driver=self)

  def find_by_name(self, name):
    return self.find_by_xpath('//*[@name="%s"]' % name)

  def find_by_id(self, id):
    return self.find_by_xpath('//*[@id="%s"]' % id, 1)

  def find_by_value(self, value):
    return self.find_by_xpath('//*[@value="%s"]' % value)

  def find_by_tag(self, tag):
    return self.find_by_xpath('//%s' % tag)

  def find_link_by_href(self, href):
    return self.find_by_xpath('//a[@href="%s"]' % href)

  def find_link_by_partial_href(self, partial_href):
    return self.find_by_xpath('//a[contains(@href, "%s")]' % partial_href)

  def find_link_by_text(self, text):
    return self.find_by_xpath('//a[text()="%s"]' % text)

  def find_link_by_partial_text(self, partial_text):
    return self.find_by_xpath('//a[contains(text(), "%s")]' % partial_text)

  def find_option_by_value(self, value):
    return self.find_by_xpath('//option[@value="%s"]' % value)

  def find_option_by_text(self, text):
    return self.find_by_xpath('//option[text()="%s"]' % text)

  def is_text_present(self, text, wait_time=None):
    wait_time = wait_time or self.wait_time
    end_time = time.time() + wait_time

    while time.time() < end_time:
      if not self.find_by_xpath('//*[contains(text(), "%s")]').is_empty():
        return True
    return False

  def type(self, name, value, slowly=False):
    return self.find_by_name(name).first.type(value, slowly)

  def fill(self, name, value):
    element = self.find_by_name(name).first
    element.value = value

  def fill_form(self, field_values):
    [self.fill(name, value) for (name, value) in field_values.iteritems()]

  def choose(self, name, value):
    fields = self.find_by_name(name)
    for field in fields:
      if field.value == value:
        field.click()

  def check(self, name):
    self.find_by_name(name).first.check()

  def uncheck(self, name):
    self.find_by_name(name).first.uncheck()

  def select(self, name, value):
    self.find_by_xpath('//select[@name="%s"]' % name).first.value = value

  def click_link_by_href(self, href):
    return self.find_link_by_href(href).first.click()

  def click_link_by_partial_href(self, partial_href):
    return self.find_link_by_partial_href(partial_href).first.click()

  def click_link_by_text(self, text):
    return self.find_link_by_text(text).first.click()

  def click_link_by_partial_text(self, partial_text):
    return self.find_link_by_partial_text(partial_text).first.click()

  def within(self, context):
    return Within(self.find_by_css(context))

  def is_element_present(self, finder, selector, wait_time=None):
    wait_time = wait_time or self.wait_time
    end_time = time.time() + wait_time

    while time.time() < end_time:
      if finder(selector):
        return True
    return False

  def is_element_not_present(self, finder, selector, wait_time=None):
    wait_time = wait_time or self.wait_time
    end_time = time.time() + wait_time

    while time.time() < end_time:
      if not finder(selector):
        return True
    return False

  def is_element_present_by_css(self, css_selector, wait_time=None):
    return self.is_element_present(self.find_by_css, css_selector, wait_time)

  def is_element_not_present_by_css(self, css_selector, wait_time=None):
    return self.is_element_not_present(self.find_by_css, css_selector, wait_time)

  def is_element_present_by_xpath(self, xpath, wait_time=None):
    return self.is_element_present(self.find_by_xpath, xpath, wait_time)

  def is_element_not_present_by_xpath(self, xpath, wait_time=None):
    return self.is_element_not_present(self.find_by_xpath, xpath, wait_time)

  def is_element_present_by_tag(self, tag, wait_time=None):
    return self.is_element_present(self.find_by_tag, tag, wait_time)

  def is_element_not_present_by_tag(self, tag, wait_time=None):
    return self.is_element_not_present(self.find_by_tag, tag, wait_time)

  def is_element_present_by_name(self, name, wait_time=None):
    return self.is_element_present(self.find_by_name, name, wait_time)

  def is_element_not_present_by_name(self, name, wait_time=None):
    return self.is_element_not_present(self.find_by_name, name, wait_time)

  def is_element_present_by_value(self, value, wait_time=None):
    return self.is_element_present(self.find_by_value, value, wait_time)

  def is_element_not_present_by_value(self, value, wait_time=None):
    return self.is_element_not_present(self.find_by_value, value, wait_time)

  def is_element_present_by_id(self, id, wait_time=None):
    return self.is_element_present(self.find_by_id, id, wait_time)

  def is_element_not_present_by_id(self, id, wait_time=None):
    return self.is_element_not_present(self.find_by_id, id, wait_time)

  @property
  def cookies(self):
    return PhantomCookieManagerAPI(self)

  def command(self, name, *args):
    message = dict(name=name, args=args)

    response = json.loads(self.server.send(json.dumps(message)))
    if ('error' in response):
      raise Exception(response['error'])

    return response.get('response', '')

class PhantomCookieManagerAPI(CookieManagerAPI):
  __metaclass__ = InheritedDocs

  def __init__(self, driver):
    self.driver = driver

  def add(self, cookies):
    for name, value in cookies.iteritems():
      self.driver.command('set_cookie', dict(name=name, value=value))

  def delete(self, *cookies):
    [self.driver.command('remove_cookie', cookie) for cookie in cookies]

  def __getitem__(self, item):
    cookies = filter(lambda x: x['name'] == item, self.driver.command('cookies'))
    return cookies and cookies[0] or None

  def __eq__(self, other_object):
    cookies = self.driver.command('cookies')
    for cookie in cookies:
      if other_object[cookie['name']] != cookie:
        return False
    return True

class PhantomElementAPI(ElementAPI):
  __metaclass__ = InheritedDocs

  def __init__(self, driver, page_id, element_id):
    self.driver = driver
    self.page_id = page_id
    self.element_id = element_id

  def _get_value(self):
    value = self.driver.command('value', self.page_id, self.element_id)
    if not value.strip():
      value = self.text
    return value

  def _set_value(self, value):
    tag_name = self.driver.command('tag_name', self.page_id, self.element_id)
    if tag_name == 'SELECT':
      self.driver.command('select', self.page_id, self.element_id, value)
    else:
      self.driver.command('set', self.page_id, self.element_id, value)

  #: Value of the element, usually a form element
  value = property(_get_value, _set_value)

  @property
  def text(self):
    return self.driver.command('text', self.page_id, self.element_id)

  def click(self):
    self.driver.command('click', self.page_id, self.element_id)

  def check(self):
    if not self.checked:
      self.click()

  def uncheck(self):
    if self.checked:
      self.click()

  @property
  def checked(self):
    return self['checked']

  @property
  def selected(self):
    return self['selected']

  @property
  def visible(self):
    return self.driver.command('visible', self.page_id, self.element_id) == 'true'

  @property
  def html(self):
    return self.driver.command('inner_html', self.page_id, self.element_id)

  @property
  def outer_html(self):
    return self.driver.command('outer_html', self.page_id, self.element_id)

  def find_by_css(self, selector, original_find=None, original_query=None):
    from cssselect import GenericTranslator, SelectorError
    try:
      expression = GenericTranslator().css_to_xpath(selector)
    except SelectorError:
      raise
    return self.find_by_xpath(expression)

  def find_by_xpath(self, selector):
    response = self.driver.command('find_within', self.page_id, self.element_id, selector)
    return ElementList([PhantomElementAPI(self.driver, self.page_id, element_id) for element_id in response], driver=self)

  def find_by_name(self, name):
    return self.find_by_xpath('descendant::*[@name="%s"]' % name)

  def find_by_id(self, id):
    return self.find_by_xpath('descendant::*[@id="%s"]' % id)

  def find_by_value(self, value):
    return self.find_by_xpath('descendant::*[@value="%s"]' % value)

  def find_by_tag(self, tag):
    return self.find_by_xpath('descendant::%s' % tag)

  def has_class(self, class_name):
    return bool(re.search(r'(?:^|\s)' + re.escape(class_name) + r'(?:$|\s)', self['class']))

  def mouse_over(self):
    self.driver.command('trigger', self.page_id, self.element_id, 'mouseover')

  def mouse_out(self):
    self.driver.command('trigger', self.page_id, self.element_id, 'mouseout')

  def fill(self, value):
    self.driver.command('set', self.page_id, self.element_id, value)

  def _type_slowly(self, value, previously_typed):
    for (idx, key) in enumerate(value):
      previously_typed += key
      self.driver.command('set', self.page_id, self.element_id, previously_typed)
      yield previously_typed

  def type(self, value, slowly=False):
    print '>>> node type, page_id = ', self.page_id
    previously_typed = self.value
    if (slowly):
      return self._type_slowly(value, previously_typed)
    return self.driver.command('set', self.page_id, self.element_id, previously_typed + value)

  def __getitem__(self, attribute):
    return self.driver.command('attribute', self.page_id, self.element_id, attribute)

  @property
  def parent(self):
    return self.driver

