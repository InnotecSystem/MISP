#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymisp import PyMISP
import argparse

# *** MISP csirt.es ***
misp_url = 'https://www.csirt.es/misp/'
misp_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
misp_cert = '/path/to/certificate.pem'
misp_verifycert = True


def connect(url, key, verify_cert, cer):
    try:
        return PyMISP(url, key, verify_cert, 'json', cert=cer)
    except Exception as e:
        print('Unable to connect to MISP: %s' % e)
        exit(1)


def test_org(m, org):
    result_orgs = m.get_organisations_list('all')
    for r in result_orgs:
        if r['Organisation']['name'].lower() == org.lower():
            return
    print('The organisation ' + org + ' doesn\'t exist')
    exit(1)


def test_tag(m, tag):
    result_tags = m.get_all_tags(True)
    for r in result_tags:
        if r.lower() == tag.lower():
            return
    print('The tag ' + tag + ' doesn\'t exist')
    exit(1)


if __name__ == '__main__':
    # Parsing arguments
    parser = argparse.ArgumentParser(description='Get all the events matching a value for a given param.')
    parser.add_argument('-a', '--action', required=True, help='Action to run: add, change, test')
    parser.add_argument('-o', '--organisation', required=False, help='Search events/attributes in a organisation')
    parser.add_argument('-i', '--attributes', required=False, action='store_true', help='Search attributes instead of events')
    parser.add_argument('-t', '--tag_old', required=True, help='Tag to search')
    parser.add_argument('-n', '--tag_new', required=True, help='Tag to add/change')
    parser.add_argument('-F', '--date_from', required=False, help='First date (yyyy-MM-dd)')
    parser.add_argument('-T', '--date_to', required=False, help='Last date (yyyy-MM-dd)')
    parser.add_argument('-p', '--publish', required=False, action='store_true', help='Publish the event')
    args = parser.parse_args()
    # Connecting to MISP
    misp = connect(misp_url, misp_key, misp_verifycert, misp_cert)
    # Checking the action
    if args.action != 'add' and args.action != 'change' and args.action != 'test':
        print('Invalid action: ' + args.action)
        exit(1)
    # Checking the tags
    test_tag(misp, args.tag_old)
    test_tag(misp, args.tag_new)
    # Including the old tag in search
    kwargs = {'tags': args.tag_old}
    # Including the organisation in search
    if args.organisation is not None:
        test_org(misp, args.organisation)
        kwargs['org'] = args.organisation
    # Including the date_from in search
    if args.date_from is not None:
        kwargs['date_from'] = args.date_from
    # Including the date_to in search
    if args.date_to is not None:
        kwargs['date_to'] = args.date_to
    # Including the new tag in search (for add)
    if args.action == 'add':
        kwargs['not_tags'] = args.tag_new
    # Searching and processing the attributes
    if args.attributes:
        i = 0
        result = misp.search('attributes', **kwargs)
        if len(result['response']) == 0:
            print('No results')
            exit(0)
        for r in result['response']['Attribute']:
            hasTag = False
            if 'Tag' in r:
                for t in r['Tag']:
                    if t['name'] == args.tag_old:
                        hasTag = True
                        break
                if hasTag:
                    if args.action == 'add':
                        print('Adding tag to attribute', r['uuid'], '(event ' + r['event_id'] + ')')
                        misp.tag(r['uuid'], args.tag_new)
                        if args.publish:
                            print('Publishing event', r['event_id'])
                            misp.fast_publish(r['event_id'], alert=False)
                    elif args.action == 'change':
                        print('Adding tag to attribute', r['uuid'], '(event ' + r['event_id'] + ')')
                        misp.tag(r['uuid'], args.tag_new)
                        print('Removing tag to attribute', r['uuid'], '(event ' + r['event_id'] + ')')
                        misp.untag(r['uuid'], args.tag_old)
                        if args.publish:
                            print('Publishing event', r['event_id'])
                            misp.fast_publish(r['event_id'], alert=False)
                    else:
                        print('Testing attribute', r['uuid'], '(event ' + r['event_id'] + ')')
                    i = i + 1
        print(i, 'attribute(s)')
    # Searching and processing the events
    else:
        result = misp.search('events', **kwargs)
        if len(result['response']) == 0:
            print('No results')
            exit(0)
        for r in result['response']:
            if args.action == 'add':
                print('Adding tag to event', r['Event']['id'], '(' + r['Event']['uuid'] + ')')
                misp.tag(r['Event']['uuid'], args.tag_new)
                if args.publish:
                    print('Publishing event', r['Event']['id'])
                    misp.fast_publish(r['Event']['id'], alert=False)
            elif args.action == 'change':
                uuid = r['Event']['uuid']
                print('Adding tag to event', r['Event']['id'], '(' + r['Event']['uuid'] + ')')
                misp.tag(r['Event']['uuid'], args.tag_new)
                print('Removing tag to event', r['Event']['id'], '(' + r['Event']['uuid'] + ')')
                misp.untag(r['Event']['uuid'], args.tag_old)
                if args.publish:
                    print('Publishing event', r['Event']['id'])
                    misp.fast_publish(r['Event']['id'], alert=False)
            else:
                print('Testing event', r['Event']['id'], '(' + r['Event']['uuid'] + ')')
        print(len(result['response']), 'event(s)')
