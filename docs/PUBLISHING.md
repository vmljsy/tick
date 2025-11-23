# Publishing Releases on GitHub

## Quick Release Process

### 1. Update Version

Edit `pyproject.toml`:
```toml
version = "0.2.0"  # Increment version
```

### 2. Commit and Tag

```bash
git add .
git commit -m "Release v0.2.0"
git tag v0.2.0
git push origin main --tags
```

### 3. Create GitHub Release

**Option A: GitHub Web UI**
1. Go to your repo → Releases → "Draft a new release"
2. Choose the tag you just created (v0.2.0)
3. Title: "v0.2.0"
4. Description: List changes/features
5. Click "Publish release"

**Option B: GitHub CLI**
```bash
gh release create v0.2.0 --title "v0.2.0" --notes "Release notes here"
```

Done! Users can now install with:
```bash
uv pip install git+https://github.com/yourusername/tick.git
```

## Optional: Build and Attach Wheel

If you want to provide a downloadable wheel file:

```bash
# Build
uv run python -m build

# Attach to release (GitHub CLI)
gh release upload v0.2.0 dist/*.whl dist/*.tar.gz

# Or manually attach via GitHub web UI
```

Users can then install from wheel:
```bash
uv pip install https://github.com/yourusername/tick/releases/download/v0.2.0/tick_time_tracker-0.2.0-py3-none-any.whl
```

## Automated Releases (Recommended)

Set up GitHub Actions to automatically:
- Build on tag push
- Create release
- Attach distribution files

See `.github/workflows/release.yml`

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `0.1.0` → `0.1.1` - Bug fixes
- `0.1.0` → `0.2.0` - New features
- `0.1.0` → `1.0.0` - Breaking changes
