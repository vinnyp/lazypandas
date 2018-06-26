import setuptools

setuptools.setup(
    name="lazypandas",
    version="0.1.0",
    url="https://github.com/vinnyp/lazypandas",

    author="Vinny Pasceri",
    author_email="vinnypasceri@gmail.com",

    description="A collection of data wrangling helper methods for pandas.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=['pandas>=0.23.1', 'numpy>=1.14.3'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
