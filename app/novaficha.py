import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from config import APIURL
from ficha import mostra_ficha, get_taseda
from utils import logger

INFORMA_CE = 100
INFORMA_DUE = 101
INFORMA_CNPJ = 102
SELECAO_CAMPOS_FICHA = 103
TYPING = 104
SUBMIT = 105
INFORMA_CONTEINER = 106
SELECAO_CAMPOS_RVF = 107
TYPING_RVF = 108
SUBMIT_RVF = 109
DESCRICAO_APREENSAO = 110
PESO_APREENSAO = 111
SELECAO_CAMPOS_APREENSAO = 112
TYPING_APREENSAO = 113
SUBMIT_APREENSAO = 114
MENU = 0

campos = {INFORMA_CE: 'CE', INFORMA_DUE: 'DUE', INFORMA_CNPJ: 'CNPJ'}


def abre_novaficha(update, context):
    return novaficha_start(update, context)


def novaficha_start(update, context):
    """Send a message when the command /start is issued."""
    logger.info('novaficha_start')
    buttons = [['Informar CE'], ['Informar DUE'], ['Informar CNPJ'],
               ['Criar Ficha'], ['Sair']]
    keyboard = ReplyKeyboardMarkup(buttons)
    text = ''
    ud = context.user_data
    print(ud)
    for descricao in campos.values():
        valor = ud.get(descricao)
        if valor is not None:
            text += descricao + ': ' + valor + '\n'
    if text == '':
        text = 'Informe alguns campos, depois confirme criação no botão "Criar Ficha"'
    update.message.reply_text(text=text,
                              reply_markup=keyboard)
    return SELECAO_CAMPOS_FICHA


def salva_ce(update, context):
    logger.info('salva_ce')
    context.user_data['callback'] = INFORMA_CE
    update.message.reply_text(
        'Digite o número do CE Mercante',
        reply_markup=ReplyKeyboardRemove())
    return TYPING


def salva_due(update, context):
    logger.info('salva_due')
    context.user_data['callback'] = INFORMA_DUE
    update.message.reply_text(
        'Digite o número da DUE',
        reply_markup=ReplyKeyboardRemove())
    return TYPING


def salva_cnpj(update, context):
    logger.info('salva_cnpj')
    context.user_data['callback'] = INFORMA_CNPJ
    update.message.reply_text(
        'Digite o número da CNPJ',
        reply_markup=ReplyKeyboardRemove())
    return TYPING


def save_input(update, context):
    """Save input for feature and return to feature selection."""
    logger.info('save_input')
    try:
        ud = context.user_data
        campo = campos[int(ud['callback'])]
        text = update.message.text
        ud[campo] = text
        update.message.reply_text('{} atualizado para {}'.format(campo, text))
    except Exception as err:
        logger.error(err, exc_info=True)
        update.message.reply_text(str(err))
    return novaficha_start(update, context)


def submit(update, context):
    logger.info('submit')
    ud = context.user_data
    campoovr_campotela = {'numeroCEmercante': 'CE',
                          'numerodeclaracao': 'DUE',
                          'cnpjfiscalizado': 'CNPJ'}
    payload = {}
    for campoovr, campotela in campoovr_campotela.items():
        valor = ud.get(campotela)
        if valor:
            payload[campoovr] = valor
    try:
        if len(payload) == 0:
            raise ValueError('Informe pelo menos um campo!!')
        # Adicionar CPF após os campos #
        # TODO: Será dispensável quando autenticar
        payload['cpf'] = context.user_data['cpf']
        r = requests.post(APIURL + 'ovr/new', json=payload, verify=False)
        if r.status_code != 201:
            raise Exception('Erro: %s - %s' % (r.status_code, r.text))
        id = r.json()['id']
        print(r.status_code, r.text)
        ud['ovr_id'] = id
        return mostra_ficha(update, context)
    except Exception as err:
        text = str(type(err)) + ' - ' + str(err)
        update.message.reply_text(text)

    # update.message.reply_text('OVR {} incluída '.format(ovr_id), reply_markup=ReplyKeyboardRemove())


def abre_novarvf(update, context):
    return novarvf_start(update, context)


campos_rvf = {INFORMA_CONTEINER: 'Contêiner'}


def novarvf_start(update, context):
    """Send a message when the command /start is issued."""
    logger.info('novarvf_start')
    buttons = [['Informar Contêiner'],
               ['Criar RVF'], ['Sair']]
    keyboard = ReplyKeyboardMarkup(buttons)
    text = ''
    ud = context.user_data
    print(ud)
    for descricao in campos_rvf.values():
        valor = ud.get(descricao)
        if valor is not None:
            text += descricao + ': ' + valor + '\n'
    if text == '':
        text = 'Informe alguns campos, depois confirme criação no botão "Criar RVF"'
    update.message.reply_text(text=text,
                              reply_markup=keyboard)
    return SELECAO_CAMPOS_RVF


def salva_conteiner(update, context):
    logger.info('salva_conteiner')
    context.user_data['callback_rvf'] = INFORMA_CONTEINER
    update.message.reply_text(
        'Digite o número do Contëiner',
        reply_markup=ReplyKeyboardRemove())
    return TYPING_RVF


