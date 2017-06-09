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

    User.toCSV(salixor, krocoh, phokopi, eyedroid, vaninou, blackjack)
    User.toTSV(salixor, krocoh, phokopi, eyedroid, vaninou, blackjack)