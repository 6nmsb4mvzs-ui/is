import SwiftUI

struct ContentView: View {
    @EnvironmentObject var manager: CheatManager
    @StateObject private var updateManager = UpdateManager()
    @State private var searchText = ""
    @State private var selectedTab = 0

    var filteredCheats: [Cheat] {
        if searchText.isEmpty {
            return manager.cheats
        }
        return manager.cheats.filter {
            $0.name.localizedCaseInsensitiveContains(searchText) ||
            $0.desc.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        ZStack {
            // Background
            LinearGradient(
                gradient: Gradient(colors: [
                    Color(red: 0.05, green: 0.05, blue: 0.15),
                    Color(red: 0.08, green: 0.08, blue: 0.2)
                ]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 0) {
                // Header
                VStack(spacing: 8) {
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("⚔️ IDLE SLAYER CHEATS")
                                .font(.system(size: 22, weight: .bold))
                                .foregroundColor(Color(red: 0, green: 0.83, blue: 1))

                            HStack(spacing: 20) {
                                HStack(spacing: 6) {
                                    Circle()
                                        .fill(manager.isRunning ? Color(red: 0, green: 0.8, blue: 0) : Color(red: 0.9, green: 0.2, blue: 0.2))
                                        .frame(width: 8, height: 8)
                                    Text(manager.isRunning ? "RUNNING" : "STOPPED")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.gray)
                                }

                                HStack(spacing: 6) {
                                    Text("Active:")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.gray)
                                    Text("\(manager.activeCheatsCount) / 18")
                                        .font(.system(size: 12, weight: .bold))
                                        .foregroundColor(Color(red: 0, green: 0.83, blue: 1))
                                }
                            }
                        }
                        Spacer()
                    }
                    .padding(16)
                }
                .background(Color(red: 0.1, green: 0.1, blue: 0.25))
                .overlay(
                    Rectangle()
                        .frame(height: 1)
                        .foregroundColor(Color(red: 0, green: 0.83, blue: 1))
                        .opacity(0.5),
                    alignment: .bottom
                )

                // Tabs
                HStack(spacing: 0) {
                    TabButton(label: "Cheats", isSelected: selectedTab == 0) {
                        selectedTab = 0
                    }
                    TabButton(label: "Settings", isSelected: selectedTab == 1) {
                        selectedTab = 1
                    }
                    TabButton(label: "Updates", isSelected: selectedTab == 2) {
                        selectedTab = 2
                    }
                }
                .background(Color(red: 0.08, green: 0.08, blue: 0.18))

                // Tab Content
                if selectedTab == 0 {
                    cheatsTabContent
                } else if selectedTab == 1 {
                    settingsTabContent
                } else {
                    updatesTabContent
                }
            }
        }
    }

    var cheatsTabContent: some View {
        VStack(spacing: 0) {
            // Search
            HStack(spacing: 8) {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.gray)

                TextField("Search cheats...", text: $searchText)
                    .textFieldStyle(.roundedBorder)
                    .background(Color(red: 0.12, green: 0.12, blue: 0.22))
                    .foregroundColor(.white)
            }
            .padding(12)
            .background(Color(red: 0.08, green: 0.08, blue: 0.18))

            // Cheats List
            ScrollView {
                VStack(spacing: 8) {
                    ForEach(filteredCheats) { cheat in
                        CheatRow(cheat: cheat)
                            .onTapGesture {
                                manager.toggleCheat(cheat.id)
                            }
                    }
                }
                .padding(12)
            }

            Divider()
                .background(Color(red: 0, green: 0.83, blue: 1).opacity(0.3))

            // Toggle Button
            Button(action: manager.toggleEngine) {
                HStack(spacing: 8) {
                    Image(systemName: manager.isRunning ? "stop.fill" : "play.fill")
                    Text(manager.isRunning ? "STOP" : "START")
                }
                .frame(maxWidth: .infinity)
                .padding(14)
                .background(
                    LinearGradient(
                        gradient: Gradient(colors: [
                            manager.isRunning ?
                                Color(red: 1, green: 0.2, blue: 0.2) :
                                Color(red: 0, green: 0.8, blue: 0),
                            manager.isRunning ?
                                Color(red: 0.7, green: 0, blue: 0) :
                                Color(red: 0, green: 0.6, blue: 0)
                        ]),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .foregroundColor(manager.isRunning ? .white : .black)
                .font(.system(size: 14, weight: .bold))
                .cornerRadius(6)
            }
            .padding(12)
            .background(Color(red: 0.08, green: 0.08, blue: 0.18))
        }
    }

    var settingsTabContent: some View {
        ScrollView {
            VStack(spacing: 12) {
                // Version
                SettingItem(
                    label: "App Version",
                    value: manager.appVersion
                )

                // Status
                SettingItem(
                    label: "Engine Status",
                    value: manager.isRunning ? "Running" : "Stopped",
                    valueColor: manager.isRunning ? Color(red: 0, green: 0.8, blue: 0) : Color(red: 1, green: 0.3, blue: 0.3)
                )

                // Last Update
                SettingItem(
                    label: "Last Checked",
                    value: formatDate(manager.lastUpdateCheck)
                )

                // Info Box
                VStack(alignment: .leading, spacing: 8) {
                    Text("About")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundColor(Color(red: 0, green: 0.83, blue: 1))

                    VStack(alignment: .leading, spacing: 4) {
                        Text("Idle Slayer Cheat Engine v2.0")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.white)

                        Text("Native macOS app with 18 cheats for Idle Slayer automation")
                            .font(.system(size: 10))
                            .foregroundColor(.gray)
                            .lineLimit(3)
                    }
                }
                .padding(12)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color(red: 0.1, green: 0.1, blue: 0.2))
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color(red: 0, green: 0.83, blue: 1).opacity(0.3), lineWidth: 1)
                        )
                )

                // Config Path
                VStack(alignment: .leading, spacing: 6) {
                    Text("Config Location")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundColor(Color(red: 0, green: 0.83, blue: 1))

                    Text("~/.idle_slayer_cheat/")
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundColor(.gray)
                        .lineLimit(1)
                        .truncationMode(.tail)
                }
                .padding(12)
                .background(Color(red: 0.1, green: 0.1, blue: 0.2))
                .cornerRadius(6)

                Spacer()
            }
            .padding(12)
        }
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }

    var updatesTabContent: some View {
        ScrollView {
            VStack(spacing: 12) {
                // Update Status
                VStack(spacing: 8) {
                    if updateManager.hasUpdate {
                        HStack(spacing: 12) {
                            Image(systemName: "arrow.down.circle.fill")
                                .font(.system(size: 20))
                                .foregroundColor(Color(red: 1, green: 0.6, blue: 0))

                            VStack(alignment: .leading, spacing: 4) {
                                Text("Update Available")
                                    .font(.system(size: 13, weight: .bold))
                                    .foregroundColor(.white)
                                Text("v\(updateManager.updateVersion)")
                                    .font(.system(size: 12))
                                    .foregroundColor(Color(red: 1, green: 0.6, blue: 0))
                            }

                            Spacer()

                            Button(action: {
                                updateManager.installUpdate()
                            }) {
                                Text("INSTALL")
                                    .font(.system(size: 11, weight: .bold))
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color(red: 1, green: 0.6, blue: 0))
                                    .foregroundColor(.black)
                                    .cornerRadius(4)
                            }
                        }
                    } else if updateManager.isChecking {
                        HStack(spacing: 8) {
                            ProgressView()
                                .scaleEffect(0.8)
                            Text("Checking for updates...")
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                        }
                    } else {
                        HStack(spacing: 8) {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(Color(red: 0, green: 0.8, blue: 0))
                            Text("Up to date")
                                .font(.system(size: 12))
                                .foregroundColor(Color(red: 0, green: 0.8, blue: 0))
                        }
                    }
                }
                .padding(12)
                .background(Color(red: 0.1, green: 0.1, blue: 0.2))
                .cornerRadius(6)

                // Status Message
                if !updateManager.updateMessage.isEmpty && !updateManager.isChecking && !updateManager.hasUpdate {
                    Text(updateManager.updateMessage)
                        .font(.system(size: 11))
                        .foregroundColor(.gray)
                        .padding(.horizontal, 12)
                }

                // Check for Updates Button
                Button(action: {
                    updateManager.checkForUpdates()
                }) {
                    Text("Check for Updates")
                        .frame(maxWidth: .infinity)
                        .padding(12)
                        .background(Color(red: 0, green: 0.83, blue: 1).opacity(0.2))
                        .foregroundColor(Color(red: 0, green: 0.83, blue: 1))
                        .cornerRadius(6)
                }
                .disabled(updateManager.isChecking)
                .padding(.horizontal, 12)

                // Auto-Update Info
                VStack(alignment: .leading, spacing: 8) {
                    Text("Auto-Update")
                        .font(.system(size: 12, weight: .bold))
                        .foregroundColor(Color(red: 0, green: 0.83, blue: 1))

                    VStack(alignment: .leading, spacing: 4) {
                        Text("✓ Checks on startup")
                            .font(.system(size: 11))
                            .foregroundColor(.gray)
                        Text("✓ Downloads from GitHub")
                            .font(.system(size: 11))
                            .foregroundColor(.gray)
                        Text("✓ Installs automatically")
                            .font(.system(size: 11))
                            .foregroundColor(.gray)
                    }
                }
                .padding(12)
                .background(Color(red: 0.1, green: 0.1, blue: 0.2))
                .cornerRadius(6)

                Spacer()
            }
            .padding(12)
        }
        .onAppear {
            updateManager.checkForUpdates()
        }
    }
}

