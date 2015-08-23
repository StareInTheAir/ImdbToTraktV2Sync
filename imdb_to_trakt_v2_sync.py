#! /usr/bin/env python3

"""
ImdbToTraktV2Sync - Syncs trakt with IMDB watchlist
Usage:
    imdb_to_trakt_v2_sync.py --watchlist <watchlist-csv-file> [--timezone <timezone>] [--oauth-pin <oauth-pin>]
    imdb_to_trakt_v2_sync.py -h | --help
    imdb_to_trakt_v2_sync.py -v | --version
    imdb_to_trakt_v2_sync.py --print-timezones

Options:
    --watchlist <watchlist-csv-file>    The csv watchlist file you downloaded from IMDB.
    --timezone <timezone>               Timezone to use to interpret IMDB dates.
                                        To see all available timezones: --print-timezones
                                        [default: America/Los_Angeles]
    --oauth-pin <oauth-pin>             Your retrieved OAuth2 PIN. When you run this script for the first time, visit
                                        http://trakt.tv/pin/5851 and grant this script access to your trakt account.
                                        You will get a PIN. Pass this PIN here. You only need to do this the first time.
    -h --help                           Show this message.
    -v --version                        Show version.
    --print-timezones                   Prints all available pytz timezones, that can be chosen for --timezone argument

https://github.com/StareInTheAir/ImdbToTraktV2Sync
"""

import csv
import datetime
from functools import reduce
import sys

import docopt
import requests
import pytz

import trakt_v2_oauth


def get_imdb_movies(csv_filename):
    # taken from https://github.com/Thijxx/imdb_to_trakt
    # credit goes also to unutbu (http://stackoverflow.com/a/21581339/2634932)
    reader = csv.reader(open(csv_filename))

    # skip header row
    next(reader)

    included_cols = [1, 2, 5, 6, 11]
    fields = ['imdb_id', 'watched_at', 'title', 'title_type', 'year']
    return [{field: row[i] for field, i in zip(fields, included_cols)} for row in reader]


def convert_imdb_date_string_to_datetime(imdb_date_string):
    return datetime.datetime.strptime(imdb_date_string, '%a %b %d %H:%M:%S %Y')


def sync_imdb_to_trakt():
    arguments = docopt.docopt(__doc__, version='1.0.1')

    if arguments['--print-timezones']:
        for timezone in pytz.all_timezones:
            print(timezone)
        sys.exit()

    user_timezone = pytz.timezone(arguments['--timezone'])

    imdb_movies = get_imdb_movies(arguments['--watchlist'])

    untested_movies = list(
        filter(lambda movie: movie['title_type'] not in ['Feature Film', 'Documentary', 'TV Movie'], imdb_movies))

    if len(untested_movies) > 0:
        print('Warning: There are some entries of an untested type in your IMDB watchlist. '
              'These will be synchronized, but the result may be unexpected.')
        print('The entries in question are: %s' % reduce(lambda output, current: '%s%s%s (%s)' %
                                                                                 (output,
                                                                                  ', ' if len(output) > 0 else '',
                                                                                  current['title'],
                                                                                  current['title_type']),
                                                         untested_movies, ''))

    # convert imdb watched_at date to datetime using pytz
    for movie in imdb_movies:
        movie['watched_at'] = user_timezone.localize(convert_imdb_date_string_to_datetime(movie['watched_at']))

    access_token = trakt_v2_oauth.get_access_token(arguments['--oauth-pin'])

    watched_movies_request = requests.get('https://api-v2launch.trakt.tv/sync/watched/movies', headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token,
        'trakt-api-version': '2',
        'trakt-api-key': trakt_v2_oauth.client_id
    })

    if watched_movies_request.status_code != 200:
        sys.exit('Getting watched movies from trakt failed with http code %d.\n%s' %
                 (watched_movies_request.status_code, watched_movies_request.text))

    already_watched_imdb_ids = reduce(
        lambda output, current: output + [current['movie']['ids']['imdb']],
        watched_movies_request.json(), [])

    movies_to_sync = list(
        filter(lambda imdb_movie: imdb_movie['imdb_id'] not in already_watched_imdb_ids, imdb_movies))

    skipped_movies = len(imdb_movies) - len(movies_to_sync)
    if skipped_movies > 0:
        print('Not synchronizing %d movie%s, because they are already marked as watched in trakt.' %
              (skipped_movies, 's' if skipped_movies != 1 else ''))

    movies_sync_request = requests.post('https://api-v2launch.trakt.tv/sync/history', headers={
        'Authorization': 'Bearer ' + access_token,
        'trakt-api-version': '2',
        'trakt-api-key': trakt_v2_oauth.client_id
    }, json={
        'movies': list(map(lambda movie: {
            'title': movie['title'],
            'year': movie['year'],
            'watched_at': pytz.utc.normalize(movie['watched_at'].astimezone(pytz.utc)).isoformat(),
            'ids': {
                'imdb': movie['imdb_id']
            }
        }, movies_to_sync))
    })

    if movies_sync_request.status_code == 201:
        movies_sync_request_response = movies_sync_request.json()
        print('Successfully synchronized %s movie%s with trakt.' %
              (movies_sync_request_response['added']['movies'],
               's' if movies_sync_request_response['added']['movies'] != 1 else ''))
        number_of_unrecognized_movies = len(movies_sync_request_response['not_found']['movies'])
        if number_of_unrecognized_movies > 0:
            print('%d unrecognized movie%s: %s' %
                  (number_of_unrecognized_movies, 's' if number_of_unrecognized_movies != 1 else '',
                   reduce(
                       lambda output, current: '%s%s%s (%s)' %
                                               (output, ', ' if len(output) > 0 else '', current['title'],
                                                current['year']),
                       movies_sync_request_response['not_found']['movies'], '')))
    else:
        sys.exit('Synchronizing movies with trakt failed with http code %d.\n%s' %
                 (movies_sync_request.status_code, movies_sync_request.text))


if __name__ == '__main__':
    sync_imdb_to_trakt()
