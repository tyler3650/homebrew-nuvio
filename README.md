# homebrew-nuvio

This is a custom Homebrew tap for [Nuvio Desktop](https://github.com/NuvioMedia/NuvioDesktop). 

Nuvio Desktop is a cross-platform media client for browsing metadata, managing collections, downloading media, and playing streams from user-installed extensions or user-provided sources.

## Malware Issues With Nuvio's .dmg File

This should fix the issue where Nuvio's .dmg file is flagged as malware, and allow you to install Nuvio directly onto macOS with no security warnings (will recure your admin passoword to run).

## Install

To install Nuvio Desktop on macOS using Homebrew (`brew`), run the following commands in your terminal:

```bash
# Add the tap
brew tap tyler3650/nuvio && brew trust tyler3650/nuvio
```
```bash
# Install the application
brew install --cask nuvio
```

## Upgrade

To upgrade Nuvio Desktop to the latest version when a new release is available in this tap, run:

```bash
brew update && brew upgrade --cask nuvio
```

## Uninstall

If you want to uninstall Nuvio Desktop and remove this tap from your system, run the following commands:

```bash
# Remove the application
brew uninstall --cask nuvio
```
```bash
# Remove the tap
brew untrust tyler3650/nuvio && brew untap tyler3650/nuvio
```
