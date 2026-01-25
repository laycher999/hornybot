import json

pc_tags = []
android_tags = []
games = []
translations = []

def f_open(file_name='games'):
    with open(f'./{file_name}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data

def sort_games_by_tag():
    pc_tags = []
    android_tags = []
    for game in games:
        if 'PC' in games[game]['tags']:
            for tag in games[game]['tags']:
                if tag in pc_tags or tag in ['PC', 'Android', 'Translate']:
                    continue
                pc_tags.append(tag)
        if 'Android' in games[game]['tags']:
            for tag in games[game]['tags']:
                if tag in android_tags or tag in ['PC', 'Android', 'Translate']:
                    continue
                android_tags.append(tag)
    return pc_tags, android_tags


def load():
    global games, pc_tags, android_tags, translations
    games = f_open('games')
    translations = f_open('translations')
    pc_tags, android_tags = sort_games_by_tag()

load()
