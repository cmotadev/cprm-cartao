from datetime import datetime, timezone
from os import path
from base64 import b64encode
from io import BytesIO
from cairosvg import svg2pdf, svg2png
from qrcode import QRCode, ERROR_CORRECT_H
# from urllib.parse import quote
from vobject import vCard
from vobject.vcard import Name, Address
from xml.etree.ElementTree import parse as xml_parse

from app import db, basedir


class Employee(db.Model):
    """
    Wrapper para tabela de empregados
    """
    __tablename__ = "employees"

    code = db.Column(
        db.Integer,
        primary_key=True
    )

    first_name = db.Column(
        db.String(100),
    )

    middle_name = db.Column(
        db.String(100),
        nullable=True
    )

    last_name = db.Column(
        db.String(100),
    )

    title = db.Column(
        db.String(50),
    )

    company = db.Column(
        db.String(50),
    )

    street = db.Column(
        db.String(100),
    )

    city = db.Column(
        db.String(100),
    )

    state_code = db.Column(
        db.String(2),
    )

    box = db.Integer()

    email = db.Column(
        db.String(100),
    )

    work_phone = db.Column(
        db.String(30),
    )

    cell_phone = db.Column(
        db.String(30),
        nullable=True
    )

    def __repr__(self):
        return "<Employee ID: %s>" % self.code

    @property
    def full_name(self):
        """
        :return:
        """
        fn = [_n for _n in (self.first_name, self.middle_name, self.last_name) if _n is not None]
        return " ".join(fn)

    def _serialize_vcard(self):
        """
        :return:
        """
        if self.code:
            # Process vCard
            _vcard = vCard()

            # # Name (Mandatory)
            _vcard.add('n').value = Name(family=self.last_name, given=self.first_name, additional=self.middle_name)

            # Formatted name (Mandatory)
            _vcard.add('fn').value = self.full_name

            # Title (Title ou Role)
            _vcard.add('title').value = self.title

            # Company
            _vcard.add('org').value = [self.company]

            # Endereço
            _vcard.add('adr').value = Address(street=self.street, city=self.city,
                                              code=self.state_code, box=str(self.box), country="Brasil")
            # E-mail
            _vcard.add('email').value = self.email

            # Telefone
            for tel, tel_type in [(self.work_phone, "WORK"), (self.cell_phone, "CELL")]:
                if tel:
                    t = _vcard.add('tel')
                    t.value = tel
                    t.type_param = tel_type

            # Revision
            _vcard.add("rev").value = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%Z")

            # serialized vcard
            return _vcard.serialize()

    def _serialize_svg(self):
        """
        :return:
        """
        src_svg = path.join(basedir, "cartao_visita_1.svg")

        xml = xml_parse(src_svg)
        root = xml.getroot()

        # Full name
        for item in root.findall(".//{http://www.w3.org/2000/svg}text[@id='card_full_name']"):
            item.text = self.full_name

        # Title
        for item in root.findall(".//{http://www.w3.org/2000/svg}text[@id='card_title']"):
            item.text = self.title

        # Work Phone
        for item in root.findall(".//{http://www.w3.org/2000/svg}text[@id='card_work_phone_number']"):
            item.text = self.work_phone

        # Cell Phone
        for item in root.findall(".//{http://www.w3.org/2000/svg}text[@id='card_cell_phone_number']"):
            item.text = self.cell_phone

        # E-Mail
        for item in root.findall(".//{http://www.w3.org/2000/svg}text[@id='card_email']"):
            item.text = self.email

        # QR Code
        qrcode = b64encode(self.as_qrcode()).decode("ascii")
        for item in root.findall(".//{http://www.w3.org/2000/svg}image[@id='card_qr_code']"):
            # item.set('{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}absref', qrcode)
            # item.set('{http://www.w3.org/1999/xlink}href', r"file://" + quote(qrcode))
            item.set('{http://www.w3.org/1999/xlink}href', "data:image/png;base64," + qrcode)

        # convert svg to pdf
        with BytesIO() as svg:
            xml.write(svg, encoding='utf-8', xml_declaration=True)
            svg.seek(0)
            bytes = svg.getvalue()

        return bytes

    def as_vcard(self, bytestring=True):
        """
        :return:
        """
        _vcard = self._serialize_vcard()

        if bytestring:
            return _vcard.encode()

        return _vcard

    def as_qrcode(self, version=1, error_correction=ERROR_CORRECT_H, box_size=5,
                  border=2, fit=True, fill_color="black", back_color="white"):
        """
        :param version:
        :param error_correction:
        :param box_size:
        :param border:
        :param fit:
        :param fill_color:
        :param back_color:
        :return:
        """
        qr = QRCode(
            version=version,
            error_correction=error_correction,
            box_size=box_size,
            border=border,
        )
        qr.add_data(self._serialize_vcard())
        qr.make(fit=fit)

        # make QR Code, removing from PIL and convert into BytesIO
        with BytesIO() as f:
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            img.save(f)
            f.seek(0)
            bytes = f.getvalue()

        return bytes

    def as_svg(self):
        """
        :return:
        """
        return self._serialize_svg()

    def as_pdf(self, dpi=200):
        """
        :return:
        """
        return svg2pdf(bytestring=self._serialize_svg().decode("utf-8"), dpi=dpi)

    def as_png(self, dpi=200):
        """
        :return:
        """
        return svg2png(bytestring=self._serialize_svg().decode("utf-8"), dpi=dpi)
