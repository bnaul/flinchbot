import glob
import json
import re
import sys


if __name__ == '__main__':
    name = sys.argv[1]

    users = json.load(open('slack/users.json'))
    user_id = [u for u in users if u['name'] == name][0]['id']

    files = glob.glob('slack/*/*.json')
    data = [json.load(open(f)) for f in files]
    messages = [el for f in data for el in f]
    texts = [m['text'].strip() for m in messages if 'user' in m and 'subtype'
             not in m and m['user'] == user_id]
    for u in users:
        texts = [re.sub('<@{}>'.format(u['id']), '@{}'.format(u['name']), t) for t in texts]
    texts = [re.sub('<[^>]*>', '', t) for t in texts]
#    texts = filter(is_valid, texts)
    for t in texts:
        try:
            print(t)
        except:
            pass
