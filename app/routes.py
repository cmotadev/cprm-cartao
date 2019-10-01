from app import app
from flask import send_file, abort, request
from io import BytesIO
from .models import Employee


@app.route('/employees/<int:code>/card', methods=["GET"])
def get_card(code):
    """
    :param code:
    :return:
    """
    # Define formats
    export_format = request.args.get("format")
    export_format = 'pdf' if export_format is None else export_format.lower()
    is_attach = True

    # Get employ or blow out
    employee = Employee.query.get(code) or abort(404)

    if export_format == 'pdf':
        out_file = employee.as_pdf()
        mime = "application/pdf"
        frmt = "pdf"

    elif export_format == 'svg':
        out_file = employee.as_svg()
        mime = "image/svg"
        frmt = "svg"

    elif export_format == 'vcard':
        out_file = employee.as_vcard(bytestring=True)  # required to encode str into bytes
        mime = "text/x-vcard"
        frmt = "vcf"

    elif export_format == 'qrcode':
        out_file = employee.as_qrcode()
        mime = "image/png"
        frmt = "png"
        is_attach = False

    elif export_format == 'png':
        out_file = employee.as_png()
        mime = "image/png"
        frmt = "png"
        is_attach = False

    else:
        abort(400)

    # deliver buffer
    buf = BytesIO()
    buf.write(out_file)
    buf.seek(0)

    return send_file(buf, mime, as_attachment=is_attach,
                     attachment_filename="card_{}_{}.{}".format(employee.code, export_format, frmt))


@app.route('/')
def index():
    return 'Hello World!'
