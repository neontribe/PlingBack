import logging

logging.basicConfig()

import unittest

from pyramid import testing

from zope.interface import Interface
from zope.interface import implements

class TestViewDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import view
        return view(*arg, **kw)

    def test_with_dotted_renderer(self):
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRendererFactory
        from pyramid.interfaces import IRequest
        reg = self.config.registry
        context = self.config._ctx
        def factory(path):
            def foo(*arg):
                return 'OK'
            return foo
        reg.registerUtility(factory, IRendererFactory, name='.pt')
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IDummy, view=view,
                      renderer='foo/template.pt')
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        discrim = ('view', IDummy, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        regview = reg.adapters.lookup(
            (IViewClassifier, IRequest, IDummy), IView, name='')
        self.assertEqual(regview(None, None).body, 'OK')

    def test_with_custom_predicates(self):
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRequest
        reg = self.config.registry
        context = self.config._ctx
        view = lambda *arg: 'OK'
        def pred1(context, request):
            return True
        def pred2(context, request):
            return True
        preds = (pred1, pred2)
        self._callFUT(context, 'repoze.view', IDummy, view=view,
                      custom_predicates=preds)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        discrim = ('view', IDummy, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        discrim = discrim + tuple(sorted(preds))
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        regview = reg.adapters.lookup(
            (IViewClassifier, IRequest, IDummy), IView, name='')
        self.assertEqual(regview(None, None), 'OK')

    def test_context_trumps_for(self):
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRequest
        reg = self.config.registry
        context = self.config._ctx
        view = lambda *arg: 'OK'
        class Foo:
            pass
        self._callFUT(context, 'repoze.view', for_=Foo, view=view,
                      context=IDummy)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        discrim = ('view', IDummy, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        regview = reg.adapters.lookup(
            (IViewClassifier, IRequest, IDummy), IView, name='')
        self.assertEqual(regview(None, None), 'OK')

    def test_with_for(self):
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRequest
        reg = self.config.registry
        context = self.config._ctx
        view = lambda *arg: 'OK'
        class Foo:
            pass
        self._callFUT(context, 'repoze.view', for_=IDummy, view=view)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        discrim = ('view', IDummy, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        regview = reg.adapters.lookup(
            (IViewClassifier, IRequest, IDummy), IView, name='')
        self.assertEqual(regview(None, None), 'OK')

class TestNotFoundDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, view, **kw):
        from pyramid.zcml import notfound
        return notfound(context, view, **kw)
    
    def test_it(self):
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.exceptions import NotFound

        reg = self.config.registry
        context = self.config._ctx
        def view(request):
            return 'OK'
        self._callFUT(context, view)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)

        discrim = ('view', NotFound, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], discrim)
        register = regadapt['callable']
        register()
        derived_view = reg.adapters.lookup(
            (IViewClassifier, IRequest, implementedBy(NotFound)),
            IView, default=None)

        self.assertNotEqual(derived_view, None)
        self.assertEqual(derived_view(None, None), 'OK')
        self.assertEqual(derived_view.__name__, 'bwcompat_view')

    def test_it_with_dotted_renderer(self):
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.exceptions import NotFound
        from pyramid.config import Configurator
        reg = self.config.registry
        config = Configurator(reg)
        def dummy_renderer_factory(*arg, **kw):
            return lambda *arg, **kw: 'OK'
        config.add_renderer('.pt', dummy_renderer_factory)
        config.commit()
        def view(request):
            return {}
        context = self.config._ctx
        self._callFUT(context, view, renderer='fake.pt')
        actions = extract_actions(context.actions)
        regadapt = actions[0]
        register = regadapt['callable']
        register()
        derived_view = reg.adapters.lookup(
            (IViewClassifier, IRequest, implementedBy(NotFound)),
            IView, default=None)
        self.assertNotEqual(derived_view, None)
        self.assertEqual(derived_view(None, None).body, 'OK')
        self.assertEqual(derived_view.__name__, 'bwcompat_view')

class TestForbiddenDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, view, **kw):
        from pyramid.zcml import forbidden
        return forbidden(context, view, **kw)
    
    def test_it(self):
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.exceptions import Forbidden
        reg = self.config.registry
        context = self.config._ctx
        def view(request):
            return 'OK'
        self._callFUT(context, view)
        actions = extract_actions(context.actions)

        self.assertEqual(len(actions), 1)

        discrim = ('view', Forbidden, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], discrim)
        register = regadapt['callable']
        register()
        derived_view = reg.adapters.lookup(
            (IViewClassifier, IRequest, implementedBy(Forbidden)),
            IView, default=None)

        self.assertNotEqual(derived_view, None)
        self.assertEqual(derived_view(None, None), 'OK')
        self.assertEqual(derived_view.__name__, 'bwcompat_view')

    def test_it_with_dotted_renderer(self):
        from zope.interface import implementedBy
        from pyramid.interfaces import IRequest
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.exceptions import Forbidden
        from pyramid.config import Configurator
        reg = self.config.registry
        config = Configurator(reg)
        def dummy_renderer_factory(*arg, **kw):
            return lambda *arg, **kw: 'OK'
        config.add_renderer('.pt', dummy_renderer_factory)
        config.commit()
        def view(request):
            return {}
        context = self.config._ctx
        self._callFUT(context, view, renderer='fake.pt')
        actions = extract_actions(context.actions)
        regadapt = actions[0]
        register = regadapt['callable']
        register()
        derived_view = reg.adapters.lookup(
            (IViewClassifier, IRequest, implementedBy(Forbidden)),
            IView, default=None)
        self.assertNotEqual(derived_view, None)
        self.assertEqual(derived_view(None, None).body, 'OK')
        self.assertEqual(derived_view.__name__, 'bwcompat_view')

