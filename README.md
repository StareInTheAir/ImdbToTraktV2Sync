# ImdbToTraktV2Sync - Syncs trakt with IMDB watchlist

A nifty python script, that takes your IMDB watchlist and transfers it to your trakt history.

## Features
- Detects which movies you already entered manually into trakt and skips them, so that you don't get duplicate entries
- Correctly sets the trakt property 'watched\_at' based on the date you marked the movie watched on IMDB
- Uses new trakt v2 API with OAuth2
- Runs with python 3 (tested with 3.4) and 2.7 (with small modification)

## Instructions
You need to download your IMDB watchlist as CSV, because IMDB removed the http retrieve feature. Head over to
http://www.imdb.com/list/watchlist, scroll almost all the way down and click "Export this list". Pass the path to the
downloaded file via the ```--watchlist```  option to the script.

IMDB doesn't specify a timezone along their dates in the CSV. I don't know how it was in the past,
but right now it looks like IMDB always uses pacific time, regardless where you actually come from.
If that's different for you, you can pass a pytz timezone via the ```--timezone``` option, 
otherwise ```America_Los_Angeles``` is the default.

You also need to grant this script permission to your trakt account: http://trakt.tv/pin/5851. You will get a
PIN which needs to be passed via the ```--oauth-pin``` option. This is a one time step. The script will redeem the PIN to get
a token and use the token from now on.

If you don't have Python 3 installed, grab it (on OS X with [brew](http://brew.sh): ```brew install python3```)

To execute the script, you will need to install the libraries I used:
```pip3 install docopt requests pytz```

Now you're ready to run the script:
```imdb_to_trakt_v2_sync.py --watchlist ~/Downloads/WATCHLIST.csv --oauth-pin <your pin>```

Or for future times just:
```imdb_to_trakt_v2_sync.py --watchlist ~/Downloads/WATCHLIST.csv```

## Usage
    imdb_to_trakt_v2_sync.py --watchlist <watchlist-csv-file> [--timezone <timezone>] [--oauth-pin <oauth-pin>]
    imdb_to_trakt_v2_sync.py -h | --help
    imdb_to_trakt_v2_sync.py -v | --version
    imdb_to_trakt_v2_sync.py --print-timezones

### Options
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

## Run with python 2.7
Rename ```client_secret_holder_python27.pyc``` to ```client_secret_holder.pyc``` and call the script with
```python2.7 imdb_to_trakt_v2_sync.py …```.

## delete\_complete\_trakt\_movie\_history.py
I wrote this script for debugging purposes. It deletes all the movies in your trakt history. You will need to get a token
from the main script, before you can run this one. Be very careful with this one. There is no undo.