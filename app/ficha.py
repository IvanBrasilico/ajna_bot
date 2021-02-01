"""Funções para consultar Endpoints do bhadrasana2."""
import io
from base64 import b64encode
from datetime import datetime, timedelta

import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from base import MENU, MINHAS_FICHAS, CONSULTA_CONTEINER, CONSULTA_EMPRESA, \
    SCAN, FOTOS, SELECIONA_FICHA, CONSULTA_FICHA, SELECIONA_RVF, CONSULTA_RVF, \
    RVF_ABERTA, ADICIONA_DESCRICAO, ADICIONA_FOTO, TASEDA
from config import APIURL
from utils import logger


def start(update, context):
    initial_menu = [['Minhas Fichas'], ['Consulta Conteiner'], ['Consulta Empresa'],
                    ['Imagem Escaner'], ['Fotos verificacao'], ['Nova Ficha']]
    logger.info('start')
    user_name = update.message.from_user.username
    logger.info('%s Starting... ' % user_name)
    try:
        cpf = get_cpf_usuario_telegram(user_name)
        context.user_data['cpf'] = cpf
        if cpf is None:
            raise Exception('Usuário não habilitado!!')
        text = 'Usuário %s CPF %s' % (user_name, cpf)
        update.message.reply_text(
            'Cliente Telegram do AJNA (alfa) - Escolha opção \n' + text,
            reply_markup=ReplyKeyboardMarkup(initial_menu, one_time_keyboard=True))
    except Exception as err:
        text = str(err)
        update.message.reply_text(text)
    return MENU


def get_cpf_usuario_telegram(user_name):
    # TODO: decorador para chamar em todas as entrados para evitar entrada direta
    r = requests.get(APIURL + 'get_cpf_telegram/%s' % user_name, verify=False)
    if r.status_code != 200:
        raise Exception('Erro: %s - %s (erro 404 pode ser Usuário não cadastrado)' % (r.status_code, r.text))
    return r.json().get('cpf')


def minhas_fichas(update, context):
    logger.info('minhas_fichas')
    # print(dir(update.message))
    user_name = update.message.from_user.username
    logger.info(user_name)
    try:
        cpf = context.user_data['cpf']
        r = requests.get(APIURL + 'minhas_fichas_text?cpf=%s' % cpf, verify=False)
        if r.status_code != 200:
            raise Exception('Erro: %s - %s' % (r.status_code, r.text))
        text = r.text
        linhas = r.text.split('\n')
        # print(len(linhas))
        opcoes = [['Abre Ficha %s' % linha.split()[0].strip()] for linha in linhas[1:]]
    except Exception as err:
        text = str(err)
    update.message.reply_text(
        "Selecione umas das fichas abaixo ou \nclique em \'Sair\' "
        "para voltar ao Menu inicial",
        reply_markup=ReplyKeyboardMarkup([*opcoes, ['Sair']],
                                         one_time_keyboard=True))
    return MENU
    # return start(update, context)


def consulta_conteiner(update, context):
    logger.info('conteiner')
    try:
        fim = datetime.now()
        inicio = fim - timedelta(days=90)
        numero = update.message.text
        user_name = update.message.from_user.username
        logger.info('%s consultando contêiner %s' % (user_name, numero))
        payload = {'numerolote': numero,
                   'datainicio': inicio,
                   'datafim': fim}
        r = requests.post(APIURL + 'consulta_conteiner_text', data=payload, verify=False)
        update.message.reply_text(r.text)
    except Exception as err:
        text = str(err)
        logger.error(err, exc_info=True)
        update.message.reply_text(text)
    return start(update, context)


def consulta_empresa(update, context):
    logger.info('empresa')
    try:
        fim = datetime.now()
        inicio = fim - timedelta(days=90)
        cnpj = update.message.text
        user_name = update.message.from_user.username
        logger.info('%s consultando empresa %s' % (user_name, cnpj))
        r = requests.get(APIURL + 'consulta_empresa_text/%s' % cnpj, verify=False)
        update.message.reply_text(r.text)
    except Exception as err:
        text = str(err)
        logger.error(err, exc_info=True)
        update.message.reply_text(text)
    return start(update, context)


