import sys, time, os
import requests
import random
from my_cookie import cookie

if len(sys.argv) < 2:
    print('error: no username')
    exit(-1)

username = sys.argv[1]
stop = False
offset = 0

FOLDER_NAME = username + '/'
LIMIT = 1

# create a new folder if it doesn't exist
if (not os.path.exists(FOLDER_NAME)):
    os.mkdir(FOLDER_NAME)
    print('{} is created'.format(FOLDER_NAME))

def setup_cookie(cookie):
    c = {}
    
    sessions = cookie.split('; ')
    for s in sessions:
        o = s.split('=')
        c[o[0]] = o[1]
    
    return c

def image_link(media):
    '''
    get the image link from media
    '''
    token = random.choice(media['token'])
    uri = media['baseUri']
    name = media['prettyName']

    # get fullview
    fullview = None
    for t in media['types']:
        if t['t'] == 'fullview':
            if 'c' in t:
                fullview = t['c']
                fullview = fullview.replace('<prettyName>', name)
            else:
                break

    # print(fullview)
    if fullview != None:
        return '{}/{}?token={}'.format(uri, fullview, token)
    else:
        return '{}?token={}'.format(uri, token)

def image_filename(uri, name):
    '''
    merge the image extension and name
    '''
    extension = uri.split('.')[-1]
    symbols = [':', '/']
    for s in symbols:
        name = name.replace(s, '!')
    return '{}.{}'.format(name, extension)

da_cookie = setup_cookie(cookie)
count = 0
while count < LIMIT:
    r = requests.get('https://www.deviantart.com/_napi/da-user-profile/api/gallery/contents?username={}&offset={}&limit=24&all_folder=true&mode=newest'.format(username, offset), cookies=da_cookie)
    if r.status_code != 200:
        # quit if http request failed
        break

    print('\noffset - {}'.format(offset))
    json = r.json()
    if json['hasMore'] == False:
        break

    json = json['results']
    for result in json:
        if count >= LIMIT:
            break

        media = result['deviation']['media']
        website_link = result['deviation']['url']
        base_uri = media['baseUri']
        token = media['token']

        img_url = image_link(media)
        img_name = FOLDER_NAME + image_filename(base_uri, website_link)
        # print(img_url)
        # print(img_name)

        if (os.path.exists(img_name)):
            print(img_name + ' has ALREADY been downloaded')
            continue

        # use cookie to get forbidden items
        image = requests.get(img_url).content
        with open(img_name, 'wb') as handler:
            handler.write(image)
            print(img_name + ' has been downloaded')
            count += 1
    
    offset += 24
    # rest a little bit
    time.sleep(0.2)

print('\nThank you for using DeviantArt Gallery Downloader\nhttps://github.com/HenryQuan/DAGD\n')