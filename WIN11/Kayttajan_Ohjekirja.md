📸🎥 Kuvat ja videot karttalla - Käyttöohje

Tämä ohjelmisto on suunniteltu mediatiedostojen (kuvien ja videoiden) selaamiseen ja hallintaan interaktiivisella kartalla. Se tukee myös tiedostojen GPS-sijaintien muokkaamista suoraan kuvien EXIF-tietoihin sekä videoiden reittien katselua.
1. Käyttöliittymän yleiskatsaus

Näyttö on jaettu kolmeen pääosaan:

    Vasen paneeli (Lähialue): Näyttää listan tiedostoista, jotka näkyvät tällä hetkellä kartan rajauksessa. Lista päivittyy automaattisesti, kun liikutat tai zoomaat karttaa.

    Keskiosa (Kartta ja Media): Interaktiivinen kartta, jossa mediatiedostot näkyvät merkkeinä (kuvat oransseina palloina, videot kameroina). Täällä aukeavat myös kuvien katseluikkuna sekä videosoitin.

    Oikea paneeli (Asetukset ja Suodatus): Sisältää API-avainten hallinnan, kansion valinnan, kartan suodatustyökalut sekä listauksen kaikista ladatuista tiedostoista.

2. Kartan toiminnot ja tasot

Oikeasta yläkulmasta (tasovalikko) voit vaihtaa kartan taustaa.

    Karttatasot: Valittavissa on OpenStreetMap sekä Maanmittauslaitoksen (MML) maastokartta, taustakartta, ilmakuva ja selkokartta.

    Kiinteistörajat: Voit laittaa MML:n kiinteistörajat näkyviin (vaatii lähelle zoomaamisen).

    Historialliset ilmakuvat: Jos tiedostoissasi on vuosilukuja (esim. 2010-2026), valikkoon ilmestyy automaattisesti kyseisten vuosien historialliset ilmakuvat.

    Huom: MML-tasojen käyttö vaatii API-avaimen (katso kohta 7).

3. Kuvien ja videoiden selaaminen

    Esikatselu (PiP - Picture in Picture): Kun viet hiiren karttamerkin päälle, avautuu pieni ikkuna, joka näyttää kuvan esikatselun. Samalla kyseinen tiedosto korostuu sivupaneelin listassa.

    Kuvan avaaminen: Klikkaa karttamerkkiä tai listan nimeä avataksesi kuvan isoon katseluikkunaan (Lightbox). Jos samassa pisteessä on useita kuvia, voit selata niitä nuolinäppäimillä tai reunoilla olevista painikkeista. Ikkuna sulkeutuu Esc-näppäimellä tai rastista.

    Videon toistaminen: Videon klikkaaminen avaa videosoittimen kartan päälle.

4. Videosoitin ja Dronereitit

Jos videossa on GPS-reittidata, kartalle piirtyy punainen viiva.

    Reitin seuranta: Kun video pyörii, kartalla liikkuu keltainen "drone-nuoli", joka näyttää kameran sijainnin ja katselusuunnan reaaliajassa.

    Minikartta: Videon alalaidassa on kelluva minikartta, joka seuraa sijaintia tarkasti. Voit raahata minikarttaa hiirellä eri paikkaan ja muuttaa sen kokoa sen oikeasta alakulmasta.

    Suurennus: "Suurenna"-painike levittää videon koko ruudulle. Tässä tilassa voit siirtää itse videon otsikkoa raahaamalla.

5. Suodatus (Oikea paneeli)

Voit helposti piilottaa tai näyttää tiedostoja kartalla ja listoilla:

    Sijainnin mukaan: Näytä kaikki, vain ne joissa on sijainti (GPS-koordinaatit), tai ne joista sijainti puuttuu.

    Tyypin mukaan: Näytä kaikki, vain JPG-kuvat, vain videot tai muut tiedostot.

6. Sijaintien muokkaaminen (EXIF-tallennus)

Voit siirtää kuvia kartalla uusiin paikkoihin. Uudet koordinaatit tallennetaan suoraan tiedostojen metatietoihin (vaatii tuen backend-palvelimelta).

Tapa A: Yksittäisen kuvan siirto

    Vie hiiri siirrettävän kuvan päälle.

    Klikkaa esikatseluikkunasta "📍 Siirrä kuvapiste".

    Raahaa ilmestyvä maalitaulu oikeaan paikkaan kartalla.

    Klikkaa ilmestyvästä alavalikosta "Tallenna EXIF-tietoihin" (tai Peruuta).

Tapa B: Usean kuvan siirto kerralla (Monivalintatila)

    Laita rasti oikean paneelin kohtaan "🎯 Monivalintatila".

    Klikkaile kartalta tai listalta ne kuvat, jotka haluat siirtää. Valitut kuvat muuttuvat purppuran värisiksi.

    Klikkaa alalaitaan ilmestyvästä valikosta "📍 Siirrä vapaasti". Raahaa iso tähtäin uuteen paikkaan ja tallenna.

    Vaihtoehto (Yhdistäminen): Kun kuvia on valittuna, voit viedä hiiren jonkin toisen (ei-valitun) kuvan päälle ja klikata "🔗 Yhdistä valitut tähän". Tämä siirtää kaikki valitut kuvat suoraan kyseisen kuvan koordinaatteihin.

7. Asetukset ja kansioiden hallinta (Oikea paneeli)

    MML API-avain: Syötä Maanmittauslaitoksen rajapinta-avain ja paina "Tallenna". Tämä mahdollistaa tarkkojen suomalaisten maastokarttojen, kiinteistörajojen ja ilmakuvien käytön. Päivitä selain sivu (F5) tallennuksen jälkeen.

    Kansion lisäys: Klikkaa "➕ Lisää kansio hiirellä" avataksesi järjestelmän kansionvalintaikkunan, josta voit tuoda uusia kuvia ja videoita sovellukseen.

8. Kehityksen tukeminen

Sovelluksen ylälaidan palkissa on linkit, joiden kautta voit halutessasi tukea ohjelmiston kehittäjää (Matti Räsänen).

    PayPal: Suora linkki PayPal-lahjoitukseen.

    Kryptolahjoitus: Klikkaamalla aukeaa ikkuna, jossa on QR-koodit ja lompakko-osoitteet Bitcoinin (BTC), Ethereumin (ETH) ja Solanan (SOL) tukemista varten.