struct TabButton: View {
    let label: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 0) {
                Text(label)
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(isSelected ? Color(red: 0, green: 0.83, blue: 1) : .gray)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)

                if isSelected {
                    Rectangle()
                        .fill(Color(red: 0, green: 0.83, blue: 1))
                        .frame(height: 2)
                }
            }
        }
        .background(isSelected ? Color(red: 0.1, green: 0.1, blue: 0.25) : Color(red: 0.08, green: 0.08, blue: 0.18))
    }
}

struct SettingItem: View {
    let label: String
    let value: String
    var valueColor: Color = Color(red: 0, green: 0.83, blue: 1)

    var body: some View {
        HStack {
            Text(label)
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.gray)

            Spacer()

            Text(value)
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(valueColor)
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(Color(red: 0.1, green: 0.1, blue: 0.2))
                .overlay(
                    RoundedRectangle(cornerRadius: 6)
                        .stroke(Color(red: 0, green: 0.83, blue: 1).opacity(0.2), lineWidth: 1)
                )
        )
    }
}

struct CheatRow: View {
    let cheat: Cheat

    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(cheat.name)
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(Color(red: 0, green: 0.83, blue: 1))

                Text(cheat.desc)
                    .font(.system(size: 11, weight: .regular))
                    .foregroundColor(.gray)
                    .lineLimit(1)
            }

            Spacer()

            Toggle("", isOn: .constant(cheat.enabled))
                .toggleStyle(SwitchToggleStyle(tint: Color(red: 0, green: 0.8, blue: 0)))
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(cheat.enabled ?
                    Color(red: 0, green: 0.3, blue: 0.1).opacity(0.4) :
                    Color(red: 0.1, green: 0.1, blue: 0.2)
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(
                            Color(red: 0, green: 0.83, blue: 1).opacity(cheat.enabled ? 0.8 : 0.3),
                            lineWidth: 1
                        )
                )
        )
        .contentShape(Rectangle())
    }
}
