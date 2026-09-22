L'objectiu del programa és agafar una llista d'esdeveniments d'usuaris i convertir-los en mètriques i consells que tinguin valor real per l'usuari. Al mateix temps, per a usuaris sensibles, també s'ha de notificar al seu responsable tenint sempre en compte la privacitat de l'usuari. Anem a veure com hem abordat aquest problema:


**EXPLICACIÓ DEL PROGRAMA**
El programa està organitzat per capes d'abstracció. Hi ha 4 capes i es comuniquen entre elles mitjançant DTOs (dtos.py):
    - Capa 1 (parse_events.py): Aquesta capa agafa els esdeveniments RAW del .json i els dona sentit. (Pickup, PassiveGlance, UsageBlock, AppSession, Block).
    
    - Capa 2 (metrics_aggregator.py): Ara que ja tenim unitats de comportament amb sentit registrats al llarg dels 30 dies, agrupem i sumem aquests registres en marcs temporals de 24h. Això facilitarà posteriorment el seu anàlisi.
    
    - Capa 3 (score_engine.py): Un cop la anterior capa ens dona un agregat del comportament diari de l'usuari, usem la Capa 3 per a calcular els "Healthy points" cada día.
            
            El mètode usat per a calcular aquesta puntuació és molt senzill.
            S'han establert 4 possibles penalitzacions: Temps de pantalla, Fragmentació, Temps nocturn y Bloquejos.
            Cada una d'aquestes penalitzacions té un valor màxim, 30,25,25 i 20 respectivament.
            Per a calcular la puntuació restem de forma lineal el valor de cada un d'aquests parametres a la puntuació màxima (100).
            
            Per exemple, si l'unica penalització que hem fet en un dia son 180min de pantalla (el màxim abans de penalització són 120min i la penalització màxima s'obté als 360min), la puntuació total es calcularia de la forma:
                    Total = 100 - ((Temps pantalla - 120)/240)*30 = 92.5punts
                    
            Aqui esta la llista de penalitzacions:
            
            ┌─────────────────────────┬──────────────────┬────────┐
            │      Penalización       │ Libre → Completo │ Máximo │
            ├─────────────────────────┼──────────────────┼────────┤
            │ Pantalla                │ 120 → 360 min    │ 30     │
            ├─────────────────────────┼──────────────────┼────────┤
            │ Fragmentación (pickups) │ 25 → 75          │ 25     │
            ├─────────────────────────┼──────────────────┼────────┤
            │ Noche                   │ 0 → 60 min       │ 25     │
            ├─────────────────────────┼──────────────────┼────────┤
            │ Bloqueos                │ 3 → 50           │ 20     │
            └─────────────────────────┴──────────────────┴────────┘
            
    - Capa 4 (guardian_engine.py i nudge_engine.py): Capa final. Aqui agafem la puntiació de la capa anterior i prenem decisions al respecte de si notificar o no al responsable i de si mostrar un nudge al usuari.
        
        Un exemple de nudge seria "Ya es tarde. Descansar también es cuidarte: ¿dejamos el móvil hasta mañana? Tu yo de mañana te lo agradecerá." Si es sobrepassa el límit de temps nocturn.
        
        La notificació al responsable sempre es farà de forma privada. L'unica informació que pot consultar el responsable és la Data, puntuació, minuts nocturns i nombre de bloquejos sensibles. Mai tindrá accés al nom concret de les apps ni webs consultades per l'usuari. Hi ha 3 motius de falta, puntuació inferior a 50, ús nocturn i bloquejos sensibles, el responsable rebrá una notificacio ATTENTION_NEEDED quan alguna d'aquestes faltes tingui una ratxa de 3 dies consecutius. L'estat ATTENTION_NEEDED desapareixerà quan es tingui una ratxa de 3 dies saludables.


Alguna de les decisions que shan pres es, per exemple, excloure el temps de son del "streak". D'aquesta forma nomes es conta el temps real que sha estat sense agafar el mobil.
A mode ilustratiu sha agafat "el dia d'avui" com a l'ultim dia de la mostra del .json.

**COM EXECUTAR-LO**        
El programa està escrit en python per el que executar-lo hauria de ser senzill:

    En una terminal executarem:
        cd [RUTA]/digital-wellbeing/ui
        ../.venv/bin/streamlit run app.py --server.port 8502
    I en una altra Terminal executarem:
        cd [RUTA]/digital-wellbeing/viewer
        ../.venv/bin/streamlit run app.py --server.port 8501
        
        
Vaig demanar a Claude que em fes un petit portal web per poder visualitzar les dades des de les diferents capes del programa a fi de poder comprendre millor com actua cada una d'aquestes capes. S'accedeix a aquest portal amb http://localhost:8501/

Per altra banda, per veure el resultat final hauriem d'anar a http://localhost:8502/. Això és una mescla entre una possible UI de la aplicació mesclada amb dades adicionals sobre privacitat al final. He intentat recrear una mica la estetica de Balanced mitjançant les imatges que teniu a la web pero la veritat que no tinc molta idea de com es el vostre llenguatge de disseny jeje.

Observant les dades podem veure clarament quin tipus de usuari son cada un. L'usuari A ha entés perfectament la filosofía Balanced i te uns habits digitals saludables ;)
Mentre que l'usuari B te molt mals hàbits digitals.


**REPTES**
El primer repte que he enfrontat ha estat escollir la tecnología de implementació. He acabat escollint Python per que és el llenguatge interpretat amb el que tinc mes facilitat. Obviament el programa hauria d'implementar-se per a dispositius mòbils pero he cregut que a fins expositius python era una bona decisió.

Tot seguit he hagut de decidir com organitzar conceptualment el codi per a que sigui comprensible i fàcil de mantenir en un futur. He cregut que separar el codi en capes llogiques era el mes adient.

**PROPOSTES DE FUTUR**
Una de les coses que crec que sería bó és personalitzar més els nudges. Per exemple podriem fer que si l'usuari te molts bloks relacionats amb GAMBLING que li dirigeixi a un lloc d'atenció psicologica o al portal d'autoprohibició del joc (https://www.ordenacionjuego.es/participantes-juego/juego-seguro/rgiaj).

Implementar Nudges o sugerencies per a patrons coneguts és senzill, però poder en un escenari real sería interessant poder generar nudges i sugerencies personalitzades a patrons de comportament mes complexos. Això podria fer-se executant LLMs de petit tamany de forma local o cridant a una API de tercers. Es podria entrenar un LLM molt petit i eficient especialitzat unica i exclusivament en detectar patrons de comportament compulsiu complexos i donar respostes personalitzades.

Un exemple d'aixo sería detectar que als caps de setmana, quan l'usuari está a casa és un 300% més probable de caure en patrons compulsius i aplicant solucions preventives per ajudar-lo de forma personalitzada.

M'agradaría haber implementat aquestes propostes però segurament no hagues estat una implementació que pugui fer-se en uns pocs dies amb una qualitat acceptable.

Ja em direu que opineu de tot plegat i podem veurens per parlar-hi.
Gràcies.