def save_input_rvf(update, context):
    """Save input for feature and return to feature selection."""
    logger.info('save_input_rvf')
    try:
        ud = context.user_data
        campo = campos_rvf[int(ud['callback_rvf'])]
        text = update.message.text
        ud[campo] = text
        update.message.reply_text('{} atualizado para {}'.format(campo, text))
    except Exception as err:
        logger.error(err, exc_info=True)
        update.message.reply_text(str(err))
    return novarvf_start(update, context)


def submit_rvf(update, context):
    logger.info('submit_rvf')
    ud = context.user_data
    print(ud)
    camporvf_campotela = {'numerolote': 'Contêiner'}
    payload = {}
    for camporvf, campotela in camporvf_campotela.items():
        valor = ud.get(campotela)
        if valor:
            payload[camporvf] = valor
    try:
        if len(payload) == 0:
            raise ValueError('Informe pelo menos um campo!!')
        # Adicionar CPF após os campos #
        # TODO: Será dispensável quando autenticar
        payload['cpf'] = context.user_data['cpf']
        payload['ovr_id'] = context.user_data['ovr_id']
        print(payload)
        r = requests.post(APIURL + 'rvf/new', json=payload, verify=False)
        if r.status_code != 201:
            raise Exception('Erro: %s - %s' % (r.status_code, r.text))
        return mostra_ficha(update, context)
    except Exception as err:
        text = str(type(err)) + ' - ' + str(err)
        update.message.reply_text(text)


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()
    return MENU


def informa_nova_apreensao(update, context):
    return novaapreensao_start(update, context)


campos_apreensao = {DESCRICAO_APREENSAO: 'Descrição da Apreensão', PESO_APREENSAO: 'Peso da Apreensão'}


def novaapreensao_start(update, context):
    """Send a message when the command /start is issued."""
    logger.info('novaapreensao_start')
    buttons = [['Descrição da Apreensão'],
               ['Peso da Apreensão'],
               ['Salvar Apreensão'],
               ['Voltar']]
    keyboard = ReplyKeyboardMarkup(buttons)
    text = ''
    ud = context.user_data
    print(ud)
    for descricao in campos_apreensao.values():
        valor = ud.get(descricao)
        if valor is not None:
            text += descricao + ': ' + valor + '\n'
    if text == '':
        text = 'Informe os campos Descrição e Peso,\ndepois confirme criação no botão "Salvar Apreensão"'
    update.message.reply_text(text=text,
                              reply_markup=keyboard)
    return SELECAO_CAMPOS_APREENSAO


def inclui_descricao_apreensao(update, context):
    logger.info('inclui_descricao_apreensao')
    context.user_data['callback_apreensao'] = DESCRICAO_APREENSAO
    update.message.reply_text(
        'Digite a descrição da apreensão',
        reply_markup=ReplyKeyboardRemove())
    return TYPING_APREENSAO


def inclui_peso_apreensao(update, context):
    logger.info('inclui_peso_apreensao')
    context.user_data['callback_apreensao'] = PESO_APREENSAO
    update.message.reply_text(
        'Digite o peso da apreensao em Kg',
        reply_markup=ReplyKeyboardRemove())
    return TYPING_APREENSAO


def save_input_apreensao(update, context):
    """Save input for feature and return to feature selection."""
    logger.info('save_input_apreensao')
    try:
        ud = context.user_data
        campo = campos_apreensao[int(ud['callback_apreensao'])]
        text = update.message.text
        ud[campo] = text
        update.message.reply_text('{} atualizado para: {}'.format(campo, text))
    except Exception as err:
        logger.error(err, exc_info=True)
        update.message.reply_text(str(err))
    return novaapreensao_start(update, context)


def submit_apreensao(update, context):
    logger.info('submit_apreensao')
    ud = context.user_data
    print(ud)
    campos_apreensao = {'descricao': 'Descrição da Apreensão',
                        'peso': 'Peso da Apreensão'}
    payload = {'tipoapreensao': '1'}
    for campoapreensao, campotela in campos_apreensao.items():
        valor = ud.get(campotela)
        if valor:
            payload[campoapreensao] = valor
    try:
        if len(payload) == 1:  # está fixo o tipo de apreensão para somente Cocaína
            raise ValueError('Informe pelo menos um campo Descrição ou Peso!!')
        # Adicionar CPF após os campos #
        # TODO: Será dispensável quando autenticar
        payload['cpf'] = context.user_data['cpf']
        payload['rvf_id'] = context.user_data['rvf_id']
        print(payload)
        r = requests.post(APIURL + '/api/inclui_apreensao_rvf', data=payload, verify=False)
        if r.status_code != 201:
            raise Exception('Erro: %s - %s' % (r.status_code, r.text))
        update.message.reply_text('Apreensão incluída com sucesso')
        return get_taseda(update, context)
    except Exception as err:
        text = str(type(err)) + ' - ' + str(err)
        update.message.reply_text(text)
