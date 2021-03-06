"""All messages sent by responders are defined here."""

REQUEST_RECEIVED = "_O teu pedido foi recebido e temos macaquinhos a trabalhar nele!_"
DEFAULT_ERROR = "O teu pedido não pode ser processado :speak_no_evil:\nTenta novamente mais tarde ou pede ajuda no <#{}|suporte>."
ERROR_SUPPORT = "É um erro? Às vezes até os macaquinhos mais espertos se enganam :grin:\n Tenta novamente mais tarde ou pede ajuda no <#{}|suporte>."
OVERLOADED_ERROR = "Não tenho macaquinhos que cheguem! :hear_no_evil::see_no_evil::speak_no_evil:\n" + DEFAULT_ERROR
UNVERIFIED_ORIGIN_ERROR = "O teu pedido tem origens suspeitas...\n" + DEFAULT_ERROR
UNAUTHORIZED = "*NÃO PODES FAZER ISSO!*\nÉ um erro? Pede ajuda no <#{}|suporte>."
BAD_COMMAND_USAGE = "*ERRO* Estás a ser totó...\n"
CREATE_TEAM_COMMAND_USAGE = "*Utilização*: `/criar-equipa <nome da equipa>`"
TEAM_REGISTRATION_SUCCESS = "Equipa registada! :banana:"
TEAM_REGISTRATION_DETAILS = "Detalhes:\n*Nome*: {}\n*Código*: {}\n*ID*: {}"
TEAM_NAME_ALREADY_EXISTS = "*ERRO!* Uma equipa com o nome '_{}_' já existe."
JOIN_TEAM_COMMAND_USAGE = "*Utilização*: `/entrar <código da equipa>`"
JOIN_TEAM_SUCCESS = "*Parabéns!*\nFoste adicionado à equipa '{}'"
USER_ALREADY_ON_TEAM_ERROR = "Já te encontras numa equipa!\n" + ERROR_SUPPORT
INVALID_CODE = "Código introduzido inválido!\n" + ERROR_SUPPORT
CHECK_BALANCE_USER_HAS_NO_TEAM = "*Ainda não te encontras numa equipa!* Só podes ver o teu saldo se fizeres parte de uma equipa.\nEntra numa equipa com o comando: `/entrar`\n" + ERROR_SUPPORT
CHECK_BALANCE_SUCCESS = "Aqui estão os detalhes financeiros da tua conta!"
CHECK_BALANCE_DETAILS = "*Equipa*: {}\n*Saldo*: {:.2f} :money_with_wings:"
BUY_COMMAND_USAGE = "*Utilização*: `/compra <@utilizador de destino> <quantia> <descrição>`"
BUY_USER_HAS_NO_TEAM = "*Ainda não te encontras numa equipa!* Só podes fazer compras se fizeres parte de uma equipa.\nEntra numa equipa com o comando: `/entrar`\n" + ERROR_SUPPORT
BUY_NO_DESTINATION_USER = "*Erro!* Deves indicar o utilizador de destino.\n" + BUY_COMMAND_USAGE
BUY_DESTINATION_ORIGIN_SAME = "*Erro!* Não podes dar dinheiro a ti próprio :thinking_face:"
BUY_DESTINATION_NO_TEAM = "*O destinatário ainda não tem equipa!*\n" + ERROR_SUPPORT
BUY_DESTINATION_SAME_TEAM = "*O destinatário está na tua equipa!*\n" + ERROR_SUPPORT
INVALID_VALUE = "*Erro!* O valor introduzido é inválido!\n" + ERROR_SUPPORT
BUY_NOT_ENOUGH_MONEY = "*Não tens dinheiro suficiente!*\n" + ERROR_SUPPORT
BUY_SUCCESS = "A tua transferência para o {} foi realizada com sucesso!"
LIST_TRANSACTIONS_USER_HAS_NO_TEAM = "*Ainda não te encontras numa equipa!* Só podes ver os teus movimentos se fizeres parte de uma equipa.\nEntra numa equipa com o comando: `/entrar`\n" + ERROR_SUPPORT
LIST_TRANSACTIONS_SUCCESS = "Aqui tens os detalhes dos últimos {} movimentos da tua equipa:\n"
LIST_TRANSACTIONS_TRANSACTION_INDEX = "_Movimento {} de {}:_\n"
LIST_TRANSACTIONS_TRANSACTION_ORIGIN_ME = "*De:* mim | *Para:* <@{}|{}> | *Data:* {}\n"
LIST_TRANSACTIONS_TRANSACTION_DESTINATION_ME = "*De:* <@{}|{}> | *Para:* mim | *Data:* {}\n"
LIST_TRANSACTIONS_TRANSACTION = "*De:* <@{}|{}> | *Para:* <@{}|{}> | *Data:* {}\n"
LIST_TRANSACTIONS_TRANSACTION_AMOUNT = "*Valor:* {:.2f} :money_with_wings: | *Descrição:* {}\n\n"
LIST_TEAMS_SUCCESS = "Aqui está a lista das {} equipas a participar:\n"
LIST_TEAMS_TEAM_DETAILS = "_{}_: *Nome:* {} | *ID:* {}\n"
LIST_REGISTRATION_TEAMS_SUCCESS = "Aqui estão as {} equipas registadas:\n"
LIST_REGISTRATION_TEAMS_TEAM_DETAILS = "_{}_: *Nome:* {} | *ID:* {} | *Código:* {}\n"
TEAM_DETAILS_COMMAND_USAGE = "*Utilização*: `/detalhes-equipa <id-equipa>`"
TEAM_DETAILS_SUCCESS = "Aqui estão os detalhes da equipa:\n"
TEAM_DETAILS_DETAILS = "*Nome:* {} | *Saldo:* {:.2f} :money_with_wings: | *ID:* {}\n"
TEAM_DETAILS_ELEMENT_DETAILS = "_Elemento:_ *Nome:* <@{}|{}> | *ID:* {}\n"
TEAM_DETAILS_SUCCESS_NO_ELEMENTS = "Não foi encontrado nenhum jogador na equipa."
TEAM_DETAILS_SUCCESS_NO_TEAM = "Não foi encontrada nenhuma equipa com esse ID."
USER_DETAILS_COMMAND_USAGE = "*Utilização: `/detalhes [@user|user-id]`.\n _Podes fornecer tanto o user pelo seu ID, bem como pela @mention_"
USER_DETAILS_SUCCESS = "*Informação:*\n*Nome:* <@{}|{}> | *ID:* {} | *Equipa:* {}"
USER_DETAILS_SUCCESS_NO_USER = "Não foi encontrado nenhum utilizador com esse ID/nome."
LIST_USER_TRANSACTIONS_SUCCESS = "Aqui tens os detalhes dos teus últimos {} movimentos:\n"
CHANGE_PERMISSIONS_COMMAND_USAGE = "*Utilização: `/alterar-permissoes [@user] [admin|staff|remover]`"
CHANGE_PERMISSIONS_SUCCESS = "As permissões do utilizador foram alteradas!"
CHANGE_PERMISSIONS_SUCCESS_CHANNEL_NOT_MODIFIED = "As permissões do utilizador foram alteradas!\nDevido a um erro, utilizador não foi adicionado/removido do canal privado, pelo que o deves fazer manualmente."
LIST_STAFF_SUCCESS = "Aqui tens a lista de elementos na staff!\n"
LIST_STAFF_DETAILS = "*Nome:* <@{}|{}> | *Função:* {} | *ID:* {}\n"
HACKERBOY_COMMAND_USAGE = "*Utilização: `/hackerboy [quantia] [descricao]`"
HACKERBOY_SUCCESS_ADD = "Boa! Transferimos {} :money_with_wings: para todas as equipas!"
HACKERBOY_SUCCESS_SUB = "Muahahah. Roubámos {} :money_with_wings: de todas as equipas!"
HACKERBOY_SUCCESS_ZERO = "Enfim, mais valia estares quieto.... 0 +- alguma coisa não faz grande diferença..."
HACKERBOY_NOT_ENOUGH_MONEY = "Erro. Alguma equipas irão ficar com saldo negativo ao realizares um 'roubo' de {} :money_with_wings:"
HACKERBOY_TEAM_COMMAND_USAGE = "*Utilização: `/hackerboy-equipa [id-equipa] [quantia] [descricao]`"
HACKERBOY_TEAM_NOT_ENOUGH_MONEY = "Erro. A equipa irá ficar com saldo negativo ao realizares um 'roubo' de {} :money_with_wings:"
HACKERBOY_TEAM_SUCCESS_ADD = "Boa! Transferimos {} :money_with_wings: para a equipa!"
HACKERBOY_TEAM_SUCCESS_SUB = "Muahahah. Roubámos {} :money_with_wings: da equipa!"
HACKERBOY_TEAM_SUCCESS_ZERO = "Enfim, mais valia estares quieto.... 0 +- alguma coisa não faz grande diferença..."
LIST_USER_TRANSACTIONS_COMMAND_USAGE = "*Utilização: `/transacoes-participante @user [quantidade]`"
USER_HAS_NO_TEAM = "*ERRO:* O utilizador não se encontra numa equipa."
LIST_ADMIN_USER_TRANSACTIONS_SUCCESS = "Aqui tens os detalhes dos últimos {} movimentos do jogador:\n"
LIST_TEAM_TRANSACTIONS_COMMAND_USAGE = "*Utilização: `/transacoes-equipa <id-equipa> [quantidade]`"
TEAM_NOT_FOUND = "*ERRO:* Essa equipa não existe."
LIST_TEAMS_TRANSACTIONS_SUCCESS = "Aqui tens os detalhes dos últimos {} movimentos da equipa:\n"
LIST_ALL_TRANSACTIONS_COMMAND_USAGE = "*Utilização: `/transacoes-todas [quantidade]`"
LIST_ALL_TRANSACTIONS_SUCCESS = "Aqui tens os detalhes dos últimos {} movimentos da NEECathon:\n"
HACKERBOY_TEAM_ADD_MONEY = "O _hackerboy_ é bondoso! Receberam uma transferência de {} :money_with_wings: !\n"
HACKERBOY_TEAM_REMOVE_MONEY = "O _hackerboy_ decidiu revoltar-se! Perderam {} :money_with_wings: do vosso saldo!\n"
HACKERBOY_TEAM_MESSAGE = "Ele deixou ainda a seguinte mensagem: ' _{}_ '."
FORMAT_ERROR = "Má formatação/utilização dos arugmentos.\n" + DEFAULT_ERROR
TRANSACTION_RECEIVED = "Boa! Receberam uma transferência de {}:money_with_wings: , do <@{}>!"
