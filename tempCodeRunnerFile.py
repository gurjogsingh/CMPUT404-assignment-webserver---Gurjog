def test_deep_no_end(self):
        url = self.baseurl + "/deep"
        expected_url = self.baseurl + "/deep/"
        try:
            req = request.urlopen(url, None, 3)
            code = req.getcode() 
            if code >= 200 and code <= 299 and req.geturl() == expected_url:
                self.assertTrue(True, "The library has redirected for us")
            else:
                self.assertTrue(False, "The URL hasn't changed %s %s" % (code,req.geturl()))
        except request.HTTPError as e:
            code = e.getcode() 
            self.assertTrue( code >= 300 and code < 400, "300ish Not FOUND! %s" % code)