def send_scan(update, context):
    logger.info('send_scan')
    numero = update.message.text
    user_name = update.message.from_user.username
    logger.info('%s consultando imagem de escaneamento %s' % (user_name, numero))
    try:
        r = requests.get(APIURL + 'escaneamentos_conteiner/%s' % numero, verify=False)
        if r.status_code == 404:
            raise Exception('Contêiner não encontrado!')
        if r.status_code != 200:
            raise Exception(r.text)
        imagens = r.json()
        for imagem in imagens:
            _id = imagem['_id']
            r = requests.get(APIURL + 'scan/%s' % _id, verify=False)
            bio = io.BytesIO(r.content)
            bio.name = '%s.jpeg' % _id
            bio.seek(0)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=bio)
            dataescaneamento = imagem['dataescaneamento']
            update.message.reply_text(dataescaneamento)
            # context.bot.send_message()
    except Exception as err:
        text = str(err)
        logger.error(err, exc_info=True)
        update.message.reply_text(text)
    return start(update, context)


def send_fotos(update, context):
    logger.info('send_fotos')
    text = update.message.text
    user_name = update.message.from_user.username
    logger.info('%s consultando fotos %s... ' % (user_name, text))
    try:
        if str(text).isnumeric():
            logger.info('Consultando fotos da rvf %s' % text)
            r = requests.get(APIURL + 'imagens_rvf/%s' % text, verify=False)
        else:
            # TODO: Consulta imagens por contêiner
            logger.info('Consultando fotos da rvf %s' % text)
            r = requests.get(APIURL + 'imagens_rvf/%s' % text, verify=False)
        logger.info(r.text)
        imagens = r.json()
        for _id in imagens:
            r = requests.get(APIURL + 'image/%s' % _id, verify=False)
            bio = io.BytesIO(r.content)
            bio.name = '%s.jpeg' % _id
            bio.seek(0)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=bio)
    except Exception as err:
        text = str(err)
        logger.error(err, exc_info=True)
        update.message.reply_text(text)
    return start(update, context)


def seleciona_ficha(update, context):
    logger.info('seleciona_ficha')
    text_parts = update.message.text.split()
    if len(text_parts) > 2:
        print('Veio por botão, passar direto para ovr %s...' % text_parts[2])
        context.user_data['ovr_id'] = text_parts[2].strip()
        return mostra_ficha(update, context)
    update.message.reply_text(
        'Digite o id da Ficha',
        reply_markup=ReplyKeyboardRemove())
    return CONSULTA_FICHA


def mostra_ficha(update, context):
    logger.info('mostra_ficha')
    if context.user_data.get('ovr_id') is None:
        ovr_selecionado = update.message.text
    else:
        ovr_selecionado = context.user_data['ovr_id']
    user_name = update.message.from_user.username
    logger.info('%s mostra_ficha ovr %s... ' % (user_name, ovr_selecionado))
    text = []
    opcoes = []
    text.append('Ficha Selecionada: %s' % ovr_selecionado)
    try:
        r = requests.get(APIURL + 'get_ovr/%s' % ovr_selecionado, verify=False)
        if r.status_code != 200:
            raise Exception(r.text)
        ovr = r.json()
        # print(ovr)
        text.append('CE: {}'.format(ovr.get('numeroCEmercante')))
        text.append('Declaracao: {}'.format(ovr.get('numerodeclaracao')))
        text.append('Fiscalizado: {}'.format(ovr.get('fiscalizado')))
        rvfs = ovr.get('rvfs')
        if rvfs:
            for rvf in rvfs:
                text.append('RVF {} contêiner/lote {}'.format(
                    rvf.get('id'), rvf.get('numerolote')))
                opcoes.append(['Abre RVF %s' % rvf.get('id')])
        text = '\n'.join(text)
    except Exception as err:
        text = 'Erro ao consultar a ficha. Digite novamente o id ou sair \n' + str(err)
        logger.error(err, exc_info=True)
        update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardRemove())
        return SELECIONA_FICHA
    update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup([*opcoes, ['Nova RVF'], ['Sair']],
                                         one_time_keyboard=True))
    return SELECIONA_RVF


