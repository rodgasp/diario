# diario.py
Realiza coleta de dados baseado em publicação PDF.

## Arquivos
diario.pdf > Fonte de dados
diario.py > Script de renderização, processamento e exportação de dados
output.json > Saída de dados

## Renderização
Utiliza-se do pacote pymupdf - fitz para renderização do conteúdo e folhas de estilo aplicados ao documento.

## Fonte de Dados
Fora utilizada a publicação datada de 05 de janeiro de 2021, constante na URL indicada para teste (http://www.diariomunicipal.com.br/famep/o-que-e)

## Template de saída
Observado que o template sugerido para teste era baseado nas publicações do estado do Acre, mantive a mesma estrutura de dados, contudo, destacando campos distintos fornecidos pela fonte de dados sugerida> Diário Oficial dos Municípios do Estado do Pará

## Tratativas de dados
Foram implementadas tratativas genéricas para fim de teste, visando a manutenção da estrutura de dados de saída fornecida  

## Melhorias e possibilidades
Observa-se infindável possibilidade de melhoria do script, desde sua tecnologia para renderização, bem como tratativas implementadas para otimização e categorização dos dados. Neste processo, vislumbra-se o acomplamento de plataformas de processamento cognitivo e big data, a fim de elucidar parâmetros indexadores de alto valor de negócio, até então desconhecidos
