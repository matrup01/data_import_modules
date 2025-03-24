from setuptools import setup, find_packages

with open("README.md","r") as f:
    long_description = f.read()

setup(
    name = "agg_dim",
    version = 0.1,
    description="Data import modules for instruments used by AG Grothe",
    packages = find_packages(),
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/matrup01/data_import_modules/",
    author = "Mathaeus Rupprecht, Florian Wieland",
    license = "MIT",
    licence_files = ("LICENSE"),
    install_requires = ["branca>=0.7.2",
                        "certifi>=2024.8.30",
                        "charset-normalizer>=2.0.4",
                        "contourpy>=1.2.1",
                        "cycler>=0.12.1",
                        "folium>=0.17.0",
                        "fonttools>=4.51.0",
                        "h5py>=3.11.0",
                        "idna>=3.4",
                        "Jinja2>=3.1.3",
                        "kiwisolver>=1.4.5",
                        "llvmlite>=0.42.0",
                        "MarkupSafe>=2.1.3",
                        "matplotlib>=3.6.0",
                        "numba>=0.59.0",
                        "numpy>=1.26.4",
                        "packaging>=23.2",
                        "pillow>=10.3.0",
                        "pyparsing>=3.1.2",
                        "python-dateutil>=2.8.2",
                        "requests>=2.31.0",
                        "six>=1.16.0",
                        "urllib3>=2.0.7",
                        "xyzservices>=2022.9.0",
                        ],
    python_requires=">=3.11.7"
    )