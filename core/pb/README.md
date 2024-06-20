download https://pocketbase.io/docs/

```bash
cd pb
xattr -d com.apple.quarantine pocketbase # for Macos
./pocketbase migrate up # for first run
./pocketbase --dev admin create test@example.com 123467890 # If you don't have an initial account, please use this command to create it
./pocketbase serve
```