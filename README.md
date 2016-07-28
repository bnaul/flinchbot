## Synopsis

Python Twitter bot originally intended to replicate the in{,s}anity of @johnflinchbaugh. Primary components are:

1. `markovgen.py`: class that reads in a plain text corpus and generates random sentences based on the input
2. `flinchbot.py`: class that connects to a Twitter account, checks for and responds to mentions, and occasionally posts a random tweet
3. `main.py`: Flask app that responds to HTTP GET's with random messages
4. `messageparse.py`: script for extracting messages from a Facebook data dump `messages.htm` file and outputting plain text
5. `slackparse.py`: script for extracting messages from a Slack zip archive and outputting plain text

## Examples

1. `python markovgen.py -n 12 -c 3 < input.txt`: generates a random fragment of (at least) 12 words where each 3-token phrase appears somewhere in the input file
2. `python flinchbot.py`: responds to any new mentions and posts a new tweet with some small probability
3. `python messageparse.py -n 'John Fontana Flinchbaugh' < messages.htm`: processes Facebook messages and extracts plain text contents of messages from John Fontana Flinchbaugh

## Possible Extensions

1. Cache data structure somewhere so that it doesn't have to be constructed from text each time. More complicated logic like the above idea would likely require this to avoid excessive computational cost.

## References
- Flask app code adapted from https://github.com/pistatium/python_slack_bot.