def seleciona_rvf(update, context):
    logger.info('seleciona_rvf')
    text_parts = update.message.text.split()
    if len(text_parts) > 2:
        print('Veio por botão, passar direto para rvf %s...' % text_parts[2])
        context.user_data['rvf_id'] = text_parts[2].strip()
        return mostra_rvf(update, context)
    update.message.reply_text(
        'Digite o id da Verificação Física a editar\n'
        'ou \'sair\' para o menu inicial',
        reply_markup=ReplyKeyboardRemove())
    return CONSULTA_RVF


def mostra_rvf(update, context):
    logger.info('mostra_ficha')
    if context.user_data.get('rvf_id') is None:
        rvf_selecionado = update.message.text
    else:
        rvf_selecionado = context.user_data['rvf_id']
    user_name = update.message.from_user.username
    logger.info('%s mostra_ficha rvf %s... ' % (user_name, rvf_selecionado))
    text = []
    result = RVF_ABERTA
    text.append('Verificação física selecionada: %s' % rvf_selecionado)
    try:
        if not isinstance(rvf_selecionado, str):
            raise ('Valor inválido: {}'.format(rvf_selecionado))
        r = requests.get(APIURL + 'get_rvf/%s' % rvf_selecionado, verify=False)
        if r.status_code != 200:
            raise Exception(r.text)
        rvf = r.json()
        text.append('Container: {}'.format(rvf.get('numerolote')))
        # text.append('Envie texto para adicionar na descrição da Ficha')
        # text.append('Envie fotos para inserir na Ficha')
        text.append('Clique em \'Descrição\' para adicionar descrição na RVF')
        text.append('Clique em \'Foto\' para adicionar foto(s) na RVF')
        text.append('Clique em \'Taseda\' para gerar um Termo de Apreensão')
        text.append('Clique em \'sair\' para voltar ao menu inicial')
        text = '\n'.join(text)
    except Exception as err:
        text = 'Erro ao consultar a verificação. Digite novamente o id ou sair \n' + str(err)
        logger.error(err, exc_info=True)
        update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardRemove())
        return SELECIONA_RVF
    update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup([['Descrição'], ['Foto'], ['Taseda (em construção)'], ['Sair']],
                                         one_time_keyboard=True))
    return RVF_ABERTA


def edita_descricao_ficha(update, context):
    logger.info('edita_descricao_ficha')
    rvf_selecionado = context.user_data['rvf_id']
    user_name = update.message.from_user.username
    descricao = update.message.text
    logger.info(descricao)
    logger.info('%s Editando descrição rvf %s... ' % (user_name, rvf_selecionado))
    try:
        payload = {'descricao': update.message.text,
                   'rvf_id': rvf_selecionado}
        r = requests.post(APIURL + 'edita_descricao_rvf', data=payload, verify=False)
        if r.status_code != 201:
            raise Exception(r.text)
        text = 'Descrição Salva com sucesso\n Nova descrição:'
        text += r.json().get('descricao')
    except Exception as err:
        text = str(err) + str(r.text)
        logger.error(err, exc_info=True)
    update.message.reply_text(text,
                              reply_markup=ReplyKeyboardMarkup([
                                  ['Descrição'], ['Foto'], ['Taseda (em construção)'], ['Sair']
                              ], one_time_keyboard=True))
    return RVF_ABERTA


