# Pattern Recognition by Randomness (PRA)
O PRA é uma técnica de aprendizado de máquina para classificação de cenas que explora a aleatoriedade ocasionada por transformações de dados nas imagens. Essas transformações são baseadas na relação entre percepção natural de aleatoriedade com a teoria matemática da complexidade algorítmica de Kolmogorov. Quanto mais complexo o estímulo, mais aleatório será percebido. As transformações de dados empregadas nas imagens utilizam a técnica de compressão com perda denominada quantização vetorial. A quantização é responsável por eliminar detalhes e ampliar as características, tornando a cena mais complexa. Após essas transformações, a aleatoriedade é medida utilizando compressão sem perda como aproximação da Complexidade de Kolmogorov.

O código-fonte disponibilizado foi escrito em Python 2.7 e teste em sistemas baseados no linux

## Estrutura dos diretórios
- codes
  - include
- dataset
   - images
   - partitionA
   - partitionB
   - partitionC
- trainedModels
   - partitionA
   - partitionB
   - partitionC
   
O diretório codes contém os scripts de todas as etapas do métodos descritas a seguir, bem como funções auxiliares. No diretório dataset pode ser encontrada a base utilizada nos experimentos e 3 sugestões de particionamento entre conjunto de treinamento e teste.
## Arquitetura do PRA

## Base de dados

## Experimente o PRA
