import wif.gui.imgview
import wif.io
import wif.config
import wif.reading
import wif.concurrency


def _raytracer_path():
    return wif.config.configuration['raytracer']


def invoke_raytracer(script):
    (stdout, stderr) = wif.reading.open_subprocess(
        [_raytracer_path(), '-s', '-'],
        script)

    blocks = (block.decode('ascii') for block in wif.reading.read_blocks_from_stream(stdout))
    messages = wif.reading.read_lines_from_stream(stderr)

    return (blocks, messages)
