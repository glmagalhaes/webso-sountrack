Webservice desenvolvido em Python para consulta da soundtrack de um filme.

O formato deve ser SuaUrl/request?title=movieTitle&year=movieYear

Para utilizá-lo são necessárias duas bibliotecas, flask e flask_cors, para instalá-las:

$pip install flask flask_cors


Para rodar o Webservice:

$sh runflask.sh


Obs.: Essa versão possui uma busca por links no youtube (infelizmente bem lenta), caso não necessite disso comente
desde a linha 150 até a linha 155 do arquivo app.py
Obs.2: Essa busca é cacheada, ou seja, a primeira vez que se buscar uma música+artista será lenta, nas próximas não =)