from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wiiu-expedition-vc-injector",
    version="1.0.0",
    author="WiiU Expedition Team (위유 원정대)",
    description="WiiU Expedition VC Injector - Python edition of TeconMoon's WiiVC Injector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/WiiU-Expedition-VC-Injector",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.9",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "wiiu-expedition=wiivc_injector.main:main",
        ],
    },
    include_package_data=True,
)
