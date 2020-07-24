# covid-5g hashtags: interaction analysis

## Data retrival

The <code> download.py <\code> script allows to download tweets with different kind of queries, randomly sampling the used time intervals.

### OPTION 1

- Command: <code> python scripts/download.py --from_date "2020-07-01" --add_days 2 --out_path "data/tweets_test_2.jsonl" --label "ClimateDev" --product "30day" --keywords "#COVID" "COVID19"


- Output:

<code> Sampling tweets from 2020-07-01 to 2020-07-03
Generated query:  #COVID OR #COVID19 lang:en

Downloading samples...
  (1/2) first 100 tweets from 2020-07-01 04:55:24 to 2020-07-01 05:55:24
  (2/2) first 100 tweets from 2020-07-02 06:31:13 to 2020-07-02 07:31:13 <\code>



### OPTION 2

- Command: <code> python scripts/download.py --from_date "2020-07-01" --add_days 2 --out_path "data/tweets_test_2.jsonl" --label "ClimateDev" --product "30day" --keywords "#COVID" "COVID19" --add_5g

- Output:

<code> Sampling tweets from 2020-07-01 to 2020-07-03
Generated query:  (#5g #COVID) OR (#5g #COVID19) lang:en

Downloading samples...
  (1/2) first 100 tweets from 2020-07-01 16:41:14 to 2020-07-01 17:41:14
  (2/2) first 100 tweets from 2020-07-02 08:43:32 to 2020-07-02 09:43:32 <\code>
