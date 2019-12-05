from io import BytesIO

from flask import send_file, abort, request, Blueprint, jsonify

from .models import CartaoVisita

qrcard_bp = Blueprint('qrcard', __name__, url_prefix="/cartao-visita")


@qrcard_bp.route('/<int:code>', methods=["GET"])
def get_emp_info(code):
    """
    :param code:
    :return:
    """
    _card = CartaoVisita.query.get(code) or abort(404)

    return jsonify(_card.as_dict())


@qrcard_bp.route('/<int:code>/vcard', methods=["GET"])
def get_vcard(code):
    """
    :param code:
    :return:
    """
    _card = CartaoVisita.query.get(code) or abort(404)

    # deliver buffer
    buf = BytesIO()
    buf.write(_card .as_vcard().encode())
    buf.seek(0)

    return send_file(buf, "text/x-vcard", as_attachment=True,
                     attachment_filename="card_{}.{}".format(_card .code, "vcf"))


@qrcard_bp.route('/<int:code>/qrcode', methods=["GET"])
def get_qrcode(code):
    """
    :param code:
    :return:
    """
    _card = CartaoVisita.query.get(code) or abort(404)

    # deliver buffer
    buf = BytesIO()
    buf.write(_card .as_qrcode())
    buf.seek(0)

    return send_file(buf, "image/png", as_attachment=False)


@qrcard_bp.route('/<int:code>/download', methods=["GET"])
def download(code):
    """
    :param code:
    :return:
    """
    _card = CartaoVisita.query.get(code) or abort(404)

    file_format = request.args.get("format") or None
    file_format = 'pdf' if file_format  is None else file_format.lower()
    dpi = request.args.get("dpi") or 300
    as_attach = request.args.get("as_attach")

    # Tratar parâmetros
    if type(dpi) is not int:
        abort(400)

    if as_attach is not None:
        if as_attach.lower() in ("n", "0", "false"):
            as_attach = False

    # Criar arquivo
    if file_format == 'pdf':
        out_file = _card.as_pdf(dpi=dpi)
        mime = "application/pdf"

    elif file_format == 'svg':
        out_file = _card.as_svg()
        mime = "image/svg+xml"

    elif file_format == 'png':
        out_file = _card.as_png(dpi=dpi)
        mime = "image/png"

    else:
        abort(400)

    # deliver buffer
    buf = BytesIO()
    buf.write(out_file)
    buf.seek(0)

    kwargs = {"as_attachment": bool(as_attach)}

    if as_attach:
        kwargs["attachment_filename"] = "card_{}.{}".format(_card.code, file_format)

    return send_file(buf, mime, **kwargs)
