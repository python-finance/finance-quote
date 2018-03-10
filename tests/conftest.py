import betamax
import os

import requests
import sys
from betamax_serializers import pretty_json

import finance_quote.base

betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

record_mode = 'none' if os.environ.get('TRAVIS_GH3') else 'once'

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes/'
    config.default_cassette_options['record_mode'] = record_mode
    config.default_cassette_options['serialize_with'] = 'prettyjson'


# create session
session = requests.Session()


# overwrite default session constructor
finance_quote.base.Session = lambda : session

recorder = betamax.Betamax(session)
