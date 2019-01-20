# Installation

```
pip install -e .
```

Installs in development mode.


# Usage

## Convert to MP4

Chai script should output base64-encoded WIF for this to work.

```
raytracer -s script.chai | wif studio-convert | ffmpeg -y -framerate FPS -vcodec png -i - -c:v libx264 -r 30 -pix_fmt yuv420p OUTPUT_FILE.mp4
```
