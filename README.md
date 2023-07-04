# SpotipyAnon

##### Anonymous access to the Spotify API


## Installation

```bash
pip install spotipy-anon
```

alternatively, for Windows users 

```bash
py -m pip install spotipy-anon
```

or upgrade

```bash
pip install spotipy-anon --upgrade
```


## Quick Start

To get started, install spotipy with spotipy-anon to create a script like this:

```python
import spotipy
from spotipy_anon import SpotifyAnon

sp = spotipy.Spotify(auth_manager=SpotifyAnon())

results = sp.search(q='weezer', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'])
```


## Reporting Issues

If you have suggestions, bugs or other issues specific to this library,
file them [here](https://github.com/dieser-niko/spotipy-anon/issues).
Or just send a pull request.



## Disclaimer

Yes, this README is heavily inspired by the [spotipy](https://github.com/spotipy-dev/spotipy) library, as I want to create a similar experience when working with this extension module.
