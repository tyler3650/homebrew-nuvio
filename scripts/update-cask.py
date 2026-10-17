#!/usr/bin/env python3
"""
Automatically checks upstream NuvioDesktop releases and updates Casks/nuvio.rb.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

DEFAULT_CASK_PATH = "Casks/nuvio.rb"
DEFAULT_UPSTREAM_REPO = "NuvioMedia/NuvioDesktop"
USER_AGENT = "homebrew-nuvio-updater"


def make_request(url: str, token: str | None = None) -> bytes:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def fetch_release_info(repo: str, target_version: str | None, token: str | None) -> dict:
    if target_version:
        # Check specific tag or release
        tag = target_version if target_version.startswith("v") else f"v{target_version}"
        # Upstream tags might not have 'v' prefix
        try:
            url = f"https://api.github.com/repos/{repo}/releases/tags/{target_version}"
            return json.loads(make_request(url, token).decode("utf-8"))
        except urllib.error.HTTPError:
            url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
            return json.loads(make_request(url, token).decode("utf-8"))
    else:
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        return json.loads(make_request(url, token).decode("utf-8"))


def parse_sha256sums(content: str) -> dict[str, str]:
    """Parses SHA256SUMS.txt into a filename -> sha256 mapping."""
    sums = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            sha, fname = parts[0].strip(), parts[1].strip().lstrip("*")
            sums[fname] = sha
    return sums


def download_and_compute_sha256(url: str, token: str | None = None) -> str:
    print(f"Downloading {url} to calculate SHA-256...", file=sys.stderr)
    data = make_request(url, token)
    return hashlib.sha256(data).hexdigest()


def update_cask_file(cask_path: str, new_version: str, arm64_hash: str, intel_hash: str) -> bool:
    with open(cask_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match existing version
    version_pattern = r'version\s+"([^"]+)"'
    match = re.search(version_pattern, content)
    if not match:
        raise ValueError(f"Could not find `version \"...\"` in {cask_path}")
    old_version = match.group(1)

    # Replace version
    content = re.sub(version_pattern, f'version "{new_version}"', content, count=1)

    # Replace sha256 stanza
    new_sha_stanza = (
        f'sha256 arm:   "{arm64_hash}",\n'
        f'         intel: "{intel_hash}"'
    )

    sha_pattern = r'sha256\s+(?::no_check|arm:\s+"[a-f0-9]+",\s+intel:\s+"[a-f0-9]+")'
    if re.search(sha_pattern, content):
        content = re.sub(sha_pattern, new_sha_stanza, content, count=1)
    else:
        # Fallback regex if formatting differed
        single_sha_pattern = r'sha256\s+[^\n]+'
        content = re.sub(single_sha_pattern, new_sha_stanza, content, count=1)

    # Add livecheck block if missing
    if "livecheck do" not in content:
        livecheck_block = (
            "\n  livecheck do\n"
            "    url :url\n"
            "    regex(/^v?(\\d+(?:\\.\\d+)+(?:-[a-z0-9.]+)?)$/i)\n"
            "    strategy :github_latest\n"
            "  end\n"
        )
        content = re.sub(
            r'(homepage\s+"[^"]+")\n',
            lambda m: m.group(1) + "\n" + livecheck_block,
            content,
            count=1,
        )

    with open(cask_path, "w", encoding="utf-8") as f:
        f.write(content)

    return old_version != new_version


def set_github_output(name: str, value: str) -> None:
    github_output_path = os.environ.get("GITHUB_OUTPUT")
    if github_output_path:
        with open(github_output_path, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update Nuvio Homebrew Cask")
    parser.add_argument("--cask-path", default=DEFAULT_CASK_PATH, help="Path to cask file")
    parser.add_argument("--repo", default=DEFAULT_UPSTREAM_REPO, help="Upstream repo (owner/repo)")
    parser.add_argument("--version", help="Specific version to update to (defaults to latest)")
    parser.add_argument("--force", action="store_true", help="Force update even if version is unchanged")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    # Read current version from cask file
    if not os.path.exists(args.cask_path):
        print(f"Error: Cask file not found at {args.cask_path}", file=sys.stderr)
        return 1

    with open(args.cask_path, "r", encoding="utf-8") as f:
        current_content = f.read()

    version_match = re.search(r'version\s+"([^"]+)"', current_content)
    if not version_match:
        print(f"Error: Could not determine current version from {args.cask_path}", file=sys.stderr)
        return 1

    current_version = version_match.group(1)
    print(f"Current cask version: {current_version}")

    # Fetch release from GitHub API
    try:
        release = fetch_release_info(args.repo, args.version, token)
    except Exception as e:
        print(f"Error fetching release info from {args.repo}: {e}", file=sys.stderr)
        return 1

    tag_name = release.get("tag_name", "")
    target_version = tag_name.lstrip("v")
    print(f"Target upstream version: {target_version} (tag: {tag_name})")

    if target_version == current_version and not args.force:
        print("Cask is already up to date.")
        set_github_output("updated", "false")
        return 0

    assets = release.get("assets", [])
    arm64_dmg_name = f"Nuvio-macOS-arm64-{target_version}.dmg"
    intel_dmg_name = f"Nuvio-macOS-x86_64-{target_version}.dmg"

    arm64_hash = None
    intel_hash = None

    # Check for SHA256SUMS.txt in assets
    sha256sums_asset = next((a for a in assets if a.get("name") == "SHA256SUMS.txt"), None)
    if sha256sums_asset:
        sums_url = sha256sums_asset.get("browser_download_url")
        try:
            print("Found SHA256SUMS.txt, parsing checksums...")
            raw_sums = make_request(sums_url, token).decode("utf-8")
            parsed_sums = parse_sha256sums(raw_sums)
            arm64_hash = parsed_sums.get(arm64_dmg_name)
            intel_hash = parsed_sums.get(intel_dmg_name)
        except Exception as e:
            print(f"Warning: Failed to fetch/parse SHA256SUMS.txt ({e}), falling back to direct downloads.", file=sys.stderr)

    # Fallback: compute directly from DMGs if not present in SHA256SUMS.txt
    if not arm64_hash:
        arm64_asset = next((a for a in assets if a.get("name") == arm64_dmg_name), None)
        if not arm64_asset:
            print(f"Error: Asset {arm64_dmg_name} not found in release {tag_name}", file=sys.stderr)
            return 1
        arm64_hash = download_and_compute_sha256(arm64_asset["browser_download_url"], token)

    if not intel_hash:
        intel_asset = next((a for a in assets if a.get("name") == intel_dmg_name), None)
        if not intel_asset:
            print(f"Error: Asset {intel_dmg_name} not found in release {tag_name}", file=sys.stderr)
            return 1
        intel_hash = download_and_compute_sha256(intel_asset["browser_download_url"], token)

    print(f"arm64 SHA-256: {arm64_hash}")
    print(f"intel SHA-256: {intel_hash}")

    update_cask_file(args.cask_path, target_version, arm64_hash, intel_hash)
    print(f"Successfully updated {args.cask_path} to {target_version}")

    set_github_output("updated", "true")
    set_github_output("version", target_version)
    set_github_output("old_version", current_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
