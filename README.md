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
   
O diretório codes contém os scripts de todas as etapas do métodos descritas a seguir, bem como funções auxiliares. No diretório dataset pode ser encontrada a base de dados utilizada nos experimentos e 3 sugestões de particionamento entre conjunto de treinamento e teste. O diretório trainedModels contém modelos treinados em cada uma das partições sugeridas e os melhores parâmetros de treinamento de cada classe.

## Arquitetura do PRA
![](https://github.com/rdffeitosa/prr/blob/master/prr.png)

A figura acima descreve as principais etapas do RPA, divididas entre os *Módulos de Treinamento* e de *Classificação*. A base do *Módulo de Treinamento* é a *etapa #1*, de *Prototipação*. Nela as imagens de treinamento fornecem amostras para uma heurística responsável por obter os protótipos das classes (*codevectors*) e organizá-los em *codebooks*. Para cada classe, o *codebook* é formado por diversos tamanhos de janelas e quantidade de protótipos, definidos em parâmetro. Na *etapa #2*, de *Quantização*, as imagens de treinamento são reconstruídas com os *codevectors* obtidos na etapa anterior. Uma medida de complexidade da informação é calculada na *etapa #3*, *Mensuração*. Os melhores parâmetros de treinamento de cada classe são selecionados na *etapa #4* *Validação*. Esses parâmetros validados são utilizados no *Módulo de Classificação* na *etapa #5* de *Quantização* das imagens de teste. Por fim, na *etapa #6* é realizado o processo de tomada de *Decisão* para as amostras de teste. Cada uma dessas etapas foi implementada em um script Python disponível no diretório **codes** e serão detalhados abaixo.

## Base de dados
A base de dados utilizada foi a *GHIM-10k*[1], originalmente composta por 20 categorias de cenas, cada uma com 500 imagens de dimensões 400x300 ou 300x400 pixels no formato JPEG. Foram selecionadas 12 classes, com 100 imagens cada, a partir do *dataset* original: *árvore*, *avião*, *campo*, *carro*, *construção*, *corrida de motos*, *flor*, *fogos de artifício*, *montanha*, *moto*, *pôr do sol* e *praia*.  Algumas classes foram selecionadas de modo que contivessem elementos em comum com outras para evitar modelos de treinamento enviesados. A Figura abaixo apresenta uma amostra de cada classe utilizada nos experimentos.

![](https://github.com/rdffeitosa/prr/blob/master/dataset/dataset.png)

[1] Guang-Hai Liu, Jing-Yu Yang, etc,.  Content-based image retrieval using computational visual attention model, Pattern Recognition, 48(8) (2015) 2554-2566.

## Execute o PRA

### Módulo de classificação
Os modelos pré-treinados disponíveis em **treinedModels** e as sugestões de melhores parâmatros podem ser utilizados para classificar as imagens disponíveis no diretório **dataset**

#### classifierPRR.py
SINTAXE

classifierPRR.py --input-folder <folder path with images for classification> --measure-engine <zip, gzip, bzip2, LZWHuffman or entropy> --classes-parameters <tuple of classes and parameters used for classification between "..."> --training-file <training data file> --quantization-colors <number of colors> [--number-processes <number of parallel processes> --id-experiment <identification of experiments> archive-results verbose-mode report-mode]
  
PARÂMETROS
- 
EXEMPLO


### Módulo de treinamento

#### trainingPrototyping.py
SINTAXE

trainingPrototyping.py --input-folder <folder path with images for training> --quantization-colors <number of colors> --training-convergence <convergence value> [--vectors-sizes <vectors sizes> --codebooks-sizes <number of symbols> --classes-parameters <classes and your specific parameters in a list of tuples "(('classname', (vector size, codebook size)), ('classname', (vector size, codebook size)), ..., ('classname', (vector size, codebook size)))"> --number-processes <number of parallel processes>]

PARÂMETROS

EXEMPLO


#### trainingQuantization.py
SINTAXE

trainingQuantization.py --input-folder <input folder with images for quantization> --quantization-colors <number of colors> --training-file <training data file> [--number-processes <number of parallel processes>]

PARÂMETROS

EXEMPLO


#### trainingMeasurement.py
SINTAXE

trainingMeasurement.py --input-data <input with quantizations data file> [--training-file <training data file>] --measure-engines <'zip gzip bzip2 LZWHuffman entropy'> [--number-processes <number of parallel processes>]

PARÂMETROS

EXEMPLO


#### trainingValidation.py
SINTAXE

trainingValidation.py --input-data <input measures data file> --reference-rate <minimum accuracy desired> --rate-step <step of decreasing of the reference rate for scrap round> [--selected-measures <'zip gzip bzip2 LZWHuffman entropy'> --max-memory <maximum amount of memory to be used> --number-processes <number of parallel processes>]

PARÂMETROS

EXEMPLO


#### trainingReportValidation.py

SINTAXE
trainingReportValidation.py --input-data <file with best scenarios>

PARÂMETROS

EXEMPLO