def inclui_descricao_rvf(update, context):
    logger.info('inclui_descricao_rvf')

    update.message.reply_text(
        'Digite o texto que será adicionado ao campo \'descrição\'', reply_markup=ReplyKeyboardRemove())

    return ADICIONA_DESCRICAO


def inclui_foto_rvf(update, context):
    logger.info('inclui_foto_rvf')

    update.message.reply_text('Envie a(s) foto(s) utilizando o Telegram.')

    return ADICIONA_FOTO


def upload_foto(update, context):
    logger.info('upload_foto')
    rvf_selecionado = context.user_data['rvf_id']
    user_name = update.message.from_user.username
    logger.info('%s Uploading image rvf %s... ' % (user_name, rvf_selecionado))
    try:
        file_id = update.message.photo[-1]
        new_file = context.bot.get_file(file_id)
        dataModificacao = datetime.strftime(datetime.today(), '%Y-%m-%dT%H:%M:%S') + '.'
        payload = {'content': b64encode(new_file.download_as_bytearray()),
                   'filename': 'teste.jpg',
                   'dataModificacao': dataModificacao,
                   'rvf_id': rvf_selecionado}
        r = requests.post(APIURL + 'api/rvf_imgupload', data=payload, verify=False)
        if r.status_code != 201:
            raise Exception(r.text)
        text = 'Arquivo Salvo com sucesso'
    except Exception as err:
        text = str(err)
        logger.error(err, exc_info=True)
    update.message.reply_text(text,
                              reply_markup=ReplyKeyboardMarkup([
                                  ['Descrição'], ['Foto'], ['Taseda (em construção)'], ['Sair']
                              ], one_time_keyboard=True))
    return ADICIONA_FOTO


def fecha_ficha(update, context):
    logger.info('fecha_ficha')
    return start(update, context)


def cancel(update, context):
    user = update.message.from_user
    logger.info("Usuário %s saiu.", user.first_name)
    update.message.reply_text('Retornando...',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def get_fichas(update, context):
    logger.info('get_fichas')
    update.message.reply_text(
        'Digite o CPF', reply_markup=ReplyKeyboardRemove())
    return MINHAS_FICHAS


def get_conteiner(update, context):
    logger.info('get_conteiner')
    update.message.reply_text(
        'Digite o número do contêiner', reply_markup=ReplyKeyboardRemove())
    return CONSULTA_CONTEINER


def get_empresa(update, context):
    logger.info('get_empresa')
    update.message.reply_text(
        'Digite o CNPJ a consultar, com no mínimo 8 dígitos (sem máscara)', reply_markup=ReplyKeyboardRemove())
    return CONSULTA_EMPRESA


def get_scan(update, context):
    logger.info('get_scan')
    update.message.reply_text(
        'Digite o número do contêiner', reply_markup=ReplyKeyboardRemove())
    return SCAN


def get_fotos(update, context):
    logger.info('get_fotos')
    update.message.reply_text(
        'Digite o id da verificação física ou o número do contêiner',
        reply_markup=ReplyKeyboardRemove())
    return FOTOS


def get_taseda(update, context):
    logger.info('get_taseda')
    update.message.reply_text('Favor informar Apreensão de Cocaína - descrição e peso (kg): \n'
                              'Clique no botão \'Taseda\' para fazer upload do documento preenchido\n'
                              'Clique no botão \'Sair\' para voltar a tela inicial.',
                              reply_markup=ReplyKeyboardMarkup([
                                  ['Inclui Apreensão'], ['Taseda'], ['Sair']
                              ], one_time_keyboard=True))

    return TASEDA


def voltar_taseda(update, context):
    logger.info('voltar_taseda')
    return get_taseda(update, context)


def upload_taseda(update, context):
    logger.info('inclui_descricao_taseda')
    update.message.reply_text(
        'Em construção...',
        reply_markup=ReplyKeyboardMarkup([
            ['Descrição Apreensão'], ['Peso'], ['Taseda (em construção)'], ['Sair']
        ], one_time_keyboard=True))
    return TASEDA
