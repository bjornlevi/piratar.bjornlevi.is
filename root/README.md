# piratar.bjornlevi.is
Vefur fyrir alls konar drasl í þinginu

## Einföld hönnunarlýsing
[Alþingi XML](https://www.althingi.is/altext/xml/) vefurinn er með viðamikið safn af upplýsingum um þingmál, ræður, nefndarfundi og ýmislegt annað.

XML skjalið [löggjafarþing](https://www.althingi.is/altext/xml/loggjafarthing/) er með yfirlitslista af öllum löggjafarþingum. Það þýðir ekki endilega að öll löggjafarþing séu með innihaldsríkar upplýsingar. 1. þing til dæmis er með tóma málaskrá og engar ræður. Önnur síða veitir aðgengi að [yfirstandandi þingi](https://www.althingi.is/altext/xml/loggjafarthing/yfirstandandi/) á meðan öll önnur þing eru í raun óbreytanleg - þó að í einhverjum tilfellum er kannski enn verið að lesa yfir ræður eldri þinga og bæta við fleiri skjölum eftir því sem upplýsingar eru skannaðar inn í kerfið.

Meðal þeirra upplýsinga sem nálgast má á vefnum er [þingmannalisti](https://www.althingi.is/altext/xml/thingmenn/). Þar eru tenglar um alla þingmenn sem hafa tekið sæti á Alþingi, hver er fæðingardagur þeirra og nafn. Hver og einn þingmaður fær einnig id. Þingmannalistinn er í stafrófsröð en ekki id röð. Fyrsti þingmaðurinn með id er id="2", einhverra hluta vegna. Í <xml><þingseta> er að finna slóð að xml skjali sem sýnir hvenær hver þingmaður sat á þingi og fyrir hvaða flokk í hvert skipti. Þar er einnig vistuð <skammstöfun> hvers þingmanns.

XML skjalið með [þingflokkum](https://www.althingi.is/altext/xml/thingflokkar/) skiptir einnig máli. Þar er hægt að sjá hvaða þingflokkar sitja á þingi [á hverju þingi](https://www.althingi.is/altext/xml/thingflokkar/?lthing=151) þar sem 151 í þessu tilfelli tilgreinir að um 151. þing sé að ræða.

Sérstakt skjal heldur utan um hverjir eru [þingflokksformenn](https://www.althingi.is/altext/xml/thingflokksformenn/). Sambærilegt skjal er útbúið fyrir þingflokksformenn [hvers þings fyrir sig](https://www.althingi.is/altext/xml/thingflokksformenn/?lthing=150).

 Eitt mikivægasta skjalið er [þingmálalisti hvers þings](https://www.althingi.is/altext/xml/thingmalalisti/?lthing=141) þar sem finna má lista af öllum málum sem lögð hafa verið fram á hverju þingi fyrir sig. Þar má finna málsnúmer, málstegund (bæði táknið fyrir málstegundina og heiti málstegundar), málsheiti og svo slóð á nánari upplýsingar um málið í xml tengli málsins. Þar má finna þingskjöl málsins sem geta verið af ýmis konar skjalategund eins og breytingartillaga og nefndarálit. Þar eru einnig upplýsingar um atkvæðagreiðslur og ræður vegna hvers máls.

Mikilvægar upplýsingar fyrir hvert þingmál er hver leggur fram málið og í hvaða þingflokki viðkomandi er. Ef sá sem leggur fram málið er ráðherra, og þá hvaða ráðherra það er eða hvort það sé þingmaður eða nefnd sem leggur fram málið. [Hér](https://www.althingi.is/altext/xml/nefndir/?lthing=141) má finna upplýsingar um nefndir hvers þings og [hverjir](https://www.althingi.is/altext/xml/nefndir/nefndarmenn/?lthing=141) eru nefndarmenn í hvaða nefnd.

Öll þingskjöl hvers þings má finna [hér](https://www.althingi.is/altext/xml/thingskjol/?lthing=141). Upplýsingarnar þar segja þó lítið nema bara skjalsnúmer, útbýting, skjalstegund og slóð á nánari upplýsingar um þingskjalið undir <slóðir><xml>. Þar er hægt að finna hverjir eru flutningsmenn skjalsins, þar á meðal hvort viðkomandi flutningsmaður sé ráðherra og þá hvaða ráðherra.

 Þó má finna allar [ræður hvers þings](https://www.althingi.is/altext/xml/raedulisti/?lthing=124) í einu skjali. Þar kemur fram hvenær ræða hófst,  hvenær henni lauk, hver tegund ræðunnar er og svo framvegis. Ræðutextann sjálfan þarf að nálgast í gegnum <slóðir><xml> hins vegar. 

Það þarf því oft að gramsa fram og til baka í skjölunum til þess að finna nauðsynlegar upplýsingar um þingmálin. 

Upplýsingarnar sem koma fram á þessari síðu er skipt upp í, fyrir hvert þing:
- Ríkisstjórnarmál, sem eru mál sem einhver ráðherra leggur fram.
- Þingmannamál, sem eru mál sem þingmenn, en ekki ráðherrar leggja fram. 
- Fyrirspurnir sem skiptast upp í svaraðar og ósvaraðar fyrirspurnir. Annars vegar til skriflegs svars og hins vegar fyrirspurnir til munnlegs svars. Svo er sérstök síða fyrir óundirbúnar fyrirspurnir.
- Nefndir, þar sem er síða fyrir hverja nefnd fyrir sig sem sýnir þau mál sem komið hafa til hverrar nefndar fyrir sig.

Allir málalistar sýna málsnúmer, málsheiti, skjalategund, flutningsmann, þingflokk flutningsmanns, í hvaða nefnd málið fór (ef það hefur farið til nefndar), hvenær skjalinu var útbýtt og hvenær það var klárað (ef það er klárað). Það er hægt að flokka málalistann eftir hvaða dálki sem er og einnig leita í málalistanum. Tengill á er á málsheiti hvers máls á <html> vefsíðu þingsins um málið.

Á hverju þingi er sérstök síða um þingflokka og þingmenn sem sýnir upplýsingar um hvern þingmann. Í hvaða nefndum viðkomandi þingmaður. Heildarræðutíma í hverri tegund máls fyrir sig (og samtölu). Lista af þingmálum sem viðkomandi þingmaður hefur lagt fram (eftir tegund, raðað í tímaröð). Mynd sést af hverjum þingmanni sem finnst á eftirfarandi slóð: https://www.althingi.is/myndir/mynd/thingmenn/1474/org/mynd.jpg - þar sem 1474 er id viðkomandi þingmanns. Tengill er á <html> síðu hvers þingmanns frá heiti viðkomandi þingmanns.
