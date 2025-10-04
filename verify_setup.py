#!/usr/bin/env python3
"""
Setup verification script for Google Photos Manager.

This script checks if all dependencies and requirements are properly
configured.
"""

from pathlib import Path
import subprocess
import sys


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(
            f"   ✅ Python {version.major}.{version.minor}.{version.micro} (compatible)"
        )
        return True
    else:
        print(
            f"   ❌ Python {version.major}.{version.minor}.{version.micro} "
            "(requires 3.8+)"
        )
        return False


def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n📦 Checking Python dependencies...")

    required_packages = [
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
        "PIL",  # Pillow
        "pillow_heif",
        "cv2",  # opencv-python
        "click",
        "tqdm",
        "requests",
        "imagehash",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package in {"PIL", "cv2", "pillow_heif"}:
                pass
            else:
                __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing_packages.append(package)

    return len(missing_packages) == 0


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("\n🎬 Checking FFmpeg...")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            # Extract version from first line
            version_line = result.stdout.split("\n")[0]
            print(f"   ✅ {version_line}")
            return True
        else:
            print("   ❌ FFmpeg not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ FFmpeg not found")
        print("   📝 Install with: brew install ffmpeg (macOS)")
        return False


def check_project_structure():
    """Check if project structure is correct."""
    print("\n📁 Checking project structure...")

    required_files = [
        "photo_manager/__init__.py",
        "photo_manager/cli.py",
        "photo_manager/auth/__init__.py",
        "photo_manager/api/__init__.py",
        "photo_manager/processors/__init__.py",
        "photo_manager/config/__init__.py",
        "photo_manager/utils/__init__.py",
        "requirements.txt",
        "README.md",
        ".env.example",
    ]

    missing_files = []
    project_root = Path(__file__).parent

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            missing_files.append(file_path)

    return len(missing_files) == 0


def check_cli():
    """Check if CLI is working."""
    print("\n⚡ Checking CLI functionality...")
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "photo_manager", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0 and "Google Photos Manager" in result.stdout:
            print("   ✅ CLI working correctly")
            return True
        else:
            print("   ❌ CLI not working")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ CLI timeout")
        return False


def check_configuration():
    """Check configuration files."""
    print("\n⚙️  Checking configuration...")

    project_root = Path(__file__).parent
    env_example = project_root / ".env.example"
    env_file = project_root / ".env"
    credentials_file = project_root / "credentials.json"

    if env_example.exists():
        print("   ✅ .env.example found")
    else:
        print("   ❌ .env.example missing")

    if env_file.exists():
        print("   ✅ .env found")
    else:
        print("   ⚠️  .env not found (copy from .env.example)")

    if credentials_file.exists():
        print("   ✅ credentials.json found")
    else:
        print("   ⚠️  credentials.json not found (see GOOGLE_SETUP.md)")

    # Check if CLI config works
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "photo_manager", "config-info"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            print("   ✅ Configuration loading works")
            return True
        else:
            print("   ❌ Configuration loading failed")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ Configuration check timeout")
        return False


def main():
    """Main verification function."""
    print("🔍 Google Photos Manager - Setup Verification")
    print("=" * 50)

    checks = [
        check_python_version(),
        check_dependencies(),
        check_ffmpeg(),
        check_project_structure(),
        check_cli(),
        check_configuration(),
    ]

    passed = sum(checks)
    total = len(checks)

    print(f"\n📊 Results: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All checks passed! Your setup is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Set up Google Photos API (see GOOGLE_SETUP.md)")
        print("   2. Run: python -m photo_manager auth")
        print("   3. Start using: python -m photo_manager albums list")
    else:
        print(f"\n⚠️  {total - passed} checks failed.")
        print("Please address the issues above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
