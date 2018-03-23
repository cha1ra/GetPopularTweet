# coding: utf-8
#cha1ra 2018.03.21
#https://qiita.com/kenmatsu4/items/23768cbe32fe381d54a2

from requests_oauthlib import OAuth1Session

#自作
import apiinfo
import wp_twind

import json
#リストをコピーするために使うよ
import copy
from janome.tokenizer import Tokenizer
import urllib.request
import csv



#ツイート取得数
GET_TWEET_NUM = 3
MAX_GET_TWEET_NUM = 100
#ふぁぼの足切りポイント
SINCE_FAV_NUM = 1000

#OAuth認証
def oauth_twitter():
    return OAuth1Session(apiinfo.get('CK'),apiinfo.get('CS'),apiinfo.get('AT'),apiinfo.get('AS'))

#ツイートから情報を取得する辞書型のテンプレ
def tweet_dict():
    dict_temp = {'id':'', 'screen_name':'', 'favorite_count':0, 'text':''}
    return dict_temp


# ツイート投稿を実際に行ってくれる
def post_tweet(tweet_text):
    url = "https://api.twitter.com/1.1/statuses/update.json"

    params = {'status': tweet_text}
    twitter = oauth_twitter()
    req = twitter.post(url, params = params)

    if req.status_code == 200:
        print('OK')
    else:
        print ('Error: %d' % req.status_code)

# search_wordで入ってきたワードで検索、検索結果からリストを返す
def tw_search(search_word):
    url = 'https://api.twitter.com/1.1/search/tweets.json'
    params = {'q': search_word, 'lang': 'ja', 'count':GET_TWEET_NUM}
    twitter = oauth_twitter()
    req = twitter.get(url, params = params)


    search_result = tweet_dict()
    return_results = []

    if req.status_code == 200:
        tweets = json.loads(req.text)
        for tweet in tweets['statuses']:
            #print(tweet['text'])
            #print('https://twitter.com/' + tweet['user']['screen_name'] + '/status/' + str(tweet['id']))
            search_result['id'] = tweet['id']
            search_result['screen_name'] = tweet['user']['screen_name']
            search_result['favorite_count'] = tweet['favorite_count']
            search_result['text'] = tweet['text']
            return_results.append(copy.copy(search_result))
    else:
        print('Error: %d' % req.status_code)
    print(GET_TWEET_NUM,'個のツイートを取得しました。')
    return return_results

#お気に入りリストを取得
def tw_get_favlist(screen_name):
    url = 'https://api.twitter.com/1.1/favorites/list.json'
    params = {'screen_name': screen_name}
    twitter = oauth_twitter()
    req = twitter.get(url, params = params)

    fav_result = tweet_dict()
    return_results = []

    if req.status_code == 200:
        tweets = json.loads(req.text)
        for tweet in tweets:
            if tweet['favorite_count'] >= SINCE_FAV_NUM:
                fav_result['id'] = tweet['id']
                fav_result['screen_name'] = tweet['user']['screen_name']
                fav_result['favorite_count'] = tweet['favorite_count']
                fav_result['text'] = tweet['text']
                return_results.append(copy.copy(fav_result))
    else:
        print ('Error: %d' % req.status_code)
    print('お気に入り一覧取得 ユーザーID: ',screen_name)
    return return_results

# 特定ツイートのリプライ取得
# search APIを使って無理やり使う
def tw_get_reply(screen_name, tweet_id):
    url = 'https://api.twitter.com/1.1/search/tweets.json'
    params = {'q': screen_name, 'lang': 'ja', 'count':MAX_GET_TWEET_NUM, 'since_id':tweet_id}
    twitter = oauth_twitter()
    req = twitter.get(url, params = params)

    return_comments = []
    comment = {'text':'', 'favorite_count':0}

    if req.status_code == 200:
        tweets = json.loads(req.text)
        for tweet in tweets['statuses']:
            if tweet['in_reply_to_status_id'] == tweet_id:
                comment['text'] = tweet['text'].replace(screen_name + ' ', '')
                comment['favorite_count'] = tweet['favorite_count']
                return_comments.append(copy.copy(comment))
            #リプを発見したら、さらにそのIDで検索をかけて主のリプライも追える
            #elif tweet['in_reply_to_status_id'] == 976963682583195648 :
                #print('get!')
    else:
        print('Error: %d' % req.status_code)
    print(return_comments)

#投稿テスト用のツイート文章生成
def create_tweet_text(search_word,most_ret_tweet):
    url = 'https://twitter.com/' + most_ret_tweet['screen_name'] + '/status/' + str(most_ret_tweet['id'])
    tweet_text = '@3zaru テスト投稿：「'    + search_word + '」という検索ワードでホットなツイート\n ' + \
                 '（リツイート数：' + str(most_ret_tweet['retweet_count']) + '件 お気に入り数：' + \
                 str(most_ret_tweet['favorite_count']) + '件）' +  url
    return tweet_text

# janomeを用いた形態素解析
def tokenizer(sentence):
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(sentence)
    for token in tokens:
        print(token)

#Wordpressの記事に埋め込むためのTweet情報を取得
def embed_tweet_info(embed_url):
    url = 'https://publish.twitter.com/oembed?url=' + embed_url
    response = urllib.request.urlopen(url)
    info = json.loads(response.read())
    #print(info)
    #url, author_name, author_url, html, width, height...
    return info

#cvs作成
def twind_csv_database(tweets_list):
    header = tweets_list[0].keys()

    with open('C:/Users/sakajiri/Documents/ResourcesForPython/Twind/tweets_data.csv', 'w') as f:
        writer = csv.writer(f, header, lineterminator='\n') # 改行コード（\n）を指定しておく
        header_row = list(tweets_list[0].keys())
        writer.writerow(header_row)
        for i in tweets_list:
            row = [i['id'], i['screen_name'], i['favorite_count']]
            for column in range(len(row)):
                row[column] = str(row[column])
            writer.writerow(row)

if __name__ == '__main__':

    fav_tweets_list = []

    print('\n------\nTwind Popoular Tweet Searcher beta\n------\n')
    
    #特定の単語について検索をかける
    search_word = '新卒'
    print(search_word + ' に関するツイートを取得…')
    search_results = tw_search(search_word)
    #fav_tweets_list.extend(copy.copy(search_results))
    
    #検索結果で取得されたそれぞれのユーザーのお気に入りツイートのリストを取得
    print('\n各ユーザーのお気に入りツイートリストを取得…')
    print('お気に入り数が ', SINCE_FAV_NUM, ' 以下のツイートは取得されません。')
    for i in search_results:
        fav_tweets_list.extend(copy.copy(tw_get_favlist(i['screen_name'])))

    
    #print(fav_tweets_list)
    print('\n取得ツイート:')
    for i in range(len(fav_tweets_list)):
        print('-----------------')
        print('ふぁぼ数:', fav_tweets_list[i]['favorite_count'])
        print(fav_tweets_list[i]['text'])

    if len(fav_tweets_list) > 0:
        twind_csv_database(fav_tweets_list)

    #tweet_text = create_tweet_text(search_word,most_ret_tweet)
    #post_tweet(tweet_text)
    #tokenizer('私はご飯を食べました')

    embed_tweet = embed_tweet_info('https://twitter.com/chamenma/status/973970839916888065')
    wp_twind.post(embed_tweet['html'])
    #tw_get_favlist('chamenma')
    #tw_get_reply('@' + ATAGOofficial',976829724000362496)

    print('\n---終了しました---\n')
