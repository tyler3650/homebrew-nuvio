cask "nuvio" do
  arch arm: "arm64", intel: "x86_64"

  version "0.1.37-alpha"
  sha256 arm:   "9835d5a800672ffeb7be759f358d1a190bcaf56545ccdaed502016da243c87de",
         intel: "1ded3b9c87d167806889f290dd471f66c73049465cb36e900be6b90a529f3bb8"

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
