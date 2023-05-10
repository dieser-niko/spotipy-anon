from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()



setup(
    name='spotipy_anon',
    version='1.2',
    description='An extension to Spotipy for anonymous access to the Spotify Web API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="@dieserniko",
    author_email="dieserniko@gmx.de",
    url='https://github.com/dieser-niko/spotipy-anon',
    project_urls={
        'Source': 'https://github.com/dieserniko/spotipy-anon',
    },
    install_requires=["spotipy>=2.23.0"],
    license='MIT',
    packages=['spotipy_anon'])
