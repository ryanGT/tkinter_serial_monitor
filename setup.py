import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name='tkinter_serial_monitor',    # This is the name of your PyPI-package.
    version='1.0.0',
    url='https://github.com/ryanGT/tkinter_serial_monitor',
    author='Ryan Krauss',
    author_email='ryanwkrauss@gmail.com',
    description="tkinter gui for reading serial output from an Arduino and plotting data",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
