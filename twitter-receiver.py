from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream
import credentials
import json
from time import sleep
from datetime import datetime
import sys

TWEET_METADATA = [
    'created_at',
    'text',
    'id',
    'coordinates',
    'place',
    'retweet_count',
    'favorite_count',
    'lang'
]

TWEET_NESTED_METADATA = {
    'user': ['id', 'location', 'followers_count'],
    'entities': ['hashtags']
}


def extract_tweet_data(raw_tweet):
    """
    Extracts only significant parts from tweet object.
    """
    tweet = json.loads(raw_tweet)
    result = {}

    for data_keyword in TWEET_METADATA:
        result[data_keyword] = tweet.get(data_keyword, None)

    for nested_keyword, nested_attributes in TWEET_NESTED_METADATA.items():
        nested_value = {}
        nested_object = tweet.get(nested_keyword, {})

        for attribute in nested_attributes:
            nested_value[attribute] = nested_object.get(attribute, None)

        result[nested_keyword] = nested_value

    return result


class FileStorageListener(StreamListener):

    def __init__(self, hashtags, storage_filename, storage_dir, chunk_size=1_000, starting_chunk=0):
        super().__init__()
        self.hashtags = hashtags
        self.chunks_counter = starting_chunk
        self.chunk_size = chunk_size

        self.storage_filename = storage_filename
        self.storage_dir = storage_dir

        self.buffer = []
        self.backoff_time = 0

    def on_data(self, raw_data):
        """
        Appends new record to the buffer, saves whole buffer content into file if buffer size limit is exceeded.
        Additionally clears error backoff time.
        """
        processed_data = extract_tweet_data(raw_data)
        self.buffer.append(processed_data)

        if len(self.buffer) >= self.chunk_size:
            self.save_chunk()
            self.chunks_counter += 1
            self.buffer = []

        return True

    def save_chunk(self, verbose=True):
        """
        Dumps buffer content into file. The name of the file is created by concatenating
        storage_filename parameter with chunk number.
        """
        new_file_path = f'{self.storage_dir}/{self.storage_filename}-{str(self.chunks_counter).zfill(4)}.json'
        data = {
            'hashtags': self.hashtags,
            'records': self.buffer
        }

        if verbose:
            print(f'{datetime.now()} ===> saving chunk {self.chunks_counter}')

        with open(new_file_path, 'w') as f:
            json.dump(data, f)

    def on_error(self, status_code):
        print(datetime.now())
        print(status_code)
        # self.backoff()
        return True

    def backoff(self):
        print(f'{datetime.now()} ====> starting backoff sleep for {self.backoff_time} seconds')
        sleep(self.backoff_time)
        self.backoff_time = max(1, self.backoff_time * 2)


if __name__ == "__main__":
    hashtags = ['coronavirus', 'covid19']

    starting_chunk = 0
    if len(sys.argv) > 1:
        starting_chunk = int(sys.argv[1])

    listener = FileStorageListener(
        hashtags=hashtags,
        storage_filename='COVIDtweets',
        storage_dir='./data/twitter-clean/',
        chunk_size=10_000,
        starting_chunk=starting_chunk
    )

    auth = OAuthHandler(credentials.API_KEY, credentials.API_KEY_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)

    stream = Stream(auth, listener)
    stream.filter(track=hashtags)
