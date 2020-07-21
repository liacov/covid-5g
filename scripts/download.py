# Dependencies
from TwitterAPI import TwitterAPI, TwitterPager
from datetime import datetime, date, timedelta
import numpy as np
import argparse
import random
import json
import time
import re

# Constants
# Path to deafult authentication credentials file
AUTH_PATH = 'data/auth.json'
# Products
API_PRODUCT_30DAY = '30day'


# Authentication: allows to query Twitter's web APIs
def auth(consumer_key, consumer_secret, token_key, token_secret):
    # Return asuthenticated twitter APIs object
    api = TwitterAPI(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token_key=token_key, access_token_secret=token_secret
    )

    return api

def authenticate(in_path):
    """
    Load credentials stored in secrets_file_path.json
    Return TwitterAPI object created using credentials
    """
    # Initialize credentials
    credentials = {}
    # Load credentials file
    with open(in_path, 'r') as in_file:
        credentials = json.load(in_file)

    return auth(**credentials)


def get_tweets(api, query, from_date, to_date, product, label, batch_size):
    """
    Return 100 tweets for a specific date
    date format is <yyyymmddhhmm> (201912250000)
    """
    # Parse from and to dates
    from_date = from_date.strftime('%Y%m%d%H%M') if from_date is not None else None
    to_date = to_date.strftime('%Y%m%d%H%M') if from_date is not None else None
    # Generate request
    r = api.request('tweets/search/{0:}/:{1:}'.format(product, label),
                    {
                        'query': query,
                        'maxResults': batch_size,
                        'fromDate': from_date,
                        'toDate': to_date
                    }
                    )
    return r


# Define function for sampling datetime intervals (from date - to date)
def sample_intervals(from_date, to_date, window=(1, 0, 0)):
    """
    Sample tweets from every day betweet start date and end date, using
    a temporal window of a spciefied width (hours, minutes, seconds).

    Input
    1. from_date: starting interval date. Datetime object;
    2. to_date: ending interval date. Datetime object;
    3. window_size: width of the sampling window;

    Output
    1. samples: list of windows. Tuple (start, end) of datetime objects;
    """
    # Initialize list of samples
    samples = list()
    # Define datetime bottom scale (earliest available date)
    bottom_scale = datetime(1970, 1, 1)
    # Retireve window size parameters
    hours, minutes, seconds = window
    # Define window as timedelta (time difference) object
    window = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    # Initialize current date as interval's start date
    curr_date = from_date
    # Loop through each day between start and end date
    while curr_date < to_date:
        # Define next date as next day
        next_date = curr_date + timedelta(days=1)
        # Define first available sampling datetime for current day
        first_datetime = datetime.combine(curr_date, datetime.min.time())
        # Define last available sampling datetime as next day 00:00:00
        last_datetime = datetime.combine(next_date, datetime.min.time())
        last_datetime = last_datetime - window
        # Express first and last datetimes as seconds from Jan 01 1970 (standard)
        first_seconds = int((first_datetime - bottom_scale).total_seconds())
        last_seconds = int((last_datetime - bottom_scale).total_seconds())
        # Randomly sample one datetime between first and last datetime (seconds from first available datetime)
        ws_seconds = random.randrange(start=0, stop=last_seconds-first_seconds, step=1)
        # Compute window start as datetime adding seconds from first available date
        ws_datetime = first_datetime + timedelta(seconds=ws_seconds)
        # Compute window end as datetime
        we_datetime = ws_datetime + window
        # Store current sample
        samples.append((ws_datetime, we_datetime))
        # Update current date
        curr_date = next_date
    # Return samples
    return samples


