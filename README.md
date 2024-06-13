
#  Alocador de salas

  

Esse projeto tem como objetivo resolver o **Problema de Alocação de Salas (PAS)** na Universidade Federal da Fronteira Sul (UFFS), Campus Chapecó.

O PAS consiste em alocar salas para aulas/turmas com horários pré-determinados. A alocação deve ser feita seguindo restrições e preferências que podem variar de acordo com a particularidade do cenário onde o problema está sendo resolvido. 

Essa aplicação utiliza de um modelo matemático e de Programação Linear Inteira para resolver o PAS no cenário da UFFS, Campus Chapecó, além disso, conta com uma interface web para facilitar o uso do usuário.

[//]: # (Essa aplicação utiliza do modelo matemático descrito no trabalho de conclusão de curso [link pro cara] para resolver o PAS no cenário da UFFS, Campus Chapecó, além disso, conta com uma interface web para facilitar o uso do usuário.)


  

#  Requisitos

*  Python >= 3.8

  

#  Instalação e configuração

Uma vez que os requisitos estão devidamente atendidos, podemos partir para a instalação

  

`pip3 install -r requirements.txt`

  

Com as dependências instaladas podemos partir para a configuração da aplicação.

  

-  Copie o arquivo `.env copy`, o renomeie para `.env` e preencha os campos presentes no arquivo

-  Também é necessário configurar o Gurobi, para informações mais detalhadas sobre sua instalação, configuração e licenças de uso acesse: https://support.gurobi.com/hc/en-us/articles/14799677517585-Getting-Started-with-Gurobi-Optimizer.

  

#  Rodando a aplicação

  

Para rodar a interface web utilize o comando

`python3 web/app.py`
