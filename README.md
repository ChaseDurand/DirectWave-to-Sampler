# DirectWave-to-Sampler
A script for converting FL Studio DirectWave Sampler instruments to Ableton Live (10+) Sampler instruments. Samples and instruments are copied into the User Library.

## Requirements
* python 3
* packaging

## Usage
Create a DirectWave instrument with "Monolithic file" disabled to create a .dwb preset and sub-folder of audio files. Pass the sub-folder path as an argument (quotes may be required if pathname has spaces).

```python3 convert-dw.py "path/to/wavs"```

## Disclaimer
This project is not endorsed or affiliated with Ableton in any way. "Ableton" is a trademark of Ableton AG.

This project is not endorsed or affiliated with Image-Line in any way. "FL Studio" is a trademark of Image-Line Software NV.