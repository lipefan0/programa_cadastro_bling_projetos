from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
import requests

app = Flask(__name__)  # Atualizando o caminho do template

class CriarContatos:
    def __init__(self, token):
        self.token = token

    def criar_payload_em_lotes(self, tipos_contato, df, tamanho_lote=10):
        tipo_contato_dict = {tipo['descricao']: tipo['id'] for tipo in tipos_contato}
        contador = 0
        total_contatos = len(df)  # Número total de contatos

        # Processar em lotes
        for inicio in range(0, total_contatos, tamanho_lote):
            fim = min(inicio + tamanho_lote, total_contatos)
            lote = df.iloc[inicio:fim]  # Seleciona um lote do DataFrame

            for index, row in lote.iterrows():
                tipo_descricao = row['tipoContato'] or ""
                tipo_id = tipo_contato_dict.get(tipo_descricao, None)

                # Criar o payload do contato
                data = {
                    "nome": self.check_value(row['nome']),
                    "codigo": self.check_value(row['codigo']),
                    "situacao": self.check_value(row['situacao']),
                    "numeroDocumento": self.check_value(row['numeroDocumento']),
                    "telefone": self.check_value(row['telefone']),
                    "celular": self.check_value(row['celular']),
                    "fantasia": self.check_value(row['fantasia']),
                    "tipo": self.check_value(row['tipo']),
                    "indicadorIe": self.check_value(row['indicadorIe']),
                    "ie": self.check_value(row['ie']),
                    "rg": self.check_value(row['rg']),
                    "orgaoEmissor": self.check_value(row['orgaoEmissor']),
                    "email": self.check_value(row['email']),
                    "endereco": {
                        "geral": {
                            "endereco": self.check_value(row['enderecoGeral']),
                            "cep": self.check_value(row['cepGeral']),
                            "bairro": self.check_value(row['bairroGeral']),
                            "municipio": self.check_value(row['cidadeGeral']),
                            "uf": self.check_value(row['ufGeral']),
                            "numero": self.check_value(row['numeroGeral']),
                            "complemento": self.check_value(row['complementoGeral'])
                        },
                        "cobranca": {
                            "endereco": self.check_value(row['enderecoCobranca']),
                            "cep": self.check_value(row['cepCobranca']),
                            "bairro": self.check_value(row['bairroCobranca']),
                            "municipio": self.check_value(row['cidadeCobranca']),
                            "uf": self.check_value(row['ufCobranca']),
                            "numero": self.check_value(row['numeroCobranca']),
                            "complemento": self.check_value(row['complementoCobranca'])
                        }
                    },
                    "dadosAdicionais": {
                        "dataNascimento": self.check_value(row['dataNascimento']),
                        "sexo": self.check_value(row['sexo']),
                        "naturalidade": self.check_value(row['naturalidade']),
                    },
                    'tiposContato': [
                        {
                            "id": tipo_id,
                            "descricao": tipo_descricao,
                        }
                    ]
                }

                # Enviar os dados do contato à API
                self.post_contatos(data)
                contador += 1  # Contagem dos contatos processados

        return contador  # Retorna o número total de contatos importados

    def check_value(self, value):
        return "" if pd.isna(value) else value

    def post_contatos(self, payload):
        url = 'https://www.bling.com.br/Api/v3/contatos'
        headers = {"Authorization": "Bearer " + self.token}
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)

    def get_tipo_contato(self):
        url = 'https://www.bling.com.br/Api/v3/contatos/tipos'
        headers = {"Authorization": "Bearer " + self.token}
        response = requests.get(url, headers=headers)
        return response.json().get('data', [])


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        token = request.form['token']
        file = request.files['file']
        df = pd.read_excel(file)
        contatos = CriarContatos(token)
        tipos_contato = contatos.get_tipo_contato()
        quantidade_importada = contatos.criar_payload(tipos_contato, df)

        return redirect(url_for('success', count=quantidade_importada))  # Redireciona para a página de sucesso

    return render_template('index.html')

@app.route('/loading', methods=['POST'])
def loading():
    token = request.form['token']
    file = request.files['file']
    df = pd.read_excel(file)
    contatos = CriarContatos(token)
    tipos_contato = contatos.get_tipo_contato()
    
    # Processando em lotes de 10 contatos por vez
    quantidade_importada = contatos.criar_payload_em_lotes(tipos_contato, df, tamanho_lote=10)

    # Redireciona para a página de sucesso
    return redirect(url_for('success', count=quantidade_importada))



@app.route('/success')
def success():
    count = request.args.get('count', 0)  # Obtém a contagem da URL
    return render_template('success.html', count=count)  # Passa a contagem para o template


if __name__ == '__main__':
    app.run(debug=True, port=5001)
