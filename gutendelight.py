#!/usr/bin/env python
# encoding: utf-8
"""
Tweet a random line of rap coupled with a rhyming line from Project Gutenberg.
"""
import argparse
import codecs
import logging
import random
import re
import sys
import webbrowser

import requests
import twitter
import yaml
from wordnik import WordApi, swagger

import countsyl  # https://github.com/akkana/scripts/blob/master/countsyl
import gutengrep

TWITTER = None


def timestamp():
    import datetime

    print(datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))


def load_text(infile):
    """Return a list of non-blank lines, ignore those beginning #"""
    with codecs.open(infile, encoding="cp1252") as f:
        lines = f.read().splitlines()
    return list(line for line in lines if line and not line.startswith("#"))


def get_rhymes_from_wordnik(word):
    global data
    wordnik_client = swagger.ApiClient(
        data["wordnik_api_key"], "http://api.wordnik.com/v4"
    )
    word_api = WordApi.WordApi(wordnik_client)
    rhymes = word_api.getRelatedWords(word, relationshipTypes="rhyme")

    if rhymes:
        rhymes = rhymes[0].words
        # pprint(rhymes)

    return rhymes


def get_rhymes_from_rhymebrain(word):
    logging.basicConfig(level=logging.DEBUG)
    url = "http://rhymebrain.com/talk?"

    # def rhymes_with(word):
    query = f"{url}function=getRhymes&word={word}"
    print_it(query)
    r = requests.get(query)
    data = r.json()
    words = [word["word"] for word in data if word["score"] >= 300]
    return words


def get_matches_from_project_gutenberg(word, sentences):
    """Find a matching sentence ending with this word"""

    # Filter
    flags = re.IGNORECASE  # TODO try with case first? nah...
    #     regex = "\b" + word + "\b\W*$"  # word followed by non-letters and $
    regex = word  # word followed by non-letters and $
    regex = word + r"\b\W*$"  # word followed by non-letters and $
    regex = r"\b" + word + r"\b\W*$"  # word followed by non-letters and $
    print(regex)
    sentences = gutengrep.find_matching_sentences(regex, sentences, flags=flags)

    return sentences


def number_of_syllables(sentence):
    min_syllables, max_syllables = countsyl.count_syllables(sentence)
    syllables = (min_syllables + max_syllables) / 2.0
    return syllables


def gutendelight(rapfile, inspec, cache):
    rap = load_text(rapfile)
    #     pprint(rap)

    # Prep PG
    all_sentences = gutengrep.prepare(inspec, cache)

    while True:

        random_line = random.choice(rap)
        #         print_it(random_line)

        last_word = random_line.split()[-1]
        #         print(last_word)

        # rhymes = get_rhymes_from_wordnik(last_word)
        rhymes = get_rhymes_from_rhymebrain(last_word)
        if not rhymes:
            print("No rhymes found, try next line of rap")
            # TODO try canonical? or just continue and find a better one?
            continue

        random.shuffle(rhymes)
        #         pprint(rhymes)

        random_line_syllables = number_of_syllables(random_line)

        for rhyme in rhymes:
            # print(rhyme)

            # Find rhyming sentences from Project Gutenberg
            sentences = get_matches_from_project_gutenberg(rhyme, all_sentences)
            if not sentences:
                print("No matches found, try next rhyme")
                continue

            sentences = gutengrep.correct_those(sentences)
            # pprint(sentences)

            closest_diff = 999
            best = None
            for sentence in sentences:
                sentence = sentence.replace("\r\n", " ")  # Remove newlines
                sentence = " ".join(sentence.split())  # Remove dupe spaces
                output = random_line + "\n\n" + sentence
                # print("*"*80)
                # print_it(output)
                # print(len(output))
                if len(output) > 280:
                    print("Too long, try next sentence")
                    continue
                else:
                    # Pick one that's about the same number of syllables
                    syllables = number_of_syllables(sentence)
                    diff = abs(random_line_syllables - syllables)
                    # print(diff, random_line_syllables, syllables)
                    if diff < closest_diff:
                        closest_diff = diff
                        best = output
            if best:
                print("Bingo!")
                return best


def load_yaml(filename):
    """
    File should contain:
    consumer_key: TODO_ENTER_YOURS
    consumer_secret: TODO_ENTER_YOURS
    access_token: TODO_ENTER_YOURS
    access_token_secret: TODO_ENTER_YOURS
    wordnik_api_key: TODO_ENTER_YOURS
    """
    with open(filename) as f:
        data = yaml.safe_load(f)

    if not data.keys() >= {
        "access_token",
        "access_token_secret",
        "consumer_key",
        "consumer_secret",
    }:
        sys.exit("Twitter credentials missing from YAML: " + filename)
    if not keys >= {"wordnik_api_key"}:
        sys.exit("Wordnik credentials missing from YAML: " + filename)
    return data


def tweet_it(string, in_reply_to_status_id=None):
    global TWITTER

    if len(string) <= 0:
        print("ERROR: trying to tweet an empty tweet!")
        return

    # Create and authorise an app with (read and) write access at:
    # https://dev.twitter.com/apps/new
    # Store credentials in YAML file
    if TWITTER is None:
        TWITTER = twitter.Twitter(
            auth=twitter.OAuth(
                data["access_token"],
                data["access_token_secret"],
                data["consumer_key"],
                data["consumer_secret"],
            )
        )

    print_it("TWEETING THIS: " + string)

    if args.test:
        print("(Test mode, not actually tweeting)")
    else:
        print("POST statuses/update")
        result = TWITTER.statuses.update(
            status=string, in_reply_to_status_id=in_reply_to_status_id
        )
        url = (
            "http://twitter.com/"
            + result["user"]["screen_name"]
            + "/status/"
            + result["id_str"]
        )
        print("Tweeted: " + url)
        if not args.no_web:
            webbrowser.open(url, new=2)  # 2 = open in a new tab, if possible


if __name__ == "__main__":
    timestamp()

    parser = argparse.ArgumentParser(
        description="Tweet a random line of rap coupled with"
        "a rhyming line from Project Gutenberg.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--rap",
        default="/Users/hugo/Dropbox/txt/raplines.txt",
        help="A text file of rap lyrics.",
    )
    parser.add_argument("inspec", nargs="?", help="Input file spec")
    parser.add_argument(
        "--cache",
        action="store_true",
        help="Load cache. If no cache, save one. Warning: "
        "the cache is saved based on the initial "
        "inspec. Subsequent uses are based on this "
        "initial cache, effectively ignoring inspec. ",
    )
    parser.add_argument(
        "-y",
        "--yaml",
        default="/Users/hugo/Dropbox/bin/data/gutendelight.yaml",
        # default='E:/Users/hugovk/Dropbox/bin/data/gutendelight.yaml',
        help="YAML file containing Twitter and Wordnik keys and secrets",
    )
    parser.add_argument(
        "-nw",
        "--no-web",
        action="store_true",
        help="Don't open a web browser to show the tweeted tweet",
    )
    parser.add_argument(
        "-x",
        "--test",
        action="store_true",
        help="Test mode: go through the motions but don't update anything",
    )
    args = parser.parse_args()

    data = load_yaml(args.yaml)

    output = gutendelight(args.rap, args.inspec, args.cache)
    print("=" * 80)
    print_it(output)
    print("=" * 80)

    print_it("Tweet this:\n" + output)
    try:
        tweet_it(output)

    except twitter.api.TwitterHTTPError as e:
        print("*" * 80)
        print(e)
        print("*" * 80)


# End of file
