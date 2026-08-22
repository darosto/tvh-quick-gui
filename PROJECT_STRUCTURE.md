# tvh-quick-gui – Projektstruktur

## Root

| Datei | Beschreibung |
|-------|--------------|
| app.py | Einstiegspunkt der FastAPI-Anwendung |
| README.md | GitHub-Projektbeschreibung |
| CHANGELOG.md | Versionshistorie |
| PROJECT_STRUCTURE.md | Übersicht über das Projekt |

---

## routes/

| Datei | Aufgabe |
|-------|----------|
| dashboard.py | Startseite |
| tv.py | Live-TV |
| guide.py | TV Guide |

---

## services/

| Datei | Aufgabe |
|-------|----------|
| tvheadend_channel_service.py | Lädt Sender aus TVHeadend |
| tvheadend_epg_service.py | Lädt EPG-Daten |

---

## models/

| Datei | Aufgabe |
|-------|----------|
| channel.py | Channel-Dataclass |

---

## templates/

| Datei | Aufgabe |
|-------|----------|
| base.html | Grundlayout |
| dashboard.html | Dashboard |
| tv.html | TV-Ansicht |
| guide.html | TV Guide |

---

## static/css/

| Datei | Aufgabe |
|-------|----------|
| webos.css | Komplettes tvh-quick-gui Design |

---

## static/js/

### core/

| Datei | Aufgabe |
|-------|----------|
| application.js | Startet tvh-quick-gui |
| event-bus.js | Kommunikation zwischen Widgets |
| events.js | Zentrale Event-Definitionen |
| page.js | Basisklasse für Seiten |
| widget.js | Basisklasse für Widgets |

---

### pages/

| Datei | Aufgabe |
|-------|----------|
| dashboard-page.js | Dashboard |
| tv-page.js | TV-Seite |
| guide-page.js | TV Guide |

---

### widgets/

| Datei | Aufgabe |
|-------|----------|
| player.js | TV-Player |
| channel-list.js | Senderliste |
| channel-info.js | Senderinformationen |
| osd.js | On Screen Display |

---

## Architektur

TVHeadend

↓

Services

↓

Routes

↓

Templates

↓

Pages

↓

Widgets

↓

Benutzer


## Entwicklungsregeln

- Neue Dateien nur anlegen, wenn eine bestehende Datei nicht erweitert werden kann.
- Eine Datei hat genau eine Aufgabe.
- Kommunikation zwischen Komponenten erfolgt über den EventBus.
- TVHeadend-Zugriffe erfolgen ausschließlich über Services.
- Pages koordinieren Widgets, Widgets enthalten die Logik.
