"""
This file defines the database models
"""
from .common import db, Field, auth
from pydal.validators import *

from pyzotero import zotero
from .settings_private import LIBRARY_ID, LIBRARY_TYPE, ZOTERO_API_KEY
import json
import os
from .settings import CACHE_PATH


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#


def rebuild_cache():
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
    searchz('')
    

def searchz(search_string):
    """
    Searches a Zotero group for all occurrences of search_string.
    Text contained in PDF attachments is included in the search.
    Returns a Python dictionary containing HTML formatted bibliographic
    references and links to attached PDFs and other files.
    
    Note:
    
    To rebuild the cache so that it syncs with changes to the Zotero database, 
    delete cache.json, then search for a blank search string.
    """

    print(LIBRARY_ID)
    Z = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, ZOTERO_API_KEY)

    # Load CACHE
    
    if os.path.exists(CACHE_PATH):
         with open(CACHE_PATH) as f:
            CACHE = json.load(f)
    else:
        CACHE = dict()
    print('CACHE loaded. {} items.'.format(len(CACHE)))

    # Perform search

    results_dict = dict()
    print('{} Searching for "{}"'.format(auth.get_user()['username'], search_string))
    search_result = Z.everything(Z.top(q=search_string, qmode='everything'))
    print('{} items found.'.format(len(search_result)))

    for search_result_item in search_result:
        search_result_key = search_result_item['key']

        # Update CACHE if necessary

        if search_result_key not in CACHE:
            print('Adding {} to CACHE.'.format(search_result_key))
            CACHE[search_result_key] = dict()
            print(Z.item(search_result_key))
            CACHE[search_result_key]['bib'] = Z.item(search_result_key, content='bib', linkwrap=True)

            # Add list of enclosures (attached files) to CACHE
            if search_result_item.get('data').get('itemType') not in ['attachment','note']:
                children = Z.children(search_result_key)
                enclosure_list = list()
                for child in children:
                    enclosure_list.append(child.get('links').get('enclosure'))
                CACHE[search_result_key]['enclosure_list'] = enclosure_list

        # Build results dict

        results_dict[search_result_key] = dict()
        results_dict[search_result_key]['bib'] = CACHE[search_result_key]['bib'][0]
        enclosures = CACHE[search_result_key].get('enclosure_list')
        if enclosures:
            results_dict[search_result_key]['enclosure_list'] = enclosures

    # Save CACHE

    cache_length = len(CACHE)
    with open(CACHE_PATH, 'w') as f:
        json.dump(CACHE, f)
    print('CACHE saved. {} items.'.format(cache_length))

    return search_string, results_dict, cache_length


