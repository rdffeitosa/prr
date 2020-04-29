# Pattern Recognition by Randomness (PRA)
O PRA é uma técnica de aprendizado de máquina para classificação de cenas que explora a aleatoriedade ocasionada por transformações de dados nas imagens. Essas transformações são baseadas na relação entre percepção natural de aleatoriedade com a teoria matemática da complexidade algorítmica de Kolmogorov. Quanto mais complexo o estímulo, mais aleatório será percebido. As transformações de dados empregadas nas imagens utilizam a técnica de compressão com perda denominada quantização vetorial. A quantização é responsável por eliminar detalhes e ampliar as características, tornando a cena mais complexa. Após essas transformações, a aleatoriedade é medida utilizando compressão sem perda como aproximação da Complexidade de Kolmogorov. Em um problema com 12 classes o PRA alcançou acurácia de 0,6967 utilizando entropia de Shannon e 0,6350 utilizando compressão.

Feitosa, R. D. F. (2020). Classificação de cenas utilizando a análise da aleatoriedade por aproximação da complexidade de Kolmogorov. Instituto de Informática, Universidade Federal de Goiás.

O código-fonte disponibilizado foi escrito em Python 2.7 e teste em sistemas baseados no linux.

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
   
O diretório codes contém os scripts de todas as etapas do métodos descritas a seguir, bem como funções auxiliares. No diretório dataset pode ser encontrada a base de dados utilizada nos experimentos [1] e 3 sugestões de particionamento entre conjunto de treinamento e teste. O diretório trainedModels contém modelos treinados em cada uma das partições sugeridas e os melhores parâmetros de treinamento de cada classe.

[1] Guang-Hai Liu, Jing-Yu Yang, etc,.  Content-based image retrieval using computational visual attention model, Pattern Recognition, 48(8) (2015) 2554-2566.
## Arquitetura do PRA
![](https://github.com/rdffeitosa/prr/blob/master/prr.png)

## Base de dados

## Experimente o PRA
