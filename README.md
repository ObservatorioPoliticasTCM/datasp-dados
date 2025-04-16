# dados-painel
Este repositório contém os scripts de extração e transformação de dados utilizados no painel do OPP.

Ele utiliza `poetry` para o gerenciamento das dependências. Para mais informações, é só acessar [https://python-poetry.org/docs/](https://python-poetry.org/docs/).

Além dos arquivos de configuração na raíz, o repositório ele tem a seguinte estrutura:

```
├── core
├── notebooks
│ ├── educacao
│ ├── genero
│ ├── saude
│ ├── urbanismo
│ └── orcamento
├── notebooks_outputs
│ ├── educacao
│ ├── genero
│ ├── saude
│ ├── urbanismo
│ └── orcamento
└── data
  ├── educacao
  ├── genero
  ├── saude
  ├── urbanismo
  └── orcamento
```

O diretório `core` conterá os módulos e funções para extração dos dados, organizado tecnicamente pelas fontes e padrões necessários para a extração.

O diretório `notebooks` conterá um subdiretório para cada Grupo de Trabalho do observatório, com os arquivos `.ipynb` dos notebooks **sem a saída das células**, para controle de alteração do código python.

O diretório `notebooks_outputs` conterá um subdiretório para cada Grupo de Trabalho do observatório, com os mesmos arquivos `.ipynb` dos subdiretórios de `notebooks`, mas com saída das células, para melhor visualização no github ou nbviewer.

Por último, o diretório `data` conterá um subdiretório para cada Grupo de Trabalho do observatório, para o armazenamento de eventuais dados de entrada não disponíveis em fontes acessíveis via script.
