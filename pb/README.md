download https://github.com/pocketbase/pocketbase/releases/download/v0.23.4/

```bash
cd pb
xattr -d com.apple.quarantine pocketbase # for Macos
./pocketbase migrate up # for first run
./pocketbase --dev admin create test@example.com 1234567890 # If you don't have an initial account, please use this command to create it
./pocketbase serve
```