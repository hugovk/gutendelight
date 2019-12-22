# @gutendelight

[![Build Status](https://travis-ci.org/hugovk/python-ci-static-analysis.svg?branch=master)](https://travis-ci.org/hugovk/python-ci-static-analysis)
[![Python: 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Tweeting a mix of hip-hop (Rapper's Delight, Fight the Power, The Message, etc.) and classic literature from Project Gutenberg.

See the Twitter bot in action at **[![](https://abs.twimg.com/favicons/favicon.ico)@gutendelight](https://twitter.com/gutendelight)** and some of the best at [![](http://favstar.fm/favicon.ico)Favstar](http://favstar.fm/users/gutendelight).

## Some examples

> The brother who rocks so viciously  
> *He gazed at me suspiciously*

https://twitter.com/hugovk/status/564387719259111425

> He said, "Sit down, punk, I wanna talk to you  
> *Each has his lot, and bears the fate he drew.*

https://twitter.com/gutendelight/status/566563697787940865

> I guess by now you can take a hunch  
> *"Let us consider," said he, after lunch.*

https://twitter.com/gutendelight/status/566563143791673344

> Then you throw your hands high in the air,  
> *"I don't see," said the native Bear.*

https://twitter.com/gutendelight/status/566560879475687425

## Algorithm goes a little something like this

1. Pick a random line from a file containing a bunch of hip-hop lyrics.
2. Take the last word and find its rhymes using the [Wordnik API](http://developer.wordnik.com/docs.html#!/word/getRelatedWords_get_4).
3. Pick a rhyme at random.
4. Find all the sentences from the [Project Gutenberg August 2003 CD](http://www.gutenberg.org/wiki/Gutenberg:The_CD_and_DVD_Project) ("contains 600 of our best Ebooks") that end with that rhyming word (using [gutengrep](https://github.com/hugovk/gutengrep)).
5. Pick one that's about the same number of syllables as the first line (using [Akkana Peck's countsyl](https://github.com/akkana/scripts/blob/master/countsyl)).
6. If no rhymes or matches found, or a sentence is too long, try another until something's found.
7. Tweet 'em!
