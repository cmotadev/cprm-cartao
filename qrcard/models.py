from base64 import b64encode
from datetime import datetime, timezone
from io import BytesIO
from re import split as re_split
from os import path
from xml.etree.ElementTree import parse as xml_parse

from cairosvg import svg2pdf, svg2png
from qrcode import QRCode, ERROR_CORRECT_M
from sqlalchemy import Column, Integer, String
from vobject import vCard
from vobject.vcard import Name, Address

from app.db import Base
from app.utils import tokenize, format_name


class CartaoVisita(Base):
    """
    Wrapper para tabela de empregados
    """
    # TODO: Arrumar o arquivo de templates para renderizar o cartão minimalista
    #       e ver opções para colocar o cartão em inglês
    __template__ = 'templates/cartao_visita_1.svg'
    __tablename__ = 'vw_empregados_cartao_visita'

    code = Column(
        "matricula",
        Integer,
        primary_key=True
    )

    name = Column(
        "nome",
        String(30)
    )

    title = Column(
        "ocup",
        String(40)
    )

    company = Column(
        "lotacao",
        String(60)
    )

    street = Column(
        "endereco_local",
        String(50)
    )

    city = Column(
        "nome_local",
        String(40)
    )

    state_code = Column(
        "uf_local",
        String(2)
    )

    box = Column(
        "cep_local",
        String(10)
    )

    email = Column(
        "email",
        String(50)
    )
    work_phone = Column(
        "telefone",
        String(15)
    )

    cell_phone = Column(
        "celular",
        String(15),
        nullable=True
    )

    @property
    def is_clean(self):
        """
        :return:
        """
        return getattr(self, "_clean", False)

    def __repr__(self):
        return "<Card: %s>" % str(self.code).zfill(8)

    def _clean_all(self):
        """
        :return:
        """
        # strips, if not formatted
        self.email = str(self.email).strip()
        self.company = str(self.company).strip()

        # Force Format names
        for prop in ["name", "title", "street", "city"]:
            val = getattr(self, prop)
            setattr(self, prop, format_name(val))

        # Force Upper or cases
        self.state_code = self.state_code.upper()
        self.email = self.email.lower()

        # Apply masks
        self.box = "%s-%s" % (self.box[:5], self.box[5:])
        # self.work_phone
        # self.cell_phone

        # Special cases
        self.company = format_name(re_split(r"\||\/+", self.company).pop())

        self._clean = True
        return

    def _get_vcard_name(self):
        name_split = tokenize(self.name)
        name_split_len = len(name_split)

        if name_split_len == 2:
            vcard_name = {"given": name_split[0],
                          "family": name_split[1]}

        elif name_split_len == 3:
            vcard_name = {"given": name_split[0],
                          "additional": name_split[1],
                          "family": name_split[2]}

        elif name_split_len >= 4:
            vcard_name = {"given": " ".join(name_split[0:2]),
                          "additional": " ".join(name_split[2:name_split_len - 1]),
                          "family": name_split[name_split_len - 1]}

        else:
            raise ValueError("Name split failed for vCard Generation")

        return vcard_name

    def as_dict(self):
        """
        :return:
        """
        if not self.is_clean:
            self._clean_all()

        return {
            "code": str(self.code).zfill(8),
            "name": self.name,
            "title": self.title,
            "company": self.company,
            "address": "%s, %s - %s. CEP: %s" % (self.street, self.city, self.state_code.upper(), self.box),
            "email": self.email,
            "work_phone": self.work_phone,
            "cell_phone": self.cell_phone,
            "rev": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%Z")
        }

    def as_vcard(self):
        """
        :return:
        """
        if self.code:
            if not self.is_clean:
                self._clean_all()

            # Process vCard
            _vcard = vCard()

            # Name (Mandatory)
            _vcard.add('n').value = Name(**self._get_vcard_name())

            # Formatted name (Mandatory)
            _vcard.add('fn').value = self.name

            # Title (Title ou Role)
            _vcard.add('title').value = self.title

            # Company
            _vcard.add('org').value = ["Serviço Geológico do Brasil/CPRM", self.company]

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

    def as_qrcode(self, error_correction=ERROR_CORRECT_M, box_size=5,
                  border=2, fill_color="black", back_color="white"):
        """
        :param error_correction:
        :param box_size:
        :param border:
        :param fill_color:
        :param back_color:
        :return:
        """
        qr = QRCode(
            error_correction=error_correction,
            box_size=box_size,
            border=border,
        )
        qr.add_data(self.as_vcard())
        qr.make(fit=True)

        # make QR Code, removing from PIL and convert into Bytestring
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
        template = path.join(path.abspath(path.dirname(__file__)), self.__template__)
        xml = xml_parse(template)
        root = xml.getroot()

        if not self.is_clean:
            self._clean_all()

        # Full name
        for item in root.findall(".//{http://www.w3.org/2000/svg}text[@id='card_full_name']"):
            item.text = self.name

        # Title
        for item in root.findall(".//{http://www.w3.org/2000/svg}text[@id='card_title']"):
            item.text = self.title

        # Company
        for item in root.findall(".//{http://www.w3.org/2000/svg}text[@id='card_company']"):
            item.text = self.company

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

    def as_pdf(self, dpi=300):
        """
        :return:
        """
        return svg2pdf(bytestring=self.as_svg().decode("utf-8"), dpi=dpi)

    def as_png(self, dpi=300):
        """
        :return:
        """
        return svg2png(bytestring=self.as_svg().decode("utf-8"), dpi=dpi)
