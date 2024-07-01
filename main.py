import os
import codecs
import json
from os import walk
from bs4 import BeautifulSoup

from OneCParser import OneCParser
from UpdGenerator import UpdGenerator

SOURCE_DIR = "source"
SOURCE_JSON_DIR = "source_json"


def doc_gen(invoice_file_name):
    json_file_name = assemble_json_file(invoice_file_name)
    json_data = parse_json_file(json_file_name)
    UpdGenerator(json_data, invoice_file_name).generate_doc()


def parse_json_file(file_name) -> dict:
    with open(file_name, 'r', encoding="utf-8") as fd:
        file_data = fd.read()
    return json.loads(file_data)


def fill_up_inn_kpp_external(one_c_data):
    with open("static_data/inn_kpp.json", 'r', encoding="utf-8") as edo_file:
        inn_data = json.loads(edo_file.read())

        seller = one_c_data["СчФакт"]["Продавец"]
        buyer = one_c_data["СчФакт"]["Покупатель"]
        seller_new_data = inn_data[seller["НаимОрг"]]
        buyer_new_data = inn_data[buyer["НаимОрг"]]

        seller["ИНН"] = seller_new_data["ИНН"]
        seller["КПП"] = seller_new_data["КПП"]
        buyer["ИНН"] = buyer_new_data["ИНН"]
        buyer["КПП"] = buyer_new_data["КПП"]


def assemble_json_file(one_c_file_name):
    invoice_file_name = decode_file_to_utf8(one_c_file_name)
    with open(invoice_file_name, 'r', encoding="utf-8") as invoice_file:
        one_c_data = OneCParser(invoice_file.read()).get_data()
    signatory = prepare_signatory("static_data/SignatoryInfo.json")
    edo = prepare_edo_info("static_data/edo_info.xml", one_c_data["СчФакт"]["Покупатель"]["НаимОрг"])
    json_file_name = os.path.join(os.path.curdir, SOURCE_JSON_DIR,
                                  os.path.basename(one_c_file_name).replace("xml", "json"))

    fill_up_inn_kpp_external(one_c_data)

    with open(json_file_name, 'w', encoding="utf-8") as json_file:
        json.dump(one_c_data | signatory | edo, json_file, indent=4, ensure_ascii=False)
    return json_file_name


def prepare_signatory(file_name):
    with open(file_name, 'r', encoding="utf-8") as fd:
        file_data = fd.read()
    return json.loads(file_data)


def prepare_edo_info(file_name, buyer_name):
    with open(file_name, 'r', encoding="utf-8") as fd:
        xml_file = fd.read()
    file_data = BeautifulSoup(xml_file, features="xml")
    data = {}
    receiver = file_data.find("Орг", attrs={"Имя": buyer_name})
    sender = file_data.find("Отправитель")
    sender_provider = sender.find("Провайдер")
    data["ЭДО"] = {
        "ИдОтпр": sender["Ид"],
        "ИдПол": receiver["Ид"],
        "ИННЮЛ": sender_provider["ИННЮЛ"],
        "ИдЭДО": sender_provider["ИдЭДО"],
        "НаимОрг": sender_provider["НаимОрг"],
    }
    return data


def decode_file_to_utf8(filename, rewrite=False):
    try:
        if "utf-8" in codecs.open(filename, 'r', 'utf-8').read():
            return filename
    except:
        pass
    with codecs.open(filename, 'r', 'windows-1251') as fd:
        file_data = fd.read()
    file_data = file_data.replace("windows-1251", "utf-8")
    if rewrite:
        new_file_name = filename
    else:
        new_file_name = filename.replace(os.path.basename(filename), "utf8_" + os.path.basename(filename))
    with codecs.open(new_file_name, 'w', 'utf-8') as fd:
        fd.write(file_data)
    return new_file_name


def make_new_docs():
    file_list = []
    for (_, _, filenames) in walk(os.path.join(os.curdir, SOURCE_DIR)):
        file_list.extend(filenames)
        break

    for file in file_list:
        file_name = os.path.join(os.path.curdir, SOURCE_DIR, file)
        decoded_file_name = decode_file_to_utf8(file_name, rewrite=True)
        doc_gen(decoded_file_name)


if __name__ == '__main__':
    make_new_docs()
