import matplotlib.pyplot as plt
from langdetect import detect
from scipy import sparse
import unidecode as ud
import networkx as nx
import json_lines
import itertools
import argparse
import json
import re

def get_hashtags(tweet):
    """
    Parse tweet hashtags
    """
    return [t['text'].lower() for t in tweet['entities']['hashtags']]

def get_edges(hastags):
    """
    Connect hashtags appearing in the same tweet
    """
    return [x for x in itertools.combinations(hastags, 2)]

def load_jsonl(file, lang):
    with open(file, 'rb') as f:
        # extract relevant fields from tweets. Be aware that replies
        # have a different structure. For example, assuming we would
        # like to extract hashtags we need to distinguish between different cases
        # (other fields return truncated text and hastags)
        list_tweets_hashtags = list()
        for tweet in json_lines.reader(f, broken=True):
            # tweet is a reply
            if 'retweeted_status' in tweet:
                try:
                    final_tweet = tweet['retweeted_status']['extended_tweet']
                    text = final_tweet['full_text']
                except:
                    # text and hashtags have not been truncated
                    final_tweet = tweet['retweeted_status']
                    text = final_tweet['text']
            # no reply
            else:
                try:
                    final_tweet = tweet['extended_tweet']
                    text = final_tweet['full_text']
                except:
                    final_tweet = tweet
                    text = final_tweet['text']
            text = ud.unidecode(text)
            text = re.sub(r'[^\w-]','', text)
            if text != '' and detect(text) == lang:
                list_tweets_hashtags.append(get_hashtags(final_tweet))
    return list_tweets_hashtags



if __name__ == "__main__":

    # Define arguments
    parser = argparse.ArgumentParser()
    # Output file path, where to store data (.json formatted)
    parser.add_argument('--data_path', type=str, required=True)
    # Output file path, where to store data (.json formatted)
    parser.add_argument('--adj_path', type=str, required=True)
    # Output file path, where to store data (.json formatted)
    parser.add_argument('--gephi_path', type=str, required=True)
    # Languange
    parser.add_argument('--lang', type=str, required=True)
    # Parse arguments to dictionary
    args = parser.parse_args()

    print("Loading hashtags...")
    list_tweets_hashtags = load_jsonl(args.data_path, args.lang)

    print("Generating network...")

    G=nx.Graph()

    # Weights for new and already existing edges
    default_weight = 1.0
    weight_increment = 1.0

    for hashtags in list_tweets_hashtags:
        G.add_nodes_from(hashtags)
        # remove duplicates -> convert to a set and then back to list
        hashtags = list(set(hashtags))
        if len(hashtags)>1:
            edges = get_edges(hashtags)
            for edge in edges:
                if G.has_edge(*edge):
                    G.get_edge_data(*edge)['weight'] += weight_increment
                else:
                    G.add_edge(*edge, weight=default_weight)

    # get largest connected component
    largest_cc = max(nx.connected_components(G), key=len)
    cc = G.subgraph(largest_cc).copy()

    # Save adjacency matrix
    print('Savign adjacency matrix as {}'.format(args.adj_path))
    adj = nx.to_scipy_sparse_matrix(cc)
    print('Shape:', adj.shape)
    sparse.save_npz(args.adj_path, adj)

    # Save file for gephi
    print("Saving gepx file as {}".format(args.gephi_path))
    nx.write_gexf(cc, args.gephi_path, version='1.2draft')
