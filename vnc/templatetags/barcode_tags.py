from barcode.base import Barcode
from django import template

from io import BytesIO
import barcode
from barcode.writer import SVGWriter


register = template.Library()


@register.simple_tag
def barcode_generate(uid):

    rv = BytesIO()

    Barcode.default_writer_options['write_text'] = False

    code = barcode.get('code128', uid, writer=SVGWriter())

    code.write(rv)

    rv.seek(0)
    rv.readline()
    rv.readline()
    rv.readline()
    rv.readline()
    svg = rv.read()

    return svg.decode("utf-8")


