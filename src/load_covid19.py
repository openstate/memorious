#!/usr/bin/env python3

import sys
import argparse
from glob import glob
import os
from os.path import basename, splitext
import json
from pathlib import Path
from pprint import pprint
from itertools import islice, chain
from time import sleep

# Import alephclient:
from alephclient.api import AlephAPI

# Load the followthemoney data model:
from followthemoney import model

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def load_meta(f):
    result = None
    with open(f, 'r') as in_file:
        result = json.load(in_file)
    return result

def create_document(document_url, title, description, mod_date):
    doc_proxy = model.make_entity('Folder')
    doc_proxy.make_id(document_url)
    doc_proxy.add('title', title)
    # doc_proxy.add('bodyText', description)
    # doc_proxy.add('modifiedAt', mod_date)
    # doc_proxy.add('sourceUrl', document_url)
    return doc_proxy

def create_link(document_id, muni_id, start_date=None, end_date=None):
    # Create the link entity proxy:
    link_proxy = model.make_entity('UnknownLink')

    # We'll derive the link ID from the other two IDs here, but
    # this could be any unique value (make sure it does not clash
    # with the ID for the main entity!)
    link_proxy.make_id('link', muni_id, document_id)

    # Now we assign the two ends of the link. Note that we can just
    # pass in a proxy object:
    link_proxy.add('subject', muni_id)
    link_proxy.add('object', document_id)
    link_proxy.add('role', 'Period')
    if start_date is not None:
        link_proxy.add('startDate', start_date)
    if end_date is not None:
        link_proxy.add('endDate', end_date)
    return link_proxy

def chunks(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))

def main(argv):
    parser = argparse.ArgumentParser(description='Load data into Aleph')
    parser.add_argument('-f', '--foreign-id', default='decentrale_regelgeving', help='foreign id for Aleph')
    parser.add_argument('-d', '--data-path', default='decentrale_regelgeving', help='Path to the data files')
    parser.add_argument('-b', '--batch-size', default=1, type=int, help='Batch size for uploading to Aleph')
    parser.add_argument('-s', '--sleep', default=0, type=int, help='Sleep time between batches')
    parsed_args = parser.parse_args(argv[1:])

    # By default, alephclient will read host and API key from the
    # environment. You can also pass both as an argument here:
    api = AlephAPI()

    # Get the collection (dataset)
    data_path = parsed_args.data_path
    foreign_id = parsed_args.foreign_id

    collection = api.load_collection_by_foreign_id(foreign_id)
    collection_id = collection.get('id')

    main_folders = {}
    batch_count = 0
    for f in glob('%s/*.json' % (data_path,)):
        root, ext = splitext(f)
        meta = load_meta(f)
        done_path = '%s.done' % (root,)
        if os.path.exists(done_path):
            eprint("%s was already done and uploaded to aleph." % (f,))
            continue
        if 'url' not in meta.keys():
            eprint("No url for %s, continuing" % (f,))
            continue
        if '/pdf' not in meta['headers'].get('Content-Type', ''):
            eprint("%s is not a pdf, continuing" % (f,))
            continue
        if not os.path.exists(root):
            eprint("%s pdf was not converted into pages, skipping" % (f,))
            continue
        folder_meta = {
            'title': meta['url'].split('/')[-1],
            'foreign_id': meta['url'],
            'source_url': meta['url'],
            'modified_at': meta['modified_at']
        }
        base_url = meta['url'].replace(folder_meta['title'], '')
        print(base_url)
        try:
            pub_id = main_folders[base_url]
        except Exception as e:
            pub_id = None
        if pub_id is None:
            pub_meta = {
                'title': meta.get('title'),
                'description': meta.get('description'),
                'foreign_id': base_url,
                'source_url': base_url,
                'modified_at': meta['modified_at']
            }
            result = api.ingest_upload(collection_id, None, pub_meta)
            pub_id = result.get('id')
        folder_meta['parent'] = {'id': pub_id}
        result = api.ingest_upload(collection_id, None, folder_meta)
        parent_id = result.get('id')
        for p in glob('%s/*.pdf' % (root,)):
            proot, pext = splitext(p)
            meta['file_name'] = '%s' % (p.replace('%s/' % (root,), ''),)
            if parent_id is not None:
                metadata = {
                    #'pdfHash': meta['url'],
                    'parent': {'id': parent_id}
                }
                meta.update(metadata)
            #pprint(meta)
            result = api.ingest_upload(collection_id, Path(p), meta)
            document_id = result.get('id')
            if parent_id is None:
                parent_id = document_id
            batch_count += 1
            if batch_count > parsed_args.batch_size:
                sleep(parsed_args.sleep)
                batch_count = 0
        open(done_path, 'a').close()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
