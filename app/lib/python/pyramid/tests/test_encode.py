import unittest

class UrlEncodeTests(unittest.TestCase):
    def _callFUT(self, query, doseq=False):
        from pyramid.encode import urlencode
        return urlencode(query, doseq)

    def test_ascii_only(self):
        result = self._callFUT([('a',1), ('b',2)])
        self.assertEqual(result, 'a=1&b=2')

    def test_unicode_key(self):
        la = unicode('LaPe\xc3\xb1a', 'utf-8')
        result = self._callFUT([(la, 1), ('b',2)])
        self.assertEqual(result, 'LaPe%C3%B1a=1&b=2')

    def test_unicode_val_single(self):
        la = unicode('LaPe\xc3\xb1a', 'utf-8')
        result = self._callFUT([('a', la), ('b',2)])
        self.assertEqual(result, 'a=LaPe%C3%B1a&b=2')

    def test_unicode_val_multiple(self):
        la = [unicode('LaPe\xc3\xb1a', 'utf-8')] * 2
        result = self._callFUT([('a', la), ('b',2)], doseq=True)
        self.assertEqual(result, 'a=LaPe%C3%B1a&a=LaPe%C3%B1a&b=2')

    def test_dict(self):
        result = self._callFUT({'a':1})
        self.assertEqual(result, 'a=1')

class URLQuoteTests(unittest.TestCase):
    def _callFUT(self, val, safe=''):
        from pyramid.encode import url_quote
        return url_quote(val, safe)

    def test_it_default(self):
        la = 'La/Pe\xc3\xb1a'
        result = self._callFUT(la)
        self.assertEqual(result, 'La%2FPe%C3%B1a')
        
    def test_it_with_safe(self):
        la = 'La/Pe\xc3\xb1a'
        result = self._callFUT(la, '/')
        self.assertEqual(result, 'La/Pe%C3%B1a')

class TestQuotePlus(unittest.TestCase):
    def _callFUT(self, val, safe=''):
        from pyramid.encode import quote_plus
        return quote_plus(val, safe)
    
    def test_it_default(self):
        la = 'La Pe\xc3\xb1a'
        result = self._callFUT(la)
        self.assertEqual(result, 'La+Pe%C3%B1a')
        
    def test_it_with_safe(self):
        la = 'La /Pe\xc3\xb1a'
        result = self._callFUT(la, '/')
        self.assertEqual(result, 'La+/Pe%C3%B1a')

        
