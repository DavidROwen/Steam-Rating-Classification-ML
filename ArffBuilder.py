class Game:
    def __init__(self, name='', tags=[], rating=''):
        self.name = name
        self.tags = tags
        self.rating = rating

    def __str__(self):
        return "{} {} Tags: {}".format(self.name, self.rating, self.tags)

    def __repr__(self):
        return "{} {} Tags: {}".format(self.name, self.rating, self.tags)

def build_arff_from_games(games, file_name='default.arff'):
    file_contents = "@RELATION game_ratings\n\n"
    
    #TAGS
    all_tags = set()
    for game in games:
        all_tags.update(game.tags)
    all_tags = list(all_tags)
    for tag in all_tags:
        tag = tag.replace('-','_')
        file_contents += "@ATTRIBUTE " + tag + " integer\n"

    #RATINGS
    all_ratings = list(set([game.rating for game in games]))
    file_contents += "@ATTRIBUTE rating { "
    for rating in all_ratings:
        file_contents += rating
        if rating == all_ratings[-1]:
            file_contents += " }\n"
        else:
            file_contents += ", "
    
    #DATA
    file_contents += "@data\n"
    for game in games:
        for tag in all_tags:
            if tag in game.tags:
                file_contents += '1'
            else:
                file_contents += '0'
            file_contents += ', '

        file_contents += str(game.rating)
        file_contents += '\n'
    
    f = open(file_name, "w")
    f.write(file_contents)
    f.close()

# all_games = []
# all_games.append(Game('God of War', ['action', 'gore'], 'positive'))
# all_games.append(Game('Pokemon', ['jrpg', 'water', 'adventure'], 'good'))
# all_games.append(Game('Halo', ['action', 'shooter', 'fps', 'sci-fi'], 'positive'))

# build_arff_from_games(all_games, 'test.arff')