class TestRepozeWho1AuthenticationPolicyDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, **kw):
        from pyramid.zcml import repozewho1authenticationpolicy
        return repozewho1authenticationpolicy(context, **kw)

    def test_it_defaults(self):
        reg = self.config.registry
        from pyramid.interfaces import IAuthenticationPolicy
        context = self.config._ctx
        self._callFUT(context)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.callback, None)
        self.assertEqual(policy.identifier_name, 'auth_tkt')
    
    def test_it(self):
        reg = self.config.registry
        from pyramid.interfaces import IAuthenticationPolicy
        context = self.config._ctx
        def callback(identity, request):
            """ """
        self._callFUT(context, identifier_name='something', callback=callback)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.callback, callback)
        self.assertEqual(policy.identifier_name, 'something')

class TestRemoteUserAuthenticationPolicyDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, **kw):
        from pyramid.zcml import remoteuserauthenticationpolicy
        return remoteuserauthenticationpolicy(context, **kw)

    def test_defaults(self):
        from pyramid.interfaces import IAuthenticationPolicy
        reg = self.config.registry
        context = self.config._ctx
        def callback(identity, request):
            """ """
        self._callFUT(context)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.environ_key, 'REMOTE_USER')
        self.assertEqual(policy.callback, None)

    def test_it(self):
        from pyramid.interfaces import IAuthenticationPolicy
        reg = self.config.registry
        context = self.config._ctx
        def callback(identity, request):
            """ """
        self._callFUT(context, environ_key='BLAH', callback=callback)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.environ_key, 'BLAH')
        self.assertEqual(policy.callback, callback)

class TestAuthTktAuthenticationPolicyDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, secret, **kw):
        from pyramid.zcml import authtktauthenticationpolicy
        return authtktauthenticationpolicy(context, secret, **kw)

    def test_it_defaults(self):
        from pyramid.interfaces import IAuthenticationPolicy
        reg = self.config.registry
        context = self.config._ctx
        self._callFUT(context, 'sosecret')
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.cookie.secret, 'sosecret')
        self.assertEqual(policy.callback, None)

    def test_it_noconfigerror(self):
        from pyramid.interfaces import IAuthenticationPolicy
        reg = self.config.registry
        context = self.config._ctx
        def callback(identity, request):
            """ """
        self._callFUT(context, 'sosecret', callback=callback,
                      cookie_name='auth_tkt',
                      secure=True, include_ip=True, timeout=100,
                      reissue_time=60, http_only=True, path="/sub/")
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.cookie.path, '/sub/')
        self.assertEqual(policy.cookie.http_only, True)
        self.assertEqual(policy.cookie.secret, 'sosecret')
        self.assertEqual(policy.callback, callback)

    def test_it_configerror(self):
        from pyramid.exceptions import ConfigurationError
        context = self.config._ctx
        def callback(identity, request):
            """ """
        self.assertRaises(ConfigurationError,
                          self._callFUT,
                          context, 'sosecret', callback=callback,
                          cookie_name='auth_tkt',
                          secure=True, include_ip=True, timeout=100,
                          reissue_time=500, http_only=True,
                          path="/cgi-bin/app.cgi/")

class TestACLAuthorizationPolicyDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, **kw):
        from pyramid.zcml import aclauthorizationpolicy
        return aclauthorizationpolicy(context, **kw)
    
    def test_it(self):
        from pyramid.authorization import ACLAuthorizationPolicy
        from pyramid.interfaces import IAuthorizationPolicy
        reg = self.config.registry
        context = self.config._ctx
        def callback(identity, request):
            """ """
        self._callFUT(context)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthorizationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthorizationPolicy)
        self.assertEqual(policy.__class__, ACLAuthorizationPolicy)

class TestRouteDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import route
        return route(*arg, **kw)

    def _assertRoute(self, name, pattern, num_predicates=0):
        from pyramid.interfaces import IRoutesMapper
        reg = self.config.registry
        mapper = reg.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.pattern, pattern)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def test_with_view(self):
        from zope.interface import Interface
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRouteRequest
        reg = self.config.registry
        context = self.config._ctx
        view = lambda *arg: 'OK'
        self._callFUT(context, 'name', 'pattern', view=view)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', None, IView, None, None, None, 'name',
                   None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        view_action['callable'](*view_action['args'], **view_action['kw'])

        route_action = actions[1]
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self._assertRoute('name', 'pattern')

        wrapped = reg.adapters.lookup(
            (IViewClassifier, request_type, Interface), IView, name='')
        self.failUnless(wrapped)

    def test_with_view_and_view_context(self):
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRouteRequest
        reg = self.config.registry
        context = self.config._ctx
        view = lambda *arg: 'OK'
        self._callFUT(context, 'name', 'pattern', view=view,
                      view_context=IDummy)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', IDummy, '', None, IView, None, None, None, 'name',
                   None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        view_action['callable'](*view_action['args'], **view_action['kw'])

        route_action = actions[1]
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))

        self._assertRoute('name', 'pattern')
        wrapped = reg.adapters.lookup(
            (IViewClassifier, request_type, IDummy), IView, name='')
        self.failUnless(wrapped)

    def test_with_view_context_trumps_view_for(self):
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRouteRequest
        reg = self.config.registry
        context = self.config._ctx
        view = lambda *arg: 'OK'
        class Foo:
            pass
        self._callFUT(context, 'name', 'pattern', view=view,
                      view_context=IDummy, view_for=Foo)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', IDummy, '', None, IView, None, None, None, 'name',
                   None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        view_action['callable'](*view_action['args'], **view_action['kw'])

        route_action = actions[1]
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))

        self._assertRoute('name', 'pattern')
        wrapped = reg.adapters.lookup(
            (IViewClassifier, request_type, IDummy), IView, name='')
        self.failUnless(wrapped)

    def test_with_dotted_renderer(self):
        from zope.interface import Interface
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IRendererFactory
        reg = self.config.registry
        def renderer(path):
            return lambda *arg: 'OK'
        reg.registerUtility(renderer, IRendererFactory, name='.pt')
        context = self.config._ctx

        view = lambda *arg: 'OK'
        self._callFUT(context, 'name', 'pattern', view=view,
                      renderer='fixtureapp/templates/foo.pt')
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', None, IView, None, None, None, 'name',
                   None, False, None, None, None) 
        self.assertEqual(view_discriminator, discrim)
        view_action['callable'](*view_action['args'], **view_action['kw'])

        route_action = actions[1]
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self._assertRoute('name', 'pattern')

        wrapped = reg.adapters.lookup(
            (IViewClassifier, request_type, Interface), IView, name='')
        self.failUnless(wrapped)
        request = DummyRequest()
        result = wrapped(None, request)
        self.assertEqual(result.body, 'OK')

    def test_with_custom_predicates(self):
        def pred1(context, request): pass
        def pred2(context, request): pass
        preds = tuple(sorted([pred1, pred2]))

        context = self.config._ctx

        self._callFUT(context, 'name', 'pattern',
                      custom_predicates=(pred1, pred2))
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)

        route_action = actions[0]
        route_discriminator = route_action['discriminator']
        self.assertEqual(
            route_discriminator,
            ('route', 'name', False, None, None, None, None,None) + preds)
        self._assertRoute('name', 'pattern', 2)

    def test_with_path_argument_no_pattern(self):
        context = self.config._ctx
        self._callFUT(context, 'name', path='pattern')
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)

        route_action = actions[0]
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self._assertRoute('name', 'pattern')

    def test_with_path_argument_and_pattern(self):
        context = self.config._ctx
        self._callFUT(context, 'name', pattern='pattern', path='path')
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)

        route_action = actions[0]
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self._assertRoute('name', 'pattern')
        

    def test_with_neither_path_nor_pattern(self):
        from pyramid.exceptions import ConfigurationError
        context = self.config._ctx
        self.assertRaises(ConfigurationError, self._callFUT, context, 'name')

class TestHandlerDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import handler
        return handler(*arg, **kw)

    def _assertRoute(self, name, pattern, num_predicates=0):
        from pyramid.interfaces import IRoutesMapper
        reg = self.config.registry
        mapper = reg.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.pattern, pattern)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def test_it(self):
        from pyramid.view import action
        from zope.interface import Interface
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRouteRequest
        reg = self.config.registry
        context = self.config._ctx
        class Handler(object): # pragma: no cover
            def __init__(self, request):
                self.request = request
            action(renderer='json')
            def one(self):
                return 'OK'
            action(renderer='json')
            def two(self):
                return 'OK'
        self._callFUT(context, 'name', '/:action', Handler)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 3)

        route_action = actions[0]
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self._assertRoute('name', '/:action')

        view_action = actions[1]
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', None, IView, None, None, None, 'name',
                   'one', False, None, None, None)
        self.assertEqual(view_discriminator[:14], discrim)
        view_action['callable'](*view_action['args'], **view_action['kw'])

        view_action = actions[2]
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', None, IView, None, None, None, 'name',
                   'two', False, None, None, None)
        self.assertEqual(view_discriminator[:14], discrim)
        view_action['callable'](*view_action['args'], **view_action['kw'])

        wrapped = reg.adapters.lookup(
            (IViewClassifier, request_type, Interface), IView, name='')
        self.failUnless(wrapped)

    def test_pattern_is_None(self):
        from pyramid.exceptions import ConfigurationError

        context = self.config._ctx
        class Handler(object):
            pass
        self.assertRaises(ConfigurationError, self._callFUT,
                          context, 'name', None, Handler)

class TestStaticDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import static
        return static(*arg, **kw)

    def test_it_with_slash(self):
        from pyramid import testing
        testing.registerDummySecurityPolicy(permissive=False)
        from pyramid.static import PackageURLParser
        from zope.interface import implementedBy
        from pyramid.static import StaticURLInfo
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IRoutesMapper
        reg = self.config.registry
        context = self.config._ctx

        self._callFUT(context, 'name', 'fixtures/static')
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        discriminator = view_action['discriminator']
        self.assertEqual(discriminator[:3], ('view', StaticURLInfo, ''))
        self.assertEqual(discriminator[4], IView)
        view_action['callable'](*view_action['args'], **view_action['kw'])

        route_action = actions[1]
        discriminator = route_action['discriminator']
        self.assertEqual(
            discriminator,
            ('route', 'name/', False, None, None, None, None, None)
            )

        mapper = reg.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].pattern, 'name/*subpath')
        self.assertEqual(routes[0].name, 'name/')

        iface = implementedBy(StaticURLInfo)
        request_type = reg.getUtility(IRouteRequest, 'name/')
        view = reg.adapters.lookup(
            (IViewClassifier, request_type, iface), IView, name='')
        request = DummyRequest()
        self.assertEqual(view(None, request).__class__, PackageURLParser)

    def test_it_with_nondefault_permission(self):
        from pyramid import testing
        from pyramid.exceptions import Forbidden
        testing.registerDummySecurityPolicy(permissive=False)
        from zope.interface import implementedBy
        from pyramid.static import StaticURLInfo
        from pyramid.interfaces import IView
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IRoutesMapper
        reg = self.config.registry
        context = self.config._ctx
        self._callFUT(context, 'name', 'fixtures/static', permission='aperm')
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 2)

        view_action = actions[0]
        discriminator = view_action['discriminator']
        self.assertEqual(discriminator[:3], ('view', StaticURLInfo, ''))
        self.assertEqual(discriminator[4], IView)
        view_action['callable'](*view_action['args'], **view_action['kw'])

        route_action = actions[1]
        discriminator = route_action['discriminator']
        self.assertEqual(
            discriminator,
            ('route', 'name/', False, None, None, None, None, None))
        mapper = reg.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].pattern, 'name/*subpath')
        self.assertEqual(routes[0].name, 'name/')


        iface = implementedBy(StaticURLInfo)
        request_type = reg.getUtility(IRouteRequest, 'name/')
        view = reg.adapters.lookup(
            (IViewClassifier, request_type, iface), IView, name='')
        request = DummyRequest()
        self.assertRaises(Forbidden, view, None, request)

class TestAssetDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import asset
        return asset(*arg, **kw)

    def test_it(self):
        import pyramid.tests
        context = self.config._ctx
        L = []
        def dummy_override(*arg):
            L.append(arg)
        self._callFUT(context, 'pyramid.tests:fixtures/',
                      'pyramid.tests:fixtureapp/', _override=dummy_override)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['discriminator'], None)
        action['callable']()
        self.assertEqual(
            L,
            [(pyramid.tests, 'fixtures/', pyramid.tests, 'fixtureapp/')])


class TestRendererDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import renderer
        return renderer(*arg, **kw)

    def test_it(self):
        from pyramid.interfaces import IRendererFactory
        reg = self.config.registry
        context = self.config._ctx
        renderer = lambda *arg, **kw: None
        self._callFUT(context, renderer, 'r')
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['discriminator'], (IRendererFactory, 'r'))
        self.failUnless(reg.getUtility(IRendererFactory, 'r'), renderer)
    
class TestZCMLConfigure(unittest.TestCase):
    i = 0
    def _callFUT(self, path, package):
        from pyramid.zcml import zcml_configure
        return zcml_configure(path, package)
    
    def setUp(self):
        from zope.deprecation import __show__
        __show__.off()
        testing.setUp(autocommit=False)
        self.tempdir = None
        import sys
        import os
        import tempfile
        from pyramid.path import package_path
        from pyramid.tests import fixtureapp as package
        import shutil
        tempdir = tempfile.mkdtemp()
        modname = 'myfixture%s' % self.i
        self.i += 1
        self.packagepath = os.path.join(tempdir, modname)
        fixturedir = package_path(package)
        shutil.copytree(fixturedir, self.packagepath)
        sys.path.insert(0, tempdir)
        self.module = __import__(modname)
        self.tempdir = tempdir

    def tearDown(self):
        from zope.deprecation import __show__
        __show__.on()
        testing.tearDown()
        import sys
        import shutil
        if self.module is not None:
            del sys.modules[self.module.__name__]
        if self.tempdir is not None:
            sys.path.pop(0)
            shutil.rmtree(self.tempdir)

    def test_zcml_configure(self):
        actions = self._callFUT('configure.zcml', self.module)
        self.failUnless(actions)
        self.failUnless(isinstance(actions, list))

    def test_zcml_configure_nonexistent_configure_dot_zcml(self):
        import os
        os.remove(os.path.join(self.packagepath, 'configure.zcml'))
        self.assertRaises(IOError, self._callFUT, 'configure.zcml',
                          self.module)

class TestZCMLScanDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, package):
        from pyramid.zcml import scan
        return scan(context, package)

    def test_it(self):
        dummy_module = DummyModule()
        def foo(): pass
        def bar(scanner, name, ob):
            dummy_module.scanned = True
        foo.__venusian_callbacks__ = {'pyramid':[bar]}
        dummy_module.foo = foo
        
        context = self.config._ctx
        self._callFUT(context, dummy_module)
        self.assertEqual(dummy_module.scanned, True)

class TestAdapterDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import adapter
        return adapter(*arg, **kw)

    def test_for_is_None_no_adaptedBy(self):
        context = DummyContext()
        factory = DummyFactory()
        self.assertRaises(TypeError, self._callFUT, context, [factory],
                          provides=None, for_=None)

    def test_for_is_None_adaptedBy_still_None(self):
        context = DummyContext()
        factory = DummyFactory()
        factory.__component_adapts__ = None
        self.assertRaises(TypeError, self._callFUT, context, [factory],
                      provides=None, for_=None)

    def test_for_is_None_adaptedBy_set(self):
        from pyramid.registry import Registry
        context = DummyContext()
        context.registry = self.config.registry
        factory = DummyFactory()
        factory.__component_adapts__ = (IDummy,)
        self._callFUT(context, [factory], provides=IFactory, for_=None)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'],
                         ('adapter', (IDummy,), IFactory, ''))
        self.assertEqual(regadapt['callable'].im_func,
                         Registry.registerAdapter.im_func)
        self.assertEqual(regadapt['args'],
                         (factory, (IDummy,), IFactory, '', None))

    def test_provides_missing(self):
        context = DummyContext()
        factory = DummyFactory()
        self.assertRaises(TypeError, self._callFUT, context, [factory],
                          provides=None, for_=(IDummy,))

    def test_provides_obtained_via_implementedBy(self):
        from pyramid.registry import Registry
        context = DummyContext()
        context.registry = self.config.registry
        self._callFUT(context, [DummyFactory], for_=(IDummy,))
        regadapt = extract_actions(context.actions)[0]
        self.assertEqual(regadapt['discriminator'],
                         ('adapter', (IDummy,), IFactory, ''))
        self.assertEqual(regadapt['callable'].im_func,
                         Registry.registerAdapter.im_func)
        self.assertEqual(regadapt['args'],
                         (DummyFactory, (IDummy,), IFactory, '', None))

    def test_multiple_factories_multiple_for(self):
        context = DummyContext()
        factory = DummyFactory()
        self.assertRaises(ValueError, self._callFUT, context,
                          [factory, factory],
                          provides=IFactory,
                          for_=(IDummy, IDummy))

    def test_no_factories_multiple_for(self):
        context = DummyContext()
        self.assertRaises(ValueError, self._callFUT, context,
                          factory=[],
                          provides=IFactory,
                          for_=(IDummy, IDummy))
        
    def test_rolled_up_factories(self):
        from pyramid.registry import Registry
        context = DummyContext()
        context.registry = self.config.registry
        factory = DummyFactory()
        self._callFUT(context,
                      [factory, factory],
                      provides=IFactory,
                      for_=(IDummy,))
        regadapt = extract_actions(context.actions)[0]
        self.assertEqual(regadapt['discriminator'],
                         ('adapter', (IDummy,), IFactory, ''))
        self.assertEqual(regadapt['callable'].im_func,
                         Registry.registerAdapter.im_func)
        self.assertEqual(regadapt['args'][0].__module__, 'pyramid.zcml')

class TestSubscriberDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import subscriber
        return subscriber(*arg, **kw)

    def test_no_factory_no_handler(self):
        context = self.config._ctx
        self.assertRaises(TypeError,
                          self._callFUT, context, for_=None, factory=None,
                          handler=None,
                          provides=None)

    def test_handler_with_provides(self):
        context = self.config._ctx
        self.assertRaises(TypeError,
                          self._callFUT, context, for_=None, factory=None,
                          handler=1, provides=1)

    def test_handler_and_factory(self):
        context = self.config._ctx
        self.assertRaises(TypeError,
                          self._callFUT, context, for_=None, factory=1,
                          handler=1, provides=None)

    def test_no_provides_with_factory(self):
        context = self.config._ctx
        self.assertRaises(TypeError,
                          self._callFUT, context, for_=None, factory=1,
                          handler=None, provides=None)

    def test_adapted_by_as_for_is_None(self):
        context = self.config._ctx
        factory = DummyFactory()
        factory.__component_adapts__ = None
        self.assertRaises(TypeError, self._callFUT, context, for_=None,
                          factory=factory, handler=None, provides=IFactory)
        
    def test_register_with_factory(self):
        context = self.config._ctx
        factory = DummyFactory()
        self._callFUT(context, for_=(IDummy,),
                      factory=factory, handler=None, provides=IFactory)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        subadapt = actions[0]
        self.assertEqual(subadapt['discriminator'], None)
        subadapt['callable'](*subadapt['args'], **subadapt['kw'])
        registrations = self.config.registry._subscription_registrations
        self.assertEqual(len(registrations), 1)
        reg = registrations[0]
        self.assertEqual(
            reg[:4],
            ((IDummy,), IFactory, None, factory)
            )

    def test_register_with_handler(self):
        context = self.config._ctx
        factory = DummyFactory()
        self._callFUT(context, for_=(IDummy,),
                      factory=None, handler=factory)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        subadapt = actions[0]
        self.assertEqual(subadapt['discriminator'], None)
        subadapt['callable'](*subadapt['args'], **subadapt['kw'])
        registrations = self.config.registry._handler_registrations
        self.assertEqual(len(registrations), 1)
        self.assertEqual(
            registrations[0][:3],
            ((IDummy,), u'', factory)
            )

class TestUtilityDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import utility
        return utility(*arg, **kw)

    def test_factory_and_component(self):
        context = self.config._ctx
        self.assertRaises(TypeError, self._callFUT,
                          context, factory=1, component=1)

    def test_missing_provides(self):
        context = self.config._ctx
        self.assertRaises(TypeError, self._callFUT, context, provides=None)
        
    def test_provides_from_factory_implements(self):
        from pyramid.registry import Registry
        context = self.config._ctx
        self._callFUT(context, factory=DummyFactory)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        utility = actions[0]
        self.assertEqual(utility['discriminator'], ('utility', IFactory, ''))
        self.assertEqual(utility['callable'].im_func,
                         Registry.registerUtility.im_func)
        self.assertEqual(utility['args'][:3], (None, IFactory, ''))
        self.assertEqual(utility['kw'], {'factory':DummyFactory})

    def test_provides_from_component_provides(self):
        from pyramid.registry import Registry
        context = self.config._ctx
        component = DummyFactory()
        self._callFUT(context, component=component)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        utility = actions[0]
        self.assertEqual(utility['discriminator'], ('utility', IFactory, ''))
        self.assertEqual(utility['callable'].im_func,
                         Registry.registerUtility.im_func)
        self.assertEqual(utility['args'][:3], (component, IFactory, ''))
        self.assertEqual(utility['kw'], {})

class TestTranslationDirDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import translationdir
        return translationdir(*arg, **kw)

    def test_it(self):
        import os
        here = os.path.dirname(__file__)
        expected = os.path.join(here, 'localeapp', 'locale')
        from pyramid.interfaces import ITranslationDirectories
        context = self.config._ctx
        tdir = 'pyramid.tests.localeapp:locale'
        self._callFUT(context, tdir)
        util = self.config.registry.getUtility(ITranslationDirectories)
        self.assertEqual(util, [expected])

class TestLocaleNegotiatorDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from pyramid.zcml import localenegotiator
        return localenegotiator(*arg, **kw)

    def test_it(self):
        from pyramid.interfaces import ILocaleNegotiator
        context = self.config._ctx
        dummy_negotiator = object()
        self._callFUT(context, dummy_negotiator)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['discriminator'], ILocaleNegotiator)
        callback = action['callable']
        callback()
        self.assertEqual(self.config.registry.getUtility(ILocaleNegotiator),
                         dummy_negotiator)

