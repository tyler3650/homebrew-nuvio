cask "nuvio" do
  arch arm: "arm64", intel: "x86_64"

  version "0.1.30-alpha"
  sha256 :no_check

  url "https://github.com/NuvioMedia/NuvioDesktop/releases/download/#{version}/Nuvio-macOS-#{arch}-#{version}.dmg"
  name "Nuvio Desktop"
  desc "Nuvio Desktop is a media client for browsing metadata, managing collections and watch progress, downloading media, and playing streams from user-installed extensions or user-provided sources."
  homepage "https://nuvio.tv/"

  app "Nuvio.app"

  zap trash: [
    "~/Library/Application Support/Nuvio",
    "~/Library/Caches/com.nuvio.media.desktop",
    "~/Library/Caches/Nuvio",
    "~/Library/HTTPStorages/com.nuvio.media.desktop",
    "~/Library/WebKit/com.nuvio.media.desktop",
    "/private/var/folders/nz/nxxfvw7x6vjchgyr76bscbq80000gn/C/com.nuvio.media.desktop",
  ]

  postflight_steps do
    # The upstream app is ad-hoc signed but not notarized.
    run "/usr/bin/xattr",
        args: ["-dr", "com.apple.quarantine", "{{appdir}}/Nuvio.app"]
  end
end
