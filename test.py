from splinter.driver.phantomjsdriver import PhantomJSDriver

d = PhantomJSDriver()
try:
  d.visit('http://www.google.com')
  print d.url
except Exception as e:
  print e

