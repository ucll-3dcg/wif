import wif.gui.imgview
import wif.encoding
import wif.config
import wif.reading
import wif.concurrency


def _raytracer_path():
    return wif.config.configuration['raytracer']


def invoke_raytracer(script, ignore_messages=False):
    (stdout, stderr) = wif.reading.open_subprocess(
        [_raytracer_path(), '-s', '-'],
        script,
        ignore_stderr=ignore_messages)

    blocks = (block.decode('ascii') for block in wif.reading.read_blocks_from_stream(stdout))
    messages = None if ignore_messages else wif.reading.read_lines_from_stream(stderr)

    return (blocks, messages)


def raytrace(script, ignore_messages=False):
    blocks, messages = invoke_raytracer(script, ignore_messages=ignore_messages)
    images = wif.reading.read_images(blocks)
    return (images, messages)
