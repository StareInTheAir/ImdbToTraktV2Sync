#! /usr/bin/env python3

from functools import reduce
import sys

import requests

import trakt_v2_oauth


def delete_all_movies_from_history():
    access_token = trakt_v2_oauth.get_access_token()

    movie_history_request = requests.get('https://api-v2launch.trakt.tv/sync/history/movies', headers={
        'Authorization': 'Bearer ' + access_token,
        'trakt-api-version': '2',
        'trakt-api-key': trakt_v2_oauth.client_id
    }, json={
        'username': 'me',
        'limit': 999999
    })

    if movie_history_request.status_code != 200:
        sys.exit('Getting watched movies from trakt failed with http code %d.\n%s' %
                 (movie_history_request.status_code, movie_history_request.text))

    trakt_history_ids = list(reduce(
        lambda output, current: output + [current['id']],
        movie_history_request.json(), []))

    print('Are you sure, you want to delete %d movies from your history?' % len(trakt_history_ids))
    answer = raw_input('Type "y" to proceed: ')
    if answer != 'y':
        sys.exit('aborted')

    movies_remove_request = requests.post('http://api-v2launch.trakt.tv/sync/history/remove', headers={
        'Authorization': 'Bearer ' + access_token,
        'trakt-api-version': '2',
        'trakt-api-key': trakt_v2_oauth.client_id
    }, json={
        'ids': trakt_history_ids
    })

    if movies_remove_request.status_code == 200:
        movies_sync_request_response = movies_remove_request.json()
        print('Successfully removed %s movie%s from trakt history.' %
              (movies_sync_request_response['deleted']['movies'],
               's' if movies_sync_request_response['deleted']['movies'] != 1 else ''))
    else:
        sys.exit('Deleting movies failed with http code %d.\n%s' %
                 (movies_remove_request.status_code, movies_remove_request.text))


if __name__ == '__main__':
    delete_all_movies_from_history()
