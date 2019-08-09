# Installation

```
pip install -e .
```

Installs in development mode.


# Usage

## Convert to MP4

Chai script should output base64-encoded WIF for this to work.

```bash
$ raytracer -s script.chai | wif extract | ffmpeg -y -framerate FPS -vcodec png -i - -c:v libx264 -r 30 -pix_fmt yuv420p OUTPUT_FILE.mp4
```

Replace `FPS` and `OUTPUTFILE`.
