# covid-5g hashtags: interaction analysis

## Authentication

Authentication to Twitter APIs can be enable by just filling in `data/auth.json` file as follows:

```
{
    "consumer_key": "fill-with-consumer-key",
    "consumer_secret": "fill-with-consumer-secret",
    "token_key": "fill-with-token-key",
    "token_secret": "fill-with-token-secret"
}
```

These data can be easily retrieved from Twitter developer's dashboard.

## Data retrival

The ```download.py``` script allows to download tweets with different kind of queries, randomly sampling the used time intervals.

### OPTION 1
- Command: ```python scripts/download.py --from_date "2020-07-01" --add_days 2 --out_path "some/path.jsonl" --label <env_name> --product <product_name> --keywords "#COVID" "#COVID19" --language en```
- Output: ```Sampling tweets from 2020-07-01 to 2020-07-03
Generated query:  #COVID OR #COVID19 lang:en
Downloading samples...
  (1/2) first 100 tweets from 2020-07-01 04:55:24 to 2020-07-01 05:55:24
  (2/2) first 100 tweets from 2020-07-02 06:31:13 to 2020-07-02 07:31:13```

### OPTION 2
- Command: ```python scripts/download.py --from_date "2020-07-01" --add_days 2 --out_path "some/path.jsonl" --label <env_name> --product <product_name> --keywords "#COVID" "#COVID19" --add_5g --language en```
- Output: ```Sampling tweets from 2020-07-01 to 2020-07-03
Generated query:  (#5g #COVID) OR (#5g #COVID19) lang:en
Downloading samples...
  (1/2) first 100 tweets from 2020-07-01 16:41:14 to 2020-07-01 17:41:14
  (2/2) first 100 tweets from 2020-07-02 08:43:32 to 2020-07-02 09:43:32```

### ADDITIONAL OPTIONS

- ```--language ```: tweets language, ```en``` or ```it``` implemented;

- ```--window```: dimension (in hours mins secs) of the time interval to be sampled;

- ```--to_date```: overwrites the ```add_days``` parameter;

- ```--batch_size ```: number of request to be done for each window;

- ```--auth_path```: path of the autentication keys file. Default: `data/auth.json`;

-```--seed```: seed for the random sampling.
