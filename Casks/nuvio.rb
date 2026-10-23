cask "nuvio" do
  arch arm: "arm64", intel: "x86_64"

  version "0.1.32-alpha"
  sha256 arm:   "0e18a27fce67f0291e2d46d3bfa95e6323cb2c0e83941b9a87193f954aeb61bd",
         intel: "ce2ebd3367eb3d3ee3079431c4eb8d4ff27fe96a2517fb81cba1a591349c84db"

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
