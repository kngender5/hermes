# Workspace Provisioning — Opprettelse av Akademisk Arbeidsområde

## Katalogstruktur (Standard V2)

```
~/projects/<workspace-name>/
├── SOUL.md                    # Identitet, språk- og resonneringsmandat
├── MEMORY.md                  # Minnebindinger, kataloglås, pre-eksekveringsregler
├── extract_canvas.py          # Canvas API-ekstraktor
├── ingest_lecture.sh          # Forelesningstranskripsjon ( chmod +x )
├── curriculum/
│   ├── syllabus_master.xlsx   # Automatisk generert oppgaveoversikt
│   └── audit_syllabus.py      # EXAM-PREP gap-analyse
├── laws/
│   └── COMPLIANCE_PROTOCOL.md # Regulatorisk verifikasjonsprotokoll
├── video_transcripts/         # Forelesningslogger, lydspor, transkripsjoner
├── workspace_calculations/    # SymPy-skript, Jupyter-notatbøker
├── plc_code/                  # IEC 61131-3 ST-filer og funksjonsblokker
├── drafts/
│   └── IEEE_RAPPORT_MAL.md    # IEEE-rapportmal
├── artifacts/                 # Genererte PDF-er, diagrammer, bodediagrammer
├── logs/                      # Kjørelogger
├── reports/                   # Risikovurderinger, samsvarserklæringer
├── references/                # Eksterne referanser
├── scripts/                   # Hjelpeskript
├── templates/
│   └── exam_notes_builder.md  # EXAM-PREP formelsamlingsmal
└── docs/
    ├── IEEE/                  # IEEE-standardreferanser
    ├── Kildekompasset/        # Kildekompasset-retningslinjer
    └── kurs/                  # Kurs-spesifikt materiell
```

## Innholdsmessige Krav til Hovedfiler

### SOUL.md
- Kjerneidentitet med ekspertrolle
- Språk- og siteringsmandat (IEEE + Kildekompasset)
- Resonneringstoken-protokoll (PLAN, INNER_MONOLOGUE, REFLECTION)
- Matematisk rendringsregel (LaTeX for formler, ren tekst for enheter)

### MEMORY.md
- Katalogstruktur med beskrivelser per mappe
- Pre-eksekveringsport: kryssreferanse mot lokale referanser
- Eksplisitt begrensning: skal ikke påvirke global SOUL.md/MEMORY.md

### extract_canvas.py
- canvasapi + pandas + dotenv
- Laster ned alle aktive kursos filer per kurskode
- Genererer syllabus_master.xlsx med oppgaver, frister, poeng

### audit_syllabus.py (EXAM-PREP gap-analyse)
- Leser syllabus_master.xlsx med pandas
- Sjekker om hver Assignment_Title finnes i kombinert tekst fra alle .md-filer under drafts/
- Verifiserer at både tema OG en løsningsworkflow er tilstede
- Krever at extract_canvas.py er kjørt først

### ingest_lecture.sh
- yt-dlp med cookies for autentiserte nettsteder (Panopto)
- ffmpeg for lydekstraksjon (mono, 16kHz, MP3)
- whisper-ctranslate2 --model large-v3 --compute_type float16 --device cuda --language no
- Kjøres med: ./ingest_lecture.sh <VIDEO_URL>
- Krever cookies.txt i video_transcripts/-mappen

## Pitfalls

### .bashrc-alias i ikke-interaktiv kontekst
Terminalverktøyets terminal()-kjøring skjer i en ikke-interaktiv sub-shell. Alias registrert i .bashrc er IKKE tilgjengelige der fordi .bashrc har en guard ("If not running interactively, don't do anything"). Brukes kun i nye interaktive terminaløkter eller etter manuelt "source ~/.bashrc".

### Sikkerhetspolicy for dotfile-skriving
Kommandoer som skriver til dotfiler via >> (f.eks. "echo ... >> ~/.bashrc") trigget HIGH-sikkerhetsregelen ("Dotfile overwrite detected"). Disse blokkeres inntil brukeren eksplisitt godkjenner. Å iterere med samme kommando fører til ytterligere blokkering — vent på brukerbekreftelse.

### PEP 668 pip-install i system-Python
"pip install" mot system-Python på Ubuntu trigget PEP 668-blokkering. Bruk alltid:
  pip install --break-system-packages <pakker>
Ikke "uv pip install" med mindre et virtuelt miljø er satt opp.
