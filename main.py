from MALUser import User

if __name__ == '__main__':
    salixor = User('mrsalixor')
    krocoh = User('Krocoh')
    phokopi = User('phokopi')
    eyedroid = User('Eyedroid')
    vaninou = User('Vanorc')
    blackjack = User('BlackJack_21')

    salixor.retrieveAnimeList()
    krocoh.retrieveAnimeList()
    phokopi.retrieveAnimeList()
    eyedroid.retrieveAnimeList()
    vaninou.retrieveAnimeList()
    blackjack.retrieveAnimeList()

    salixor.retrieveMangaList()
    krocoh.retrieveMangaList()
    phokopi.retrieveMangaList()
    eyedroid.retrieveMangaList()
    vaninou.retrieveMangaList()
    blackjack.retrieveMangaList()

    User.toTSV(salixor, krocoh, phokopi, eyedroid, vaninou, blackjack, destination = 'shared_works_anime.tsv')
    User.toTSV(salixor, krocoh, phokopi, eyedroid, vaninou, blackjack, destination = 'shared_works_manga.tsv', worktype="manga")

    User.toCSV(salixor, krocoh, phokopi, eyedroid, vaninou, blackjack, destination = 'shared_works_anime.csv')
    User.toCSV(salixor, krocoh, phokopi, eyedroid, vaninou, blackjack, destination = 'shared_works_manga.csv', worktype="manga")
