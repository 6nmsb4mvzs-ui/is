import SwiftUI

@main
struct IdleSlayerCheatApp: App {
    @StateObject var cheatManager = CheatManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(cheatManager)
                .frame(minWidth: 600, minHeight: 700)
                .onReceive(NotificationCenter.default.publisher(for: NSWindow.didBecomeMainNotification)) { notification in
                    if let window = notification.object as? NSWindow {
                        cheatManager.setWindow(window)
                    }
                }
        }
        .windowStyle(.hiddenTitleBar)
        .commands {
            CommandGroup(replacing: .appSettings) {
                Button("Quit") {
                    NSApplication.shared.terminate(nil)
                }
                .keyboardShortcut("q", modifiers: .command)
            }
        }
    }
}