class TestDefaultPermissionDirective(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, name):
        from pyramid.zcml import default_permission
        return default_permission(context, name)
    
    def test_it(self):
        from pyramid.interfaces import IDefaultPermission
        reg = self.config.registry
        context = self.config._ctx
        self._callFUT(context, 'view')
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IDefaultPermission)
        perm = reg.getUtility(IDefaultPermission)
        self.assertEqual(perm, 'view')

class TestLoadZCML(unittest.TestCase):
    def setUp(self):
        testing.setUp(autocommit=False)

    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        from zope.configuration import xmlconfig
        import pyramid.includes
        xmlconfig.file('configure.zcml', package=pyramid.includes)

class TestRolledUpFactory(unittest.TestCase):
    def _callFUT(self, *factories):
        from pyramid.zcml import _rolledUpFactory
        return _rolledUpFactory(factories)

    def test_it(self):
        def foo(ob):
            return ob
        factory = self._callFUT(foo, foo)
        result = factory(True)
        self.assertEqual(result, True)

class Test_path_spec(unittest.TestCase):
    def _callFUT(self, context, path):
        from pyramid.zcml import path_spec
        return path_spec(context, path)

    def test_no_package_attr(self):
        context = DummyContext()
        path = '/thepath'
        result = self._callFUT(context, path)
        self.assertEqual(result, path)

    def test_package_attr_None(self):
        context = DummyContext()
        context.package = None
        path = '/thepath'
        result = self._callFUT(context, path)
        self.assertEqual(result, path)

    def test_package_path_doesnt_start_with_abspath(self):
        context = DummyContext()
        context.package = DummyPackage('pyramid.tests')
        path = '/thepath'
        result = self._callFUT(context, path)
        self.assertEqual(result, path)

    def test_package_path_starts_with_abspath(self):
        import pkg_resources
        import os
        context = DummyContext()
        package = DummyPackage('pyramid.tests')
        package_path = pkg_resources.resource_filename('pyramid.tests', '')
        template_path = os.path.join(package_path, 'templates/foo.pt')
        context.package = package
        result = self._callFUT(context, template_path)
        self.assertEqual(result, 'pyramid.tests:templates/foo.pt')

    def test_package_name_is___main__(self):
        context = DummyContext()
        package = DummyPackage('__main__')
        context.package = package
        result = self._callFUT(context, '/foo.pt')
        self.assertEqual(result, '/foo.pt')

    def test_path_is_already_asset_spec(self):
        context = DummyContext()
        result = self._callFUT(context, 'pyramid.tests:foo.pt')
        self.assertEqual(result, 'pyramid.tests:foo.pt')

class IDummy(Interface):
    pass

class IFactory(Interface):
    pass

class DummyFactory(object):
    implements(IFactory)
    def __call__(self):
        """ """
        
class DummyModule:
    __path__ = "foo"
    __name__ = "dummy"
    __file__ = ''

class DummyContext:
    def __init__(self, resolved=DummyModule):
        self.actions = []
        self.info = None
        self.resolved = resolved
        self.package = None

    def action(self, discriminator, callable=None, args=(), kw={}, order=0):
        self.actions.append((discriminator, callable, args, kw, order))

    def path(self, path):
        return path

class Dummy:
    pass

class DummyRoute:
    pass

class DummyRequest:
    subpath = ()
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        self.path_info = environ.get('PATH_INFO', None)

    def get_response(self, app):
        return app

    def copy(self):
        return self

class DummyPackage(object):
    def __init__(self, name):
        self.__name__ = name
        self.__file__ = '/__init__.py'

def extract_actions(native):
    from zope.configuration.config import expand_action
    L = []
    for action in native:
        (discriminator, callable, args, kw, includepath, info, order
         ) = expand_action(*action)
        d = {}
        d['discriminator'] = discriminator
        d['callable'] = callable
        d['args'] = args
        d['kw'] = kw
        d['order'] = order
        L.append(d)
    return L
        
