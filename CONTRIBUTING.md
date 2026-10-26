# Contributing

This is a personal project for testing and educational purposes. Contributions and pull requests are not accepted, and the tool is not intended for distribution to the Idle Slayer community.

## Development Setup

If you want to modify the code locally:

1. **Install Xcode Command Line Tools**
   ```bash
   xcode-select --install
   ```

2. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd is_engine_swift
   ```

3. **Build locally**
   ```bash
   swift build
   ```

4. **Run tests** (if any)
   ```bash
   swift test
   ```

5. **Run the app** (development)
   ```bash
   swift run IdleSlayerCheat
   ```

## Project Structure

```
is_engine_swift/
├── Sources/
│   └── IdleSlayerCheat/
│       ├── IdleSlayerCheatApp.swift    # Main app entry
│       ├── ContentView.swift           # UI (Cheats + Settings tabs)
│       └── CheatManager.swift          # State & engine management
├── is_engine/                          # Python automation code
│   ├── core.py                         # CheatMode enum, AutomationEngine
│   ├── cheats.py                       # 18 cheat implementations
│   ├── chest_hunt_ai.py                # Minigame solver
│   └── ...
├── Package.swift                       # Swift package manifest
├── run.command                         # One-click installer
└── README.md
```

## Building for Release

1. **Update version** in `ContentView.swift` and `CheatManager.swift`
2. **Build release binary**
   ```bash
   swift build -c release
   ```
3. **Tag and push**
   ```bash
   git tag -a v2.0.1 -m "Release v2.0.1"
   git push origin v2.0.1
   ```
4. GitHub Actions will automatically build and create a release

## Code Style

- Swift: Follow Swift API Design Guidelines
- Python: PEP 8
- Comments: Explain *why*, not *what*
- No large PRs - keep changes focused

## Personal Use Only

This tool is for your personal testing and educational purposes. Do not:
- Share with others
- Distribute to the Idle Slayer community
- Use for commercial purposes
- Modify the license or attribution

---

Questions? Check the README first.
