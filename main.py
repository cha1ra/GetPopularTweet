# coding: utf-8
#cha1ra 2018.03.21
#https://qiita.com/kenmatsu4/items/23768cbe32fe381d54a2

from requests_oauthlib import OAuth1Session
import apiinfo
import json


# ツイート投稿用のURL
def post_tweet(tweet_text):
	url = "https://api.twitter.com/1.1/statuses/update.json"

	params = {'status': tweet_text}

	twitter = OAuth1Session(apiinfo.get('CK'),apiinfo.get('CS'),apiinfo.get('AT'),apiinfo.get('AS'))
	req = twitter.post(url, params = params)

	if req.status_code == 200:
		print('OK')
	else:
		print ('Error: %d' % req.status_code)

def search(search_word):
	url = 'https://api.twitter.com/1.1/search/tweets.json'
	params = {'q': search_word, 'lang': 'ja', 'count':20}
	twitter = OAuth1Session(apiinfo.get('CK'),apiinfo.get('CS'),apiinfo.get('AT'),apiinfo.get('AS'))
	req = twitter.get(url, params = params)

	return_tweet = {'id':'', 'screen_name':'', 'retweet_count':0, 'favorite_count':0}

	if req.status_code == 200:
		tweets = json.loads(req.text)
		for tweet in tweets['statuses']:
			#print(tweet['text'])
			#print(tweet['retweet_count'])
			#print(tweet['favorite_count'])
			#print(tweet['user']['followers_count'])
			print('https://twitter.com/' + tweet['user']['screen_name'] + '/status/' + str(tweet['id']))
			#一番リツイートが多いやつ (フォロワー制限)
			if(tweet['retweet_count'] > return_tweet['retweet_count']):
				return_tweet['id'] = tweet['id']
				return_tweet['screen_name'] = tweet['user']['screen_name']
				return_tweet['retweet_count'] = tweet['retweet_count']
				return_tweet['favorite_count'] = tweet['favorite_count']
	else:
		print('Error: %d' % req.status_code)
	return return_tweet

#投稿テスト用
def create_tweet_text(search_word,most_ret_tweet):
	url = 'https://twitter.com/' + most_ret_tweet['screen_name'] + '/status/' + str(most_ret_tweet['id'])
	tweet_text = '@3zaru テスト投稿：「'	 + search_word + '」という検索ワードでホットなツイート\n ' + \
				 '（リツイート数：' + str(most_ret_tweet['retweet_count']) + '件 お気に入り数：' + \
				 str(most_ret_tweet['favorite_count']) + '件）' +  url
	return tweet_text



if __name__ == '__main__':
	search_word = '残業'
	most_ret_tweet = search(search_word)
	tweet_text = create_tweet_text(search_word,most_ret_tweet)
	#post_tweet(tweet_text)
