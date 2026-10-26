import Foundation
import Cocoa

class CheatManager: ObservableObject {
    @Published var cheats: [Cheat] = []
    @Published var isRunning: Bool = false
    @Published var activeCheatsCount: Int = 0
    @Published var appVersion: String = "2.0.0"
    @Published var lastUpdateCheck: Date = Date()
    @Published var statusMessage: String = "Ready"

    private let configPath: String
    private var statusTimer: Timer?
    private var engineProcess: Process?
    private var hotkeyMonitor: Any?
    private weak var window: NSWindow?

    init() {
        self.configPath = "\(NSHomeDirectory())/.idle_slayer_cheat/cheats.json"
        loadCheats()
        loadState()
        startStatusMonitoring()
        setupGlobalHotkey()
    }

    func setWindow(_ window: NSWindow) {
        self.window = window
    }

    private func loadCheats() {
        cheats = [
            Cheat(id: "autofarm_coins", name: "AutoFarm Coins", desc: "Farm coins only"),
            Cheat(id: "autofarm_slayer", name: "AutoFarm Slayer", desc: "Farm slayer points"),
            Cheat(id: "autofarm_quest_temp", name: "Auto Temp Quests", desc: "Complete temp quests"),
            Cheat(id: "autofarm_quest_normal", name: "Auto Normal Quests", desc: "Complete normal quests"),
            Cheat(id: "autofarm_quest_event", name: "Auto Event Quests", desc: "Complete event quests"),
            Cheat(id: "auto_ascend", name: "Auto Ascend", desc: "Ascend at 25%"),
            Cheat(id: "auto_minions", name: "Auto Minions", desc: "Start minions"),
            Cheat(id: "auto_upgrades_1", name: "Budget Upgrades", desc: "Cost-effective"),
            Cheat(id: "auto_upgrades_2", name: "All Upgrades", desc: "Buy everything"),
            Cheat(id: "auto_craft", name: "Auto Craft", desc: "Craft items"),
            Cheat(id: "auto_ads", name: "Auto Ads", desc: "Watch ads"),
            Cheat(id: "auto_rage", name: "Rage Automation", desc: "Megahorde trigger"),
            Cheat(id: "quest_router", name: "Quest Router", desc: "Smart routing"),
            Cheat(id: "gear_craft_ai", name: "Gear Craft AI", desc: "AI crafting"),
            Cheat(id: "bonus_stage", name: "Bonus Stages", desc: "Auto-run stages"),
            Cheat(id: "chest_hunt_solver", name: "Chest Hunt AI", desc: "Minigame AI"),
            Cheat(id: "ua_planner", name: "UA Planner", desc: "Ascension plan"),
            Cheat(id: "minigame_runner", name: "Minigame Runner", desc: "Pattern runner"),
        ]
    }

    private func loadState() {
        guard let data = try? Data(contentsOf: URL(fileURLWithPath: configPath)),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Bool] else {
            return
        }

