from flask import Flask, escape
from datetime import datetime, timezone
from vobject import vCard
from vobject.vcard import Name, Address

app = Flask(__name__)

people = {
    '93112841': {
        "first_name": "Carlos Eduardo",
        "middle_name": "Miranda",
        "last_name": "Mota",
        "title": "Pesquisador em Geociências",
        "company": "CPRM Esritório Rio de Janeiro",
        "street": "Av Pasteur, 404, Urca",
        "city": "Rio de Janeiro",
        "state_code": "RJ",
        "country": "Brasil",
        "box": "22290-255",
        "email": "carlos.mota@cprm.gov.br",
        "tels": [
            ("21 2546-0320", "WORK"),
            ("21 97551-7278", "CELL")
        ]
    },
}


class Contact(object):
    """
    """
    __vcard__ = vCard()

    @property
    def vcard(self):
        """
        :return:
        """
        return self.__vcard__

    def __init__(self, first_name, middle_name, last_name, title, company,
                 street, city, state_code, country, box, email, tels=[]):

        # Name (Mandatory)
        self.vcard.add('n').value = Name(family=last_name, given=first_name, additional=middle_name)

        # Formatted name (Mandatory)
        self.vcard.add('fn').value = "{} {} {}".format(first_name, middle_name, last_name)

        # Title (Title ou Role)
        self.vcard.add('title').value = title

        # Company
        self.vcard.add('org').value = [company]

        # Endereço
        self.vcard.add('adr').value = Address(street=street, city=city,
                                              code=state_code, box=box, country=country)
        # E-mail
        self.vcard.add('email').value = email

        # Telefone
        for tel in tels:
            t = self.vcard.add('tel')
            t.value = tel[0]
            t.type_param = tel[1]

        # Revision
        self.vcard.add("rev").value = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%Z")

    def export_vcard(self):
        """
        :return:
        """
        return self.vcard.serialize()

    def export_qrcode(self):
        """
        :return:
        """
        return self.vcard.serialize()


@app.route('/cartao/<matricula>', methods=["GET"])
def card(matricula):
    p = Contact(**people[matricula])

    return p.export_vcard()


@app.route('/')
def index():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
