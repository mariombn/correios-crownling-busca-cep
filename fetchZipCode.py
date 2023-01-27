#!/usr/bin/env python3

import html_to_json
import json
import urllib.request
import urllib.parse

def main():
    # Busca Todas as UFs no site dos Correios
    print("Obtendo todos os UFs...")
    uf_collection = getAllUFs()
    print("OK")

    # Cria um json em branco
    json_result = []

    # Para cada UF
    for uf in uf_collection:
        print("    Processando UF " + uf)
        # busca o conteúdo da primeira página
        content = getContentByUf(uf)

        # Adiciona Resultado ao JSON
        json_result.append({
            'uf': uf,
            'data': content
        })

    print("Processamento Concluido")

    # Salva arquivo JSON em disco
    with open("result.json", "w") as outfile:
        json.dump(json_result, outfile)

    print("Arquivo result.json gerado com sucesso")
    

def getAllUFs():

    # Prepara a requisição para a página dos correios
    url = r'https://www2.correios.com.br/sistemas/buscacep/buscaFaixaCep.cfm'
    data = {}
    content = []
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-agent',
         "Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201")]

    # Executa a requisição
    with opener.open(url, urllib.parse.urlencode(data).encode('ISO-8859-1')) as url:
        for line in url.readlines():
            content.append(line.decode('ISO-8859-1'))

    # Filtra o HTML para obter o bloco onde encontra-se o <select> das UFs
    content = [elem.rstrip() for elem in content if 'select name=UF' in elem]

    # Converte o HTML para JSON
    jsonContent = html_to_json.convert(content[0])

    # Navega no JSON até chegar no nivel dos <options> das UFs
    uf_collection_raw = jsonContent['div'][0]['form'][0]['div'][0]['div'][0]['span'][1]['label'][0]['select'][0]['option'][0]['option']
    uf_collection = []

    # Cria uma lista com as UFs
    for uf_raw in uf_collection_raw:
        uf_collection.append(uf_raw['_value'])
    

    return uf_collection

def getContentByUf(uf):
    url = r'https://www2.correios.com.br/sistemas/buscacep/resultadoBuscaFaixaCEP.cfm'

    data = {
        'UF': uf
    }

    content = []
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-agent',
         "Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201")]

    with opener.open(url, urllib.parse.urlencode(data).encode('ISO-8859-1')) as url:
        for line in url.readlines():
            content.append(line.decode('ISO-8859-1'))

    content = [elem.rstrip() for elem in content if 'table class="tmptabela"' in elem]
    jsonContent = html_to_json.convert(content[0])

    record_collection_raw = jsonContent['div'][0]['div'][1]['div'][1]['br'][2]['table'][0]['tr']
    count = 0

    record_collection = []

    for record_raw in record_collection_raw:
        if count < 2:
            count += 1
            continue

        record_collection.append({
            'locate': record_raw['td'][0]['_value'],
            'range': record_raw['td'][1]['_value'],
            'status': record_raw['td'][2]['_value'],
            'type': record_raw['td'][3]['_value'],
        })

    return record_collection

main()