# WiseFlow Installations- und Benutzerhandbuch

**3.x Benutzer müssen das ursprüngliche Repository und den pb-Ordner vollständig löschen und das 4.x Repository neu klonen, sonst kann das Programm nicht normal gestartet werden.**

## 📋 Systemanforderungen

- **Python**: 3.10 - 3.12 (3.12 empfohlen)
- **Betriebssystem**: macOS, Linux oder Windows
- **Hardwareanforderungen**: 8GB RAM oder mehr (bei Verwendung von Online-LLM-Diensten)

## 📥 Gebrauchsanweisung

Die Benutzeroberfläche von wiseflow 4.x verwendet PocketBase (obwohl ich es nicht mag, gibt es momentan keine bessere Alternative)

### 1. Zugriff auf die Oberfläche

🌐 Nach erfolgreichem Start öffnen Sie Ihren Browser und besuchen Sie: **http://127.0.0.1:8090/_/**

### 2. Konfiguration von Informationsquellen und Fokuspunkten

Wechseln Sie zum focus_point-Formular

Über dieses Formular können Sie Ihre Fokuspunkte festlegen. Die LLM wird die Informationen entsprechend extrahieren, filtern und kategorisieren.
    
Feldbeschreibungen:
- focuspoint (erforderlich), Beschreibung des Fokuspunkts, teilen Sie dem LLM mit, welche Informationen Sie suchen, z.B. "Informationen zum Übergang von der Grundschule zur Mittelschule in Shanghai", "Ausschreibungsankündigungen"
- restrictions (optional), Einschränkungen für den Fokuspunkt, teilen Sie dem LLM mit, welche Informationen ausgeschlossen werden sollen, z.B. "Nur offizielle Informationen zum Übergang zur Mittelschule in Shanghai", "Veröffentlichungen nach dem 1. Januar 2025 mit einem Wert über 1 Million"
- explanation (optional), Erklärungen für spezielle Konzepte oder Fachbegriffe, um Missverständnisse zu vermeiden, z.B. "Übergang von der Grundschule zur Mittelschule bedeutet den Wechsel von der Grundschule zur Mittelschule"
- activated, ob aktiviert. Wenn deaktiviert, wird dieser Fokuspunkt ignoriert, kann aber später wieder aktiviert werden
- freq, Crawling-Frequenz in Stunden, als ganze Zahl (wir empfehlen, die Scanfrequenz nicht höher als einmal täglich zu setzen, d.h. auf 24, Minimum ist 2, d.h. alle 2 Stunden)
- search, ob bei jedem Crawl die Suchmaschine aktiviert werden soll und ob über konfigurierte soziale Medien gesucht werden soll
- sources, Auswahl der entsprechenden Informationsquellen

**Änderungen an der focus_point-Konfiguration erfordern keinen Neustart des Programms und werden automatisch beim nächsten Durchlauf wirksam.**

Sie können Informationsquellen sowohl auf der sources-Seite als auch auf der focus_points-Seite hinzufügen. Beschreibung der Felder für Informationsquellen:

- type, Typ, derzeit unterstützt: web, rss, wb (Weibo), ks (Kuaishou), mp (WeChat Official Account (4.0 noch nicht unterstützt, wartet auf 4.1))
- creators, IDs der zu crawlenen Ersteller (mehrere mit ',' getrennt), nur gültig für ks, wb und mp, wobei ks und mp 'homefeed' unterstützen (repräsentiert systemgesteuerte Inhalte). Dieses Feld kann auch leer bleiben, dann wird die Quelle nur für die Suche verwendet

  *Hinweis: Die ID muss die entsprechende Webseiten-URL des Profils sein, z.B. für Weibo https://m.weibo.cn/profile/2656274875, dann ist die ID 2656274875*

- url, Link zur Informationsquelle, nur gültig für rss und web-Typen.

### 3. Ergebnisse anzeigen

- infos-Seite speichert die extrahierten nützlichen Informationen
- crawled_data-Seite speichert die gecrawlten Rohdaten
- ks_cache-Seite speichert Kuaishou-Cachedaten
- wb_cache-Seite speichert Weibo-Cachedaten

## 🌟 Installation und Bereitstellung

**Die Installation erfolgt in nur drei Schritten!**

### 📋 Projektquellcode herunterladen und uv sowie pocketbase installieren

- für MacOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

- für Windows:

