# EKOM Curriculum Coverage Map

## Kilder
Alle filer i `~/projects/study-workbench/curriculum/AUT23_-_Ekom/fagstoff_files/`

## Fil-til-tema-mapping

| PDF-fil | Hovedtema | Emner |
|---|---|---|
| `2025 EKOM - Del 1.pdf` | Studieplan, introduksjon | Hva er EKOM, infrastruktur, transmisjon, Kabel-TV, HMS |
| `2025 EKOM - Del 2 (701).pdf` | NEK 701 - Felles kablingssystemer | EN 50173-serien, normstruktur (normativ/informativ), fjernmating-kategorier RP1/RP2/RP3 |
| `2025 EKOM - Del 3 (702-del 1 og 2).pdf` | NEK 702 - Installasjon innendørs | EN 50174-1/2, dokumentasjon, planlegging |
| `2025 EKOM - Del 4 (702-del 3).pdf` | NEK 702 - Installasjon utendørs | EN 50174-3, føringsveier, segregasjon, jordkabler |
| `2025 EKOM - Frekvens, bølgelengde og desibel.pdf` | Fysiske grunnlagsbegreper | f=1/T, λ=c/f, ω=2πf, dB-formler, lysspekter |
| `2025 EKOM - PoE.pdf` | Power over Ethernet | PSE/PD, aktiv/passiv, endspan/midspan, 802.3af/at/bt |
| `2025 Fiberoptikk i praksis og fiberbudsjett.pdf` | Fiber teori + PON | FTTH, OLT/ONT/ODF, transportnett/aksessnett, GPON, XG-PON, WDM-PON, budsjett |
| `2025 Fiberrør og kabler.pdf` | Kabler og rør | Mikrorør DB, jordanlegg, luftanlegg, splittertyper |
| `2025 Kabel-TV.pdf` | Kabel-TV og HFC | HFC-arkitektur, DVB-C/T/S, IP-TV, IGMP, frekvensspekter |
| `2026 EKOM - DOCSIS.pdf` | DOCSIS-standarden | Versjoner, QAM, OFDM, LDPC, EuroDOCSIS, CMTS, HFC |
| `2022 HMS og FSE i EKOM.pdf` | HMS i EKOM-kontekst | Internkontrollforskriften, relevante lover, HMS-mål |
| `2024 Introduksjon til WDM.pdf` | WDM-teknologi | WDM/CWDM/DWDM, bølgelengder, Mux/Demux, OADM, designregler |
| `2025 Skjøting og Feilsøking fiber Fagskolen.pdf` | Praktisk fiberarbeid | Skjøting, OTDR-målinger, lab-oppgaver |
| `EKOM 2025 - Lover, forskrifter og standarder.pdf` | Fullstendig lovoversikt | Ekomloven, Elsikkerhet, Autorisasjon, EMC, Nkom, §-henvisninger |
| `Forskrifter og standarder med løsningsforslag.pdf` | Øvingsoppgaver med svar | Caseløsning, lovhenvisnings-øvelser |
| `Hvordan besvare en Case.pdf` | Eksamensmetodikk | Trinvis fremgangsmåse for casebesvarelser |

## Eksamensrelevante formler
- Frekvens: f = 1/T
- Bølgelengde: λ = c/f = c·T
- Vinkelfrekvens: ω = 2π·f
- Desibel: dB = 10·log10(P1/P2)
- Optisk budsjett: P_TX - P_RX_min ≥ Σ(demping)

## Nøkkeltabeller å kunne utenat
1. Splitterdempning (1:2=3dB til 1:256=24dB)
2. GPON SFP B+ vs C+ (TX/RX-følsomhet)
3. GPON vs XG-PON vs WDM-PON sammenligning
4. CWDM-kanaler (1271-1611 nm, 18 kanaler)
5. PoE-standarder (802.3af=15.4W, 802.3at=30W, 802.3bt=60W)
6. DOCSIS-versjoner og kapasitet
7. NEK 700-tilknytning (EN 50173, 50174, 50600)
8. Fjernmating-kategorier (RP1≤212mA, RP2≤500mA, RP3≤500mA)

## Output-filer (2026-05-25)
- `~/projects/study-workbench/drafts/EKOM_EKSAMENSNOTATER.md` — komplett markdown-versjon
- `~/projects/study-workbench/drafts/EKOM_EKSAMENSNOTATER.html` — HTML med SVG-diagrammer
- `~/projects/study-workbench/drafts/EKOM_Eksamensnotater_v2.ipynb` — Jupyter notebook v2 (55+ celler), interaktive kalkulatorer, systemdesigner, OTDR-simulator, prosjektplanlegging, komponentvelger, eksamensquiz, HMS-sjekkliste. Se `references/jupyter-notebook-creation.md` for genereringsmønster.
- `~/projects/study-workbench/drafts/NEK_701_702_DETALJERT.md` — NEK 701/702 detaljert referanse
- `~/projects/study-workbench/workspace_groundtruth/` — Ground truth pipeline data (inventory, extracts, verification, gaps)
