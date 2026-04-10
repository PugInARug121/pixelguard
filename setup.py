from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pixelguard-discord-bot",
    version="1.0.0",
    author="PixelGuard Community",
    author_email="",
    description="A comprehensive Discord moderation bot with welcome features and image generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pixelguard-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Communications :: Chat :: Discord",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="discord bot moderation welcome spam honeypot image generation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/pixelguard-bot/issues",
        "Source": "https://github.com/yourusername/pixelguard-bot",
        "Documentation": "https://github.com/yourusername/pixelguard-bot/blob/main/README.md",
    },
)