**Windows-Benutzer müssen zuerst Git Bash herunterladen und dann die folgenden Befehle in Bash ausführen [Bash-Download-Link](https://git-scm.com/downloads/win)**

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

Diese Operationen installieren uv. Für die Installation von pocketbase siehe [pocketbase docs](https://pocketbase.io/docs/)

Sie können auch versuchen, install_pocketbase.sh (für MacOS/Linux) oder install_pocketbase.ps1 (für Windows) zu verwenden.

### 📥 .env-Datei basierend auf env_sample konfigurieren

Erstellen Sie im wiseflow-Ordner (Projektstammverzeichnis) basierend auf env_sample eine .env-Datei und füllen Sie die relevanten Einstellungen aus.

Version 4.x erfordert keine PocketBase-Anmeldedaten in der .env-Datei und begrenzt auch nicht die PocketBase-Version. Außerdem haben wir vorübergehend die Secondary Model-Einstellung entfernt. Sie benötigen daher mindestens nur vier Parameter:

- LLM_API_KEY="" # LLM-Dienstschlüssel (jeder Anbieter mit OpenAI-kompatiblem API-Format ist geeignet, bei lokaler Verwendung von ollama nicht erforderlich)
- LLM_API_BASE="https://api.siliconflow.com/v1" # LLM-Dienstschnittstelle
- JINA_API_KEY="" # Suchmaschinen-Dienstschlüssel (Jina empfohlen, für persönliche Nutzung sogar ohne Registrierung verfügbar)
- PRIMARY_MODEL="Qwen3-14B" # Qwen3-14B oder ähnliches Denkmodell empfohlen
- VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct" # Visuelles Modell, optional aber empfehlenswert. Wird zur Analyse notwendiger Seitenbilder verwendet (das Programm entscheidet basierend auf dem Kontext, ob eine Analyse notwendig ist, nicht jedes Bild wird extrahiert), mindestens Qwen2.5-VL-7B-Instruct erforderlich

### 🚀  Los geht's!

- für MacOS/Linux:

```bash
cd wiseflow
uv venv # nur beim ersten Mal erforderlich
uv sync # nur beim ersten Mal erforderlich
python -m playwright install --with-deps chromium # nur beim ersten Mal erforderlich
chmod +x run.sh # nur beim ersten Mal erforderlich
./run.sh
```

- für Windows:

```bash
cd wiseflow
uv venv # nur beim ersten Mal erforderlich
uv sync # nur beim ersten Mal erforderlich
python -m playwright install --with-deps chromium # nur beim ersten Mal erforderlich
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser # nur beim ersten Mal erforderlich
.\run.ps1
```

✨ **So einfach ist das!** Das Startskript führt automatisch folgende Aufgaben aus:
- ✅ Überprüft die Umgebungskonfiguration
- ✅ Synchronisiert die Projektabhängigkeiten
- ✅ Aktiviert die virtuelle Umgebung
- ✅ Startet die PocketBase-Datenbank
- ✅ Führt die WiseFlow-Anwendung aus

Das Programm führt zunächst einen Crawling-Durchlauf für alle aktivierten Quellen (activated auf true gesetzt) durch und führt dann periodisch im Stundentakt entsprechend der eingestellten Frequenz aus.

⚠️ **Hinweis:** Wenn Sie den Prozess mit `Ctrl+C` beenden, wird der PocketBase-Prozess möglicherweise nicht automatisch beendet und muss manuell geschlossen oder der Terminal neu gestartet werden.

### 📝 Manuelle Installation (optional)

Wenn Sie jeden Schritt manuell kontrollieren möchten, können Sie auch folgende Schritte ausführen:

#### 1. Führen Sie das install_pocketbase-Skript im Stammverzeichnis aus

Linux/macos-Benutzer führen bitte aus:

```bash
chmod +x install_pocketbase.sh
./install_pocketbase.sh
```

**Windows-Benutzer führen bitte aus:**
```powershell
.\install_pocketbase.ps1
```

#### 2. Virtuelle Umgebung erstellen und aktivieren

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# oder unter Windows:
# .venv\Scripts\activate
```

##### 4.2 Abhängigkeiten installieren

```bash
uv sync
```

Dies installiert wiseflow und alle seine Abhängigkeiten und stellt die Konsistenz der Abhängigkeitsversionen sicher. uv sync liest die Abhängigkeitsdeklarationen des Projekts und synchronisiert die virtuelle Umgebung.

Dann Browser-Abhängigkeiten installieren:

```bash
python -m playwright install --with-deps chromium
```

Schließlich den Hauptdienst starten:

```bash
python core/run_task.py
# oder unter Windows:
# python core\run_task.py
```

Wenn Sie die PocketBase-Benutzeroberfläche benötigen, starten Sie den PocketBase-Dienst:

```bash
cd wiseflow/pb
./pocketbase serve
```

oder unter Windows:

```powershell
cd wiseflow\pb
.\pocketbase.exe serve
```

### 🔧 Umgebungsvariablen konfigurieren

Sowohl für den schnellen Start als auch für die manuelle Installation müssen Sie die env_sample-Datei als Referenz verwenden und eine .env-Datei erstellen:

#### 1. LLM-bezogene Konfiguration

wiseflow ist eine LLM-native Anwendung. Bitte stellen Sie sicher, dass Sie dem Programm einen stabilen LLM-Dienst zur Verfügung stellen.

🌟 **wiseflow schränkt die Modellserviceanbieter nicht ein, solange der Dienst mit dem OpenAI SDK kompatibel ist, einschließlich lokal bereitgestellter Dienste wie ollama, Xinference usw.**

##### Empfehlung 1: Verwendung des MaaS-Dienstes von SiliconFlow

SiliconFlow bietet MaaS-Dienste für die meisten gängigen Open-Source-Modelle an. Dank ihrer eigenen Beschleunigungstechnologie für Inferenz haben sie große Vorteile in Bezug auf Geschwindigkeit und Preis. Bei Verwendung des SiliconFlow-Dienstes kann die .env-Konfiguration wie folgt aussehen:

```
LLM_API_KEY=Ihr_API_Schlüssel
LLM_API_BASE="https://api.siliconflow.com/v1"
PRIMARY_MODEL="Qwen3-14B"
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
CONCURRENT_NUMBER=8
```
      
😄 Wenn Sie möchten, können Sie meinen [SiliconFlow-Einladungslink](https://cloud.siliconflow.com/i/WNLYbBpi) verwenden, damit ich mehr Token-Belohnungen erhalten kann 🌹

##### Empfehlung 2: Verwendung von AiHubMix als Proxy für OpenAI, Claude, Gemini und andere kommerzielle Modelle

Wenn Ihre Informationsquellen hauptsächlich nicht-chinesische Seiten sind und Sie auch nicht verlangen, dass die extrahierten Informationen auf Chinesisch sind, empfehlen wir die Verwendung von OpenAI, Claude, Gemini und anderen kommerziellen Modellen. Sie können den Drittanbieter-Proxy **AiHubMix** ausprobieren, der direkte Verbindungen in chinesischen Netzwerken, bequeme Zahlungen über Alipay unterstützt und das Risiko von Kontosperrungen vermeidet.
Bei Verwendung von AiHubMix-Modellen kann die .env-Konfiguration wie folgt aussehen:

```
LLM_API_KEY=Ihr_API_Schlüssel
LLM_API_BASE="https://aihubmix.com/v1" # siehe https://doc.aihubmix.com/
PRIMARY_MODEL="gpt-4o-mini"
VL_MODEL="gpt-4o"
CONCURRENT_NUMBER=8
```

😄 Willkommen zur Registrierung über den [AiHubMix-Einladungslink](https://aihubmix.com?aff=Gp54) 🌹

##### Lokale Bereitstellung des LLM-Dienstes

Am Beispiel von Xinference kann die .env-Konfiguration wie folgt aussehen:

```
# LLM_API_KEY='' nicht erforderlich für lokale Dienste, bitte auskommentieren oder löschen
LLM_API_BASE='http://127.0.0.1:9997' # 'http://127.0.0.1:11434/v1' für ollama
PRIMARY_MODEL=gestartete Modell-ID
VL_MODEL=gestartete Modell-ID
CONCURRENT_NUMBER=1 # basierend auf tatsächlichen Hardware-Ressourcen
```

#### 3. JINA_API_KEY-Einstellung (für Suchmaschinendienst)

Auf https://jina.ai/ erhältlich, derzeit ohne Registrierung verfügbar. (Bei hohem Datenverkehr oder kommerzieller Nutzung bitte nach Aufladung verwenden)

```
JINA_API_KEY=Ihr_API_Schlüssel
```

#### 4. Andere optionale Konfigurationen

Die folgenden sind optionale Konfigurationen:
- #VERBOSE="true" 

  Ob der Beobachtungsmodus aktiviert werden soll. Wenn aktiviert, werden Debug-Informationen in der Logger-Datei aufgezeichnet (standardmäßig nur in der Konsole ausgegeben)

- #CONCURRENT_NUMBER=8 

  Steuert die Anzahl der gleichzeitigen LLM-Anfragen, standardmäßig 1 wenn nicht festgelegt (bitte stellen Sie sicher, dass der LLM-Anbieter die festgelegte Parallelität unterstützt, bei lokalen LLMs mit Vorsicht verwenden, es sei denn, Sie sind sich Ihrer Hardware-Basis sicher)

## 🐳 Docker-Bereitstellung

Das Docker-Bereitstellungsschema für Version 4.x wird später folgen. Wir hoffen auch auf PR-Beiträge von interessierten Entwicklern~

## 🌹 Bezahlte Dienste

Open Source ist nicht einfach ☺️ Die Dokumentation und Beratung kostet viel Zeit. Wenn Sie bereit sind, Unterstützung zu leisten, bieten wir bessere Dienstleistungen an~

- Detailliertes Tutorial-Video + 3 E-Mail-Beratungen: ￥12.88
- Detailliertes Tutorial-Video + 3 E-Mail-Beratungen + Beitritt zur bezahlten Benutzergruppe: ￥19.88

*Hinweis: In der bezahlten Benutzergruppe wird keine Beratung angeboten, sie dient nur dem Austausch von Produktanforderungen und Nutzungserfahrungen. Bei zukünftigen Iterationen werden die häufigen Anforderungen der bezahlten Benutzergruppe priorisiert, und Systemoptimierungen werden hauptsächlich für die Fälle in der bezahlten Benutzergruppe durchgeführt*

Zahlungsmethode: Scannen Sie den folgenden Zahlungscode und geben Sie Ihre E-Mail-Adresse im Kommentar an. Wir werden uns innerhalb von 24 Stunden mit Ihnen in Verbindung setzen und den Service bereitstellen.

<img src="alipay.png" alt="Alipay Zahlungscode" width="300">      <img src="weixinpay.jpg" alt="WeChat Zahlungscode" width="300"> 