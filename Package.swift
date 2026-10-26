// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "IdleSlayerCheat",
    platforms: [
        .macOS(.v13)
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "IdleSlayerCheat",
            dependencies: [],
            path: "Sources/IdleSlayerCheat"
        )
    ]
)
