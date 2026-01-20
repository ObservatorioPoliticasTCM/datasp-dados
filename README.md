# dados-painel
Este repositório contém os scripts de extração e transformação de dados utilizados no painel do OPP.

Ele utiliza `poetry` para o gerenciamento das dependências. Para mais informações, é só acessar [https://python-poetry.org/docs/](https://python-poetry.org/docs/).

Além dos arquivos de configuração na raíz, o repositório tem a seguinte estrutura:

```
├── core
│   ├── downloads
│   ├── geo
│   └── urbanismo
├── notebooks
│   ├── educacao
│   ├── saude
│   └── urbanismo
├── rendered_notebooks
│   ├── educacao
│   ├── saude
│   └── urbanismo
├── data
│   ├── cache
│   └── input
└── data_output
    ├── educacao
    ├── saude
    └── urbanismo
```

O diretório `core` contém os módulos e funções para extração dos dados, organizado tecnicamente pelas fontes e padrões necessários para a extração. Inclui submódulos para `downloads`, `geo` e `urbanismo`.

O diretório `notebooks` contém um subdiretório para cada Grupo de Trabalho do observatório, com os arquivos `.ipynb` dos notebooks **sem a saída das células**, para controle de alteração do código python.

O diretório `rendered_notebooks` contém um subdiretório para cada Grupo de Trabalho do observatório, com os mesmos arquivos `.ipynb` dos subdiretórios de `notebooks`, mas com saída das células, para melhor visualização no github ou nbviewer.

O diretório `data` contém:
- `cache`: dados intermediários gerados durante a execução dos notebooks
- `input`: dados de entrada não disponíveis em fontes acessíveis via script

O diretório `data_output` contém um subdiretório para cada Grupo de Trabalho do observatório, para o armazenamento dos dados de saída que serão consumidos no Qlik Sense.

Tanto o diretório `data_output` quanto o diretório `data/cache` são gerados na execução dos notebooks, mas são ignorados pelo git.

**IMPORTANTE:** para executar corretamente os notebooks, é necessário que o servidor do jupyter lab seja iniciado na raiz do projeto, para que os caminhos absolutos de importação estejam corretos. O arquivo `.vscode/settings.json` possui uma sugestão de configuração para a execução correta na extensão Jupyter do Visual Studio Code.
