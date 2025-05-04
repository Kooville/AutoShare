# AutoShare

## Sovelluksen toiminnot
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sovellukseen.
- Käyttäjä pystyy ilmoittamaan oman autonsa käytettäväksi.
    - Ilmoitukseen kerrotaan vapaat ajat, ajoneuvon koko, hinta sekä sijainti.
    - Ilmoitukseen voi lisätä kuvia.
    - Ilmoitukseen voi lisätä vapaamuotoisen kuvauksen kohteesta.
- Ilmoituksia pystyy muokata ja poistaa.
- Käyttäjä pystyy varaamaan ajoneuvon käyttöönsä vapaana aikana.
    - Pystyy myös perumaan varauksen jolloin ajoneuvo vapautuu taas käyttöön
    - Ilmoituksia voidaan hakea ajoneuvon koon, hinnan tai sijainnin perusteella.
- Sovelluksessa on käyttäjäsivut joista näkee käyttäjän omat ilmoitukset ja linkit niihin, sekä ilmoitusten määrän.


## Sovelluksen käyttöönotto
- Lataa repositorio itsellesi githubista.
- Aja schema.sql tiedoston sql komennot terminaalissa.
    - Sen jälkeen tee sama init.sql tiedoston komennoille.
- Tämän jälkeen aja terminaalissa komennot "python3 -m venv venv" --> "source venv/bin/activate" --> "pip install flask" --> "flask run"
- Tässä kohtaa terminaaliin tulee linkki jossa sivu nyt pyörii.
