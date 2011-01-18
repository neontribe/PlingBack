import unittest

class TestGetRoot(unittest.TestCase):
    def _callFUT(self, app, request=None):
        from pyramid.paster import get_root
        return get_root(app, request)

    def test_it_norequest(self):
        app = DummyApp()
        root, closer = self._callFUT(app)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'].registry, app.registry)
        self.assertEqual(len(app.threadlocal_manager.popped), 0)
        closer()
        self.assertEqual(len(app.threadlocal_manager.popped), 1)

    def test_it_withrequest(self):
        app = DummyApp()
        request = DummyRequest({})
        root, closer = self._callFUT(app, request)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['registry'], dummy_registry)
        self.assertEqual(pushed['request'], request)
        self.assertEqual(len(app.threadlocal_manager.popped), 0)
        closer()
        self.assertEqual(len(app.threadlocal_manager.popped), 1)

    def test_it_requestfactory_overridden(self):
        app = DummyApp()
        request = Dummy()
        class DummyFactory(object):
            @classmethod
            def blank(cls, path):
                return request
        registry = DummyRegistry(DummyFactory)
        app.registry = registry
        root, closer = self._callFUT(app)
        self.assertEqual(len(app.threadlocal_manager.pushed), 1)
        pushed = app.threadlocal_manager.pushed[0]
        self.assertEqual(pushed['request'], request)

class Dummy:
    pass

dummy_root = Dummy()

class DummyRegistry(object):
    def __init__(self, result=None):
        self.result = result

    def queryUtility(self, iface, default=None):
        return self.result or default

dummy_registry = DummyRegistry()

class DummyApp:
    def __init__(self):
        self.registry = dummy_registry
        self.threadlocal_manager = DummyThreadLocalManager()

    def root_factory(self, environ):
        return dummy_root

class DummyThreadLocalManager:
    def __init__(self):
        self.pushed = []
        self.popped = []
        
    def push(self, item):
        self.pushed.append(item)

    def pop(self):
        self.popped.append(True)
        
class DummyRequest:
    def __init__(self, environ):
        self.environ = environ
        