        for i in cheats.indices {
            cheats[i].enabled = json[cheats[i].id] ?? false
        }
        updateActiveCount()
    }

    private func saveState() {
        let fileManager = FileManager.default
        let dirPath = "\(NSHomeDirectory())/.idle_slayer_cheat"

        try? fileManager.createDirectory(atPath: dirPath, withIntermediateDirectories: true)

        var state: [String: Bool] = [:]
        for cheat in cheats {
            state[cheat.id] = cheat.enabled
        }

        if let data = try? JSONSerialization.data(withJSONObject: state),
           let _ = try? data.write(to: URL(fileURLWithPath: configPath)) {
        }
    }

    func toggleCheat(_ id: String) {
        if let index = cheats.firstIndex(where: { $0.id == id }) {
            let newState = !cheats[index].enabled
            cheats[index].enabled = newState

            // Save to disk immediately
            saveState()
            updateActiveCount()

            print("[CheatManager] Toggled \(id) → \(newState ? "ON" : "OFF")")

            // If engine running, sync with Python engine
            if isRunning {
                syncCheatState(id: id, enabled: newState)
            }
        }
    }

    private func syncCheatState(id: String, enabled: Bool) {
        let pythonCode = """
        import sys
        sys.path.insert(0, '\(NSHomeDirectory())/.idle_slayer_cheat')
        try:
            from is_engine.core import engine, CheatMode
            mode = CheatMode('\(id)')
            current = engine.state.active_cheats.get(mode, False)
            target = \(enabled ? "True" : "False")
            if current != target:
                engine.state.toggle_cheat(mode)
        except Exception as e:
            print(f"Sync error: {e}")
        """

        DispatchQueue.global().async {
            let process = Process()
            process.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
            process.arguments = ["-c", pythonCode]
            try? process.run()
            process.waitUntilExit()
        }
    }

    func start() {
        DispatchQueue.global().async {
            self.startEngine()
            DispatchQueue.main.async {
                self.isRunning = true
                self.statusMessage = "Running - \(self.activeCheatsCount) cheats active"
            }
        }
    }

    func stop() {
        DispatchQueue.global().async {
            self.stopEngine()
            DispatchQueue.main.async {
                self.isRunning = false
                self.statusMessage = "Stopped"
            }
        }
    }

    // Setup global hotkey for ⌘ + M
    private func setupGlobalHotkey() {
        DispatchQueue.main.async {
            NSEvent.addGlobalMonitorForEvents(matching: .keyDown) { [weak self] event in
                // ⌘ + M: command key + M
                if event.modifierFlags.contains(.command) && event.characters?.lowercased() == "m" {
                    self?.toggleMenuVisibility()
                }
            }
        }
    }

    private func toggleMenuVisibility() {
        DispatchQueue.main.async {
            if let window = self.window {
                if window.isVisible && window.isKeyWindow {
                    window.orderOut(nil)
                } else {
                    NSApplication.shared.activate(ignoringOtherApps: true)
                    window.makeKeyAndOrderFront(nil)
                }
            }
        }
    }

    private func startEngine() {
        stopEngine()

        engineProcess = Process()
        engineProcess?.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        engineProcess?.arguments = [
            "-u",
            "-m",
            "is_engine.launcher"
        ]

        // Set working directory to the engine folder
        engineProcess?.currentDirectoryURL = URL(fileURLWithPath: "\(NSHomeDirectory())/.idle_slayer_cheat")

        let pipe = Pipe()
        engineProcess?.standardOutput = pipe
        engineProcess?.standardError = pipe

        try? engineProcess?.run()
        print("[CheatManager] Python engine process started (PID: \(engineProcess?.processIdentifier ?? -1))")
        print("[CheatManager] Launcher: is_engine.launcher with proper handler registration")

        // Log output in background
        DispatchQueue.global().async {
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            if let output = String(data: data, encoding: .utf8) {
                print("[Engine Output]:\n\(output)")
            }
        }
    }

    private func stopEngine() {
        if let process = engineProcess, process.isRunning {
            process.terminate()
            process.waitUntilExit()
            engineProcess = nil
            print("[CheatManager] Python engine process stopped")
        }
    }

    private func updateEngineState() {
        guard isRunning else { return }

        let enabledCheats = cheats.filter { $0.enabled }.map { $0.id }.joined(separator: ",")

        let pythonCode = """
        import sys
        sys.path.insert(0, '\(NSHomeDirectory())/.idle_slayer_cheat')
        try:
            from is_engine.core import engine, CheatMode
            enabled = '\(enabledCheats)'.split(',') if '\(enabledCheats)' else []
            for cheat_id in enabled:
                try:
                    mode = CheatMode(cheat_id)
                    if mode not in engine.state.active_cheats or not engine.state.active_cheats[mode]:
                        engine.state.toggle_cheat(mode)
                except:
                    pass
        except:
            pass
        """

        DispatchQueue.global().async {
            let process = Process()
            process.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
            process.arguments = ["-c", pythonCode]
            try? process.run()
            process.waitUntilExit()
        }
    }

    private func startStatusMonitoring() {
        statusTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { _ in
            self.updateStatus()
        }
    }

    private func updateStatus() {
        let pythonCode = """
        import sys
        import json
        sys.path.insert(0, '\(NSHomeDirectory())/.idle_slayer_cheat')
        try:
            from is_engine.core import engine
            active = len([c for c in engine.state.active_cheats.values() if c])
            print(json.dumps({
                'running': engine.running,
                'active_count': active
            }))
        except:
            print(json.dumps({'running': False, 'active_count': 0}))
        """

        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        process.arguments = ["-c", pythonCode]

        let pipe = Pipe()
        process.standardOutput = pipe

        try? process.run()
        process.waitUntilExit()

        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        if let output = String(data: data, encoding: .utf8),
           let jsonData = output.data(using: .utf8),
           let json = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any] {
            DispatchQueue.main.async {
                self.isRunning = json["running"] as? Bool ?? false
            }
        }
    }

    private func updateActiveCount() {
        activeCheatsCount = cheats.filter { $0.enabled }.count
    }

    deinit {
        statusTimer?.invalidate()
        stopEngine()
        if let monitor = hotkeyMonitor {
            NSEvent.removeMonitor(monitor)
        }
    }
}

struct Cheat: Identifiable {
    let id: String
    let name: String
    let desc: String
    var enabled: Bool = false
}
