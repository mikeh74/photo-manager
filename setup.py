"""
Setup configuration for Google Photos Manager.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = (
    readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
)

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split("\n")
    requirements = [
        req.strip() for req in requirements if req.strip() and not req.startswith("#")
    ]

setup(
    name="google-photos-manager",
    version="1.0.0",
    author="Photo Manager",
    author_email="contact@example.com",
    description="A Python application for managing your Google Photos library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/photo-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics",
        "Topic :: System :: Archiving",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-mock>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ]
    },
    entry_points={
        "console_scripts": [
            "photo-manager=photo_manager.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
