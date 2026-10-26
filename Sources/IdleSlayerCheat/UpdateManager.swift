import Foundation
import Cocoa

class UpdateManager: ObservableObject {
    @Published var hasUpdate = false
    @Published var updateVersion = ""
    @Published var updateProgress: Double = 0
    @Published var isChecking = false
    @Published var updateMessage = ""

    private let appVersion = "2.4.2"
    private let repoOwner = "6nmsb4mvzs-ui"
    private let repoName = "is"

    func checkForUpdates() {
        isChecking = true
        updateMessage = "Checking for updates..."

        DispatchQueue.global().async {
            let urlString = "https://api.github.com/repos/\(self.repoOwner)/\(self.repoName)/releases/latest"
            guard let url = URL(string: urlString) else {
                DispatchQueue.main.async {
                    self.isChecking = false
                }
                return
            }

            var request = URLRequest(url: url)
            request.setValue("application/vnd.github.v3+json", forHTTPHeaderField: "Accept")

            let task = URLSession.shared.dataTask(with: request) { data, response, error in
                DispatchQueue.main.async {
                    self.isChecking = false

                    guard let data = data, error == nil,
                          let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                        self.updateMessage = "Failed to check updates"
                        return
                    }

                    if let tagName = json["tag_name"] as? String {
                        let version = tagName.replacingOccurrences(of: "v", with: "")
                        if self.isNewerVersion(version) {
                            self.updateVersion = version
                            self.hasUpdate = true
                            self.updateMessage = "Update available: v\(version)"
                        } else {
                            self.updateMessage = "Already up to date"
                        }
                    }
                }
            }
            task.resume()
        }
    }

    func installUpdate() {
        updateMessage = "Downloading update..."
        updateProgress = 0

        let urlString = "https://github.com/\(repoOwner)/\(repoName)/releases/download/v\(updateVersion)/Idle_Slayer_Cheat-v\(updateVersion).zip"

        guard let url = URL(string: urlString) else {
            updateMessage = "Invalid download URL"
            return
        }

        let downloadTask = URLSession.shared.downloadTask(with: url) { [weak self] tempURL, response, error in
            guard let self = self, let tempURL = tempURL, error == nil else {
                DispatchQueue.main.async {
                    self?.updateMessage = "Download failed"
                }
                return
            }

            DispatchQueue.main.async {
                self.updateMessage = "Installing update..."
                self.extractAndInstall(tempURL)
            }
        }

        downloadTask.resume()
    }

    private func extractAndInstall(_ zipPath: URL) {
        DispatchQueue.global().async {
            let tempDir = FileManager.default.temporaryDirectory
            let extractDir = tempDir.appendingPathComponent(UUID().uuidString)

            do {
                try FileManager.default.createDirectory(at: extractDir, withIntermediateDirectories: true)

                let process = Process()
                process.executableURL = URL(fileURLWithPath: "/usr/bin/unzip")
                process.arguments = ["-q", zipPath.path, "-d", extractDir.path]
                try process.run()
                process.waitUntilExit()

                // Find the .app bundle
                let contents = try FileManager.default.contentsOfDirectory(atPath: extractDir.path)
                guard let appFolder = contents.first(where: { $0.contains("is_engine_swift") || $0.hasSuffix(".app") }) else {
                    throw NSError(domain: "No app found", code: -1)
                }

                let newAppPath = extractDir.appendingPathComponent(appFolder)
                let installPath = FileManager.default.homeDirectoryForCurrentUser
                    .appendingPathComponent("Applications")
                    .appendingPathComponent("Idle_Slayer_Cheat.app")

                // Remove old app
                try? FileManager.default.removeItem(at: installPath)

                // Move new app
                try FileManager.default.moveItem(at: newAppPath, to: installPath)

                DispatchQueue.main.async {
                    self.updateMessage = "Update installed! Relaunching..."
                    self.hasUpdate = false

                    // Relaunch
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                        self.relaunchApp(at: installPath)
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.updateMessage = "Installation failed: \(error.localizedDescription)"
                }
            }
        }
    }

    private func relaunchApp(at path: URL) {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/open")
        process.arguments = [path.path]
        try? process.run()

        NSApplication.shared.terminate(nil)
    }

    private func isNewerVersion(_ newVersion: String) -> Bool {
        let current = appVersion.split(separator: ".").compactMap { Int($0) }
        let new = newVersion.split(separator: ".").compactMap { Int($0) }

        for (c, n) in zip(current, new) {
            if n > c { return true }
            if n < c { return false }
        }

        return new.count > current.count
    }
}