def main(args):
    # va sostituito con il sampling di damiano
    # dates_list = create_dates(start_date=START_DATE,num_requests=NUM_REQUESTS)

    ######################################
    # Get start date and interval (in days)
    from_date = date.fromisoformat(args.from_date)
    # Case <add_days> is set
    if args.add_days is not None:
        to_date = from_date + timedelta(days=args.add_days)
    # Case <to_date> is set
    elif args.to_date is not None:
        to_date = date.fromisoformat(args.to_date)
    # Case neither <to_date> nor <add_days> are set
    else:
        # Show error message and terminate script
        args.error('Neither <add_days> nor <to_date> parameters have been set')

    # Log sampling interval information
    print('Sampling tweets from {0:%Y-%m-%d} to {1:%Y-%m-%d}'.format(
        from_date,
        to_date
    ))

    # Get sampling window
    hours, minutes, seconds = 1, 0, 0  # Define default window
    window_len = len(args.window)  # Get window size
    # Get hours, minutes and seconds from parameters
    hours = args.window[0] if window_len >= 1 else hours
    minutes = args.window[1] if window_len >= 2 else minutes
    seconds = args.window[2] if window_len >= 3 else seconds
    # Define window
    window = (hours, minutes, seconds)

    # Clean and add hashtag to keywords
    keywords = args.keywords
    keywords = [re.sub(r'[\#\@ ]', '', kw) for kw in keywords]  # Remove hashtags and whitespaces
    keywords = ['#' + kw for kw in keywords]  # Add hashtags at the beginning of the keyword

    # Get language
    language = args.language

    # create query, list of available operators here:
    # https://developer.twitter.com/en/docs/tweets/search/overview/premium#AvailableOperators
    query = ''  # Initialize query
    query = query + (' OR '.join(keywords) if keywords else '')  # Add keywords
    query = query + (' lang:{0:s}'.format(language) if language else '')  # Add language
    # NB: logical connectors must be changed manually - mixed query must be written as string
    # print('Generated query: ', query, end='\n\n')

    # Get API label and product
    label = args.label
    product = args.product

    # Get retrieved tweets batch size
    batch_size = args.batch_size

    # Get output file path
    out_path = args.out_path
    # Get flag to decide to overwrite existing file or not
    overwrite = args.overwrite
    # Get authentication credentials files
    auth_path = args.auth_path

    # Get sampled intervals
    samples = sample_intervals(from_date, to_date, window=window)

    # Check if output file must be overwritten
    if overwrite:
        # Create empty file
        open(out_path, 'w', encoding='utf-8').close()

    ############################################

    # authenticate
    api = authenticate(auth_path)

    ################################################
    # Log download started
    print('Downloading samples...')
    # Loop through each sampling interval
    for i, (ws_datetime, we_datetime) in enumerate(samples):
        with open(out_path, 'a', encoding='utf-8') as f:
            # Get tweets for the sampled interval
            tweets = get_tweets(
                api=api,
                query=query,
                from_date=ws_datetime,
                to_date=we_datetime,
                label=label,
                product=product,
                batch_size=batch_size
            )
            # Write tweets to file
            for tweet in tweets:
                json.dump(tweet, f)
                f.write('\n')

        # Show download progress
        print('  ({0:d}/{1:d}) first {2:d} tweets from {3:s} to {4:s}'.format(
            i + 1,  # Current iteration
            len(samples),  # Total number of iterations
            args.batch_size,  # Batch size
            ws_datetime.strftime('%Y-%m-%d %H:%M:%S'),  # Window start time
            we_datetime.strftime('%Y-%m-%d %H:%M:%S')  # Window end time
        ))
        # Sleep 2 seconds
        time.sleep(2)
    ############################################


if __name__ == "__main__":

    # Define arguments
    parser = argparse.ArgumentParser()
    # Must the output file be overwritten? (T/F)
    parser.add_argument('--overwrite', type=bool, default=False)
    # Start date of download period (iso format YYYY-mm-dd)
    parser.add_argument('--from_date', type=str, required=True)
    # End date of download period (iso format YYYY-mm-dd)
    parser.add_argument('--to_date', type=str)
    # Number of days to add to <start_date> in order to obtain <to_date>
    # This overrides <to_date> parameter
    parser.add_argument('--add_days', type=int)
    # Window expressed as hours, minutes, seconds (default 1 hour)
    parser.add_argument('--window', nargs='+', type=int, default=[])
    # Keywords list to be used in query
    parser.add_argument('--keywords', nargs='+', type=str, default=[])
    # Filter tweets language (according to twitter language)
    parser.add_argument('--language', type=str, default='en')
    # Number of tweets retrieved for each request
    parser.add_argument('--batch_size', type=int, default=100)
    # Output file path, where to store data (.json formatted)
    parser.add_argument('--out_path', type=str, required=True)
    # Authentication credentials file path
    parser.add_argument('--auth_path', type=str, default=AUTH_PATH)
    # Twitter-level application name
    parser.add_argument('--label', type=str, required=True)
    # Twitter.level product name
    parser.add_argument('--product', type=str, default=API_PRODUCT_30DAY)
    # Sampling seed (allows reproducibility)
    parser.add_argument('--seed', type=int, required=False)
    # Parse arguments to dictionary
    args = parser.parse_args()

    # Set random seed, if specified
    if args.seed is not None:
        random.seed(args.seed)

    main(args)
