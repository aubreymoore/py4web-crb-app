"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash

from py4web.utils.form import Form, FormStyleBulma
from .models import searchz, rebuild_cache
from . import settings


@authenticated('rebuild_cache_action')
def rebuild_cache_action():
    print('rebuilding cache')
    rebuild_cache()
    print('finished rebuilding cache')


@authenticated('search', 'search_results.html')
def search():
    search_string, results_dict, cache_length = searchz(request.query['search_string'])
    return locals()


@authenticated('index', 'search_form.html')
def search_form():
    user = auth.get_user()
    form = Form([Field('search_string')], formstyle=FormStyleBulma)
    if form.accepted:
        print(URL('search', vars=form.vars))
        redirect(URL('search', vars=form.vars))
    return dict(form=form)
