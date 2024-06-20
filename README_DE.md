# WiseFlow

**[中文](README_CN.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [English](README.md)**

**Wiseflow** ist ein agiles Information-Mining-Tool, das in der Lage ist, prägnante Nachrichten aus verschiedenen Quellen wie Webseiten, offiziellen WeChat-Konten, sozialen Plattformen usw. zu extrahieren. Es kategorisiert die Informationen automatisch mit Tags und lädt sie in eine Datenbank hoch.

Es mangelt uns nicht an Informationen, sondern wir müssen den Lärm herausfiltern, um wertvolle Informationen hervorzuheben! 

Sehen Siewie WiseFlow Ihnen hilft, Zeit zu sparen, irrelevante Informationen zu filtern und interessante Punkte zu organisieren!

https://github.com/TeamWiseFlow/wiseflow/assets/96130569/bd4b2091-c02d-4457-9ec6-c072d8ddfb16

<img alt="sample.png" src="asset/sample.png" width="1024"/>

## 🔥 Wichtige Updates in V0.3.0

- ✅ Neuer universeller Web-Content-Parser, der auf GNE (ein Open-Source-Projekt) und LLM basiert und mehr als 90% der Nachrichtenseiten unterstützt.

- ✅ Neue asynchrone Aufgabenarchitektur.

- ✅ Neue Strategie zur Informationsextraktion und Tag-Klassifizierung, die präziser und feiner ist und Aufgaben mit nur einem 9B LLM perfekt ausführt.

## 🌟 Hauptfunktionen

- 🚀 **Native LLM-Anwendung**  
  Wir haben die am besten geeigneten Open-Source-Modelle von 7B~9B sorgfältig ausgewählt, um die Nutzungskosten zu minimieren und es datensensiblen Benutzern zu ermöglichen, jederzeit vollständig auf eine lokale Bereitstellung umzuschalten.


- 🌱 **Leichtes Design**  
  Ohne Vektormodelle ist das System minimal invasiv und benötigt keine GPUs, was es für jede Hardwareumgebung geeignet macht.


- 🗃️ **Intelligente Informationsextraktion und -klassifizierung**  
  Extrahiert automatisch Informationen aus verschiedenen Quellen und markiert und klassifiziert sie basierend auf den Interessen der Benutzer.

  😄 **Wiseflow ist besonders gut darin, Informationen aus WeChat-Official-Account-Artikeln zu extrahieren**; hierfür haben wir einen dedizierten Parser für mp-Artikel eingerichtet!


- 🌍 **Kann in jedes RAG-Projekt integriert werden**  
  Kann als dynamische Wissensdatenbank für jedes RAG-Projekt dienen, ohne dass der Code von Wiseflow verstanden werden muss. Es reicht, die Datenbank zu lesen!


- 📦 **Beliebte PocketBase-Datenbank**  
  Die Datenbank und das Interface nutzen PocketBase. Zusätzlich zur Webschnittstelle sind APIs für Go/JavaScript/Python verfügbar.
    
    - Go: https://pocketbase.io/docs/go-overview/
    - JavaScript: https://pocketbase.io/docs/js-overview/
    - Python: https://github.com/vaphes/pocketbase

## 🔄 Unterschiede und Zusammenhänge zwischen Wiseflow und allgemeinen Crawler-Tools und RAG-Projekten

| Merkmal                | WiseFlow                                           | Crawler / Scraper                        | RAG-Projekte               |
|------------------------|----------------------------------------------------|------------------------------------------|----------------------------|
| **Hauptproblem gelöst** | Datenverarbeitung (Filterung, Extraktion, Tagging) | Rohdaten-Erfassung                       | Downstream-Anwendungen     |
| **Zusammenhang**       |                                                    | Kann in Wiseflow integriert werden, um leistungsfähigere Rohdaten-Erfassung zu ermöglichen | Kann Wiseflow als dynamische Wissensdatenbank integrieren |

## 📥 Installation und Verwendung

WiseFlow hat fast keine Hardwareanforderungen, minimale Systemlast und benötigt keine dedizierte GPU oder CUDA (bei Verwendung von Online-LLM-Diensten).

1. **Code-Repository klonen**

     😄 Liken und Forken ist eine gute Angewohnheit

    ```bash
    git clone https://github.com/TeamWiseFlow/wiseflow.git
    cd wiseflow
   
    conda create -n wiseflow python=3.10
    conda activate wiseflow
    cd core
    pip install -r requirement.txt
    ```

Sie können `pb`, `task` und `backend` mit den Skripten im Verzeichnis `core/scripts` starten (verschieben Sie die Skriptdateien in das Verzeichnis `core`).

**Hinweis:**
- Starten Sie immer zuerst `pb`. `task` und `backend` sind unabhängige Prozesse und können in beliebiger Reihenfolge gestartet werden, oder es kann nur einer von ihnen nach Bedarf gestartet werden.
- Laden Sie zuerst den PocketBase-Client, der Ihrem Gerät entspricht, von [hier](https://pocketbase.io/docs/) herunter und platzieren Sie ihn im Verzeichnis `/core/pb`.
- Bei Problemen mit dem Betrieb von `pb` (einschließlich Fehler beim ersten Start usw.), siehe [`core/pb/README.md`](/core/pb/README.md).
- Erstellen und bearbeiten Sie vor der Verwendung die `.env`-Datei und platzieren Sie sie im Stammverzeichnis des wiseflow-Code-Repositories (eine Ebene über dem Verzeichnis `core`). Die `.env`-Datei kann auf `env_sample` verweisen. Detaillierte Konfigurationsanweisungen sind unten aufgeführt.
- Es wird dringend empfohlen, den Docker-Ansatz zu verwenden. Siehe den fünften Punkt unten.

📚 Für Entwickler siehe [/core/README.md](/core/README.md) für weitere Informationen.

Zugriff auf die erfassten Daten über PocketBase:
- http://127.0.0.1:8090/_/ - Admin-Dashboard-Interface
- http://127.0.0.1:8090/api/ - REST-API


2. **Konfiguration**

    Kopiere `env_sample` im Verzeichnis und benenne es in `.env` um, und fülle deine Konfigurationsinformationen (wie LLM-Service-Tokens) wie folgt aus:

   - LLM_API_KEY # API-Schlüssel für den Large-Model-Inference-Service (falls du den OpenAI-Dienst nutzt, kannst du diesen Eintrag löschen)
   - LLM_API_BASE # URL-Basis für den Modellservice, der OpenAI-kompatibel ist (falls du den OpenAI-Dienst nutzt, kannst du diesen Eintrag löschen)
   - WS_LOG="verbose"  # Debug-Logging aktivieren, wenn nicht benötigt, löschen
   - GET_INFO_MODEL # Modell für Informations-Extraktions- und Tagging-Aufgaben, standardmäßig gpt-3.5-turbo
   - REWRITE_MODEL # Modell für Aufgaben der Konsolidierung und Umschreibung von nahegelegenen Informationen, standardmäßig gpt-3.5-turbo
   - HTML_PARSE_MODEL # Modell für Web-Parsing (intelligent aktiviert, wenn der GNE-Algorithmus unzureichend ist), standardmäßig gpt-3.5-turbo
   - PROJECT_DIR # Speicherort für Data- Cache- und Log-Dateien, relativ zum Code-Repository; standardmäßig das Code-Repository selbst, wenn nicht angegeben
   - PB_API_AUTH='email|password' # Admin-E-Mail und Passwort für die pb-Datenbank (**sie kann fiktiv sein, muss aber eine E-Mail-Adresse sein**)
   - PB_API_BASE  # Nicht erforderlich für den normalen Gebrauch, nur notwendig, wenn du nicht die standardmäßige PocketBase-Local-Interface (Port 8090) verwendest.


3. **Modell-Empfehlung**

    Nach wiederholten Tests (auf chinesischen und englischen Aufgaben) empfehlen wir für **GET_INFO_MODEL**, **REWRITE_MODEL**, und **HTML_PARSE_MODEL** die folgenden Modelle für optimale Gesamteffekt und Kosten: **"zhipuai/glm4-9B-chat"**, **"alibaba/Qwen2-7B-Instruct"**, **"alibaba/Qwen2-7B-Instruct"**.

    Diese Modelle passen gut zum Projekt, sind in der Befolgung von Anweisungen stabil und haben hervorragende Generierungseffekte. Die zugehörigen Prompts für dieses Projekt sind ebenfalls für diese drei Modelle optimiert. (**HTML_PARSE_MODEL** kann auch **"01-ai/Yi-1.5-9B-Chat"** verwenden, das in den Tests ebenfalls sehr gut abgeschnitten hat)

⚠️ Wir empfehlen dringend, den **SiliconFlow** Online-Inference-Service für niedrigere Kosten, schnellere Geschwindigkeiten und höhere kostenlose Quoten zu verwenden! ⚠️

Der SiliconFlow Online-Inference-Service ist mit dem OpenAI SDK kompatibel und bietet Open-Service für die oben genannten drei Modelle. Konfiguriere LLM_API_BASE als "https://api.siliconflow.cn/v1" und LLM_API_KEY, um es zu verwenden.

😄 Oder Sie möchten vielleicht meinen [Einladungslink](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92) verwenden, damit ich auch mehr Token-Belohnungen erhalten kann 😄


4. **Lokale Bereitstellung**

    Wie du sehen kannst, verwendet dieses Projekt 7B/9B-LLMs und benötigt keine Vektormodelle, was bedeutet, dass du dieses Projekt vollständig lokal mit nur einer RTX 3090 (24 GB VRAM) bereitstellen kannst.

    Stelle sicher, dass dein lokaler LLM-Dienst mit dem OpenAI SDK kompatibel ist und konfiguriere LLM_API_BASE entsprechend.


5. **Programm ausführen**

    ```bash
    docker compose up
    ```

    **Hinweis:**
   - Führen Sie die obigen Befehle im Stammverzeichnis des wiseflow-Code-Repositories aus.
   - Erstellen und bearbeiten Sie vor dem Ausführen die `.env`-Datei im selben Verzeichnis wie die Dockerfile (Stammverzeichnis des wiseflow-Code-Repositories). Die `.env`-Datei kann sich auf `env_sample` beziehen.
   - Beim ersten Ausführen des Docker-Containers können Fehler auftreten. Dies ist normal, da Sie noch kein Admin-Konto für das `pb`-Repository erstellt haben.

    Lassen Sie den Container in diesem Fall weiterlaufen, öffnen Sie `http://127.0.0.1:8090/_/` in Ihrem Browser und folgen Sie den Anweisungen, um ein Admin-Konto zu erstellen (verwenden Sie unbedingt eine E-Mail). Füllen Sie dann die erstellte Admin-E-Mail (nochmals, verwenden Sie unbedingt eine E-Mail) und das Passwort in die `.env`-Datei ein und starten Sie den Container neu.


6. **Geplanten Quellen-Scan hinzufügen**

    Nach dem Start des Programms öffnen Sie die PocketBase Admin-Dashboard-UI unter [http://127.0.0.1:8090/_/](http://127.0.0.1:8090/_/).

    6.1 Öffnen Sie das **tags-Formular**

    Dieses Formular ermöglicht es Ihnen, Ihre Interessenschwerpunkte anzugeben. Das LLM wird die Informationen entsprechend verfeinern, filtern und kategorisieren.

    **Beschreibung des Tags-Felds:**
    - `name`: Beschreibung des Interessenschwerpunkts. **Hinweis: Seien Sie spezifisch**. Ein gutes Beispiel ist `Trends im Wettbewerb zwischen den USA und China`; ein schlechtes Beispiel ist `Internationale Situation`.
    - `activated`: Gibt an, ob der Tag aktiviert ist. Wenn deaktiviert, wird dieser Interessenschwerpunkt ignoriert. Das Ein- und Ausschalten erfordert keinen Neustart des Docker-Containers und wird beim nächsten geplanten Task aktualisiert.

    6.2 Öffnen Sie das **sites-Formular**

    Dieses Formular ermöglicht es Ihnen, benutzerdefinierte Informationsquellen anzugeben. Das System wird geplante Hintergrundaufgaben starten, um diese Quellen lokal zu scannen, zu analysieren und zu verarbeiten.

    **Felderbeschreibung des Formulars sites:**
   - url: Die URL der Quelle. Die Quelle muss nicht die spezifische Artikelseite angeben, nur die Artikelliste-Seite.
   - per_hours: Häufigkeit des Scannens, in Stunden, ganzzahlig (Bereich 1~24; wir empfehlen eine Scanfrequenz von einmal pro Tag, also auf 24 eingestellt).
   - activated: Ob aktiviert. Wenn deaktiviert, wird die Quelle ignoriert; sie kann später wieder aktiviert werden.


## 🛡️ Lizenz

Dieses Projekt ist unter der [Apache 2.0](LICENSE) Lizenz als Open-Source verfügbar.

Für kommerzielle Nutzung und maßgeschneiderte Kooperationen kontaktieren Sie uns bitte unter **E-Mail: 35252986@qq.com**.

- Kommerzielle Kunden, bitte registrieren Sie sich bei uns. Das Produkt verspricht für immer kostenlos zu sein.
- Für maßgeschneiderte Kunden bieten wir folgende Dienstleistungen basierend auf Ihren Quellen und geschäftlichen Anforderungen:
  - Dedizierter Crawler und Parser für Kunden-Geschäftsszenario-Quellen
  - Angepasste Strategien zur Informationsextraktion und -klassifizierung
  - Zielgerichtete LLM-Empfehlungen oder sogar Feinabstimmungsdienste
  - Dienstleistungen für private Bereitstellungen
  - Anpassung der Benutzeroberfläche

## 📬 Kontaktinformationen

Wenn Sie Fragen oder Anregungen haben, können Sie uns gerne über [Issue](https://github.com/TeamWiseFlow/wiseflow/issues) kontaktieren.

## 🤝 Dieses Projekt basiert auf den folgenden ausgezeichneten Open-Source-Projekten:

- GeneralNewsExtractor (General Extractor of News Web Page Body Based on Statistical Learning) https://github.com/GeneralNewsExtractor/GeneralNewsExtractor
- json_repair (Reparatur ungültiger JSON-Dokumente) https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (PocketBase Client SDK für Python) https://github.com/vaphes/pocketbase

# Zitierung

Wenn Sie Teile oder das gesamte Projekt in Ihrer Arbeit verwenden oder zitieren, geben Sie bitte die folgenden Informationen an:

```
Author: Wiseflow Team
https://openi.pcl.ac.cn/wiseflow/wiseflow
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
