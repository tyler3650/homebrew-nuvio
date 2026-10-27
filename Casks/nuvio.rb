cask "nuvio" do
  arch arm: "arm64", intel: "x86_64"

  version "0.1.33-alpha"
  sha256 arm:   "2dcab2bf5cb84274b6b677ff92348951696d526470b80b59f6d9077eb298724a",
         intel: "a89237c978efb593258ba3b32c38d2a99e101e5242fd4e8975e76efafd61b6e0"

  url "https://github.com/NuvioMedia/NuvioDesktop/releases/download/#{version}/Nuvio-macOS-#{arch}-#{version}.dmg"
  name "Nuvio Desktop"
  desc "Free, open-source media app"
  homepage "https://nuvio.tv/"

  livecheck do
    url :url
    regex(/^v?(\d+(?:\.\d+)+(?:-[a-z0-9.]+)?)$/i)
    strategy :github_latest
  end

  depends_on :macos

  app "Nuvio.app"

  postflight_steps do
    # The upstream app is ad-hoc signed but not notarized.
    run "/usr/bin/xattr",
        args: ["-dr", "com.apple.quarantine", "{{appdir}}/Nuvio.app"]
  end

  zap trash: [
    "/private/var/folders/nz/nxxfvw7x6vjchgyr76bscbq80000gn/C/com.nuvio.media.desktop",
    "~/Library/Application Support/Nuvio",
    "~/Library/Caches/com.nuvio.media.desktop",
    "~/Library/Caches/Nuvio",
    "~/Library/HTTPStorages/com.nuvio.media.desktop",
    "~/Library/WebKit/com.nuvio.media.desktop",
  ]
end
