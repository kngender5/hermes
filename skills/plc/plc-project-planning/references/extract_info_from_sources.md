# Hva å hente ut fra hver kildefil

Når du samler informasjon for funksjonsbeskrivelsen, bør du trekke ut spesifikke elementer fra hver kildefiltype:

## I/O-liste (I_O_liste.txt)
- **Digitale inn (DI)**: Adresse (f.eks. I0.0), funksjon (f.eks. Start-knapp), type (normalt åpen/lukket), begrunnelse for valg
- **Digitale ut (DO)**: Adresse (f.eks. Q0.0), funksjon (f.eks. Transportelement innlasting → lift), type, begrunnelse
- **Eventuelle analoge I/O**: Hvis tilstede, adresse, måleområde, skaleringsfaktor
- **Reserverte adresser**: Hvilke som er reservert til fremtidig utvidelse
- **Samlet antall**: Totalt antall inn- og utganger (inkl. reserverte) for oversikt

## PLC-oppsett-plan (PLC_oppsett_plan.txt)
- **Valgt PLC-modell**: F.eks. S7-1500 CPU 1511-1 PN, begrunnelse (ytelse, minne, kommunikasjonsbehov)
- **Programmeringsspråk**: LAD og/eller FBD, begrunnelse (tilgjengelighet, teamkompetanse)
- **HW-konfigurasjon**: Modulplassering, adresseområder
- **PROFINET-oppsett**: For HMI-tilkobling
- **Generelle antagelser**: Spenning, frekvens, miljøforhold

## Programsekvenser (Program_sekvenser.txt)
- **Tilstandsmaskin**: Hvert trinn (SeqStep-verdier)
- **For hvert trinn**:
  - Nummer og navn (f.eks. 0 - INITIALISERING)
  - Hovedhandlinger (hvordan outputs/settes, variabler oppdateres)
  - Avsluttende betingelse (hvornår man går til neste trinn)
  - Eventuelle timere/counters brukt
- **Overgangsbetingelser**: Klar logikk for når man går fra ett trinn til et annet
- **Nødstopp/alarm-håndtering**: Hvordan SeqStep 99 aktiveres og deaktiveres
- **Variabelbruk**: Hvordan DB-variabler leses og skrives i sekvensen

## Sikkerhetskrets-dokumentasjon (Sikkerhetskrets_dokumentasjon.txt)
- **Fysisk tilkobling**: Hvordan nødstopp og sensorer er seriekoblet (NC)
- **PLC-input**: Hvilken input som brukes for samlet sikkerhetssignal (f.eks. I0.2)
- **PLC-logikk**: Hvordan Safety_OK deriveres (f.eks. Safety_OK = NOT(I0.2))
- **Utportgating**: Hvordan kritiske outputs AND-es med Safety_OK
- **Alarmhåndtering**: Hvilke alarmbits som settes, hvordan de driver HMI-indikatorer
- **Nullstillingslogikk**: Betingelser for å tillate nullstilling (må være ingen aktive farer + nullstillingsknapp trykket)
- **Standarder**: Hvilke standarder som følges (f.eks. EN ISO 13849-1, EN ISO 13850)

## HMI-utviklingsplan (HMI_utviklingsplan.txt)
- **Kommunikasjon**: PROFINET-kobling mellom S7-1500 og PC
- **Taggkobling**: Mapping fra PLC-DB-variabler til HMI-tagger (f.eks. DB1.TotalEsker → HMI-tagg `TotalEsker`)
- **Skjermstruktur**: Beskrivelse av hver skjerm (oversikt, alarm, alarmlogg, innstillinger)
- **Alarmhåndtering**: Hvordan alarmer vises, kvitteres, logges
- **Datalogg**: Hvordan CSV-logging oppnås (script som leser counter-variabler hver sekund eller ved CycleDone)
- **Språk**: At alt tekst er på norsk (knappetikker, tooltips, alarmbeskrivelser)
- **Oppdateringsfrekvens**: Måloppsdateringsrate (f.eks. 200ms)
- **Sikkerhet**: Passordbeskyttelse for innstillinger, eventuelle nivåer

## Konfigurasjonsoppsummering (Konfigurasjonsoppsummering.txt)
- **I/O-konfig**: Bekreftelse på adressebruk
- **DB-struktur**: Oversikt over alle DB-er og deres formål
- **Sekvens-parametre**: Eventuelle justerbare parametre (timerværdier, maks antall paller per etasje)
- **Sikkerhetsparametre**: Debounce-tider, timeout-verdier
- **HMI-parametre**: Skjermoppløsning, farger, fonter

## FAT-testplan (FAT_testplan.txt)
- **Testkrav**: Hva som skal verifiseres (sekvens, størrelsesrouting, sikkerhet, alarmer, logging)
- **Testprosedyrer**: Hvordan hver test utføres
- **Forventede resultater**: Hva som skal observeres for hver test
- **Acceptanskriterier**: Grenser for hva som godtas

## Bruksanvisning (Bruksanvisning.txt)
- **Brukerprosedyrer**: Hvordan operatøren starter/stopper/anlegget
- **Alarmhåndtering**: Hvordan operatøren skal reagere på forskjellige alarmer
- **Vedlikehold**: Hvilke sjekk som skal gjøres regelmessig
- **Feilsøking**: Vanlige problemer og løsninger
- **Sikkerhetsforskrifter**: Viktige sikkerhetsregler for operatøren

## Generelle prinsipper for utvinning
- **Begrunnelse**: For hvert teknisk valg du inkluderer i funksjonsbeskrivelsen, finn og noter begrunnelsen fra kilfilene
- **Sammenheng**: Sørg for at informasjonen flyter logisk fra overordnet til detaljnivå
- **Unngå duplikasjon**: Hvis samme informasjon finnes i flere filer, noter det én gang med referanse til alle kilder
- **Fyll hull**: Hvis noe mangler i kilfilene (f.eks. begrunnelse for et valg), gjør et kvalifisert antatt og merk det som antatt
