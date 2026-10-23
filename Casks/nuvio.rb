cask "nuvio" do
  arch arm: "arm64", intel: "x86_64"

  version "0.1.31-alpha"
  sha256 arm:   "380c98b78373a01a6701f81bc8c765a92fa33ab5fb8bf4d7395df55a5f2b4e7c",
         intel: "2f3590ed780aeb1023fe4790abe518f471822e9d250eee0bc3bed73c69ee03ec"

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
