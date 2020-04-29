# Pattern Recognition by Randomness (PRR)
PRA is a machine learning technique for scenes classification that explores the randomness caused by data transformations in images. These transformations are based on the relationship between natural perception of randomness and Kolmogorov's Theory. The more complex the stimulus, the more random it will be perceived. The data transformations performed in the images use a lossy compression technique, called vector quantization. Quantization is responsible for eliminating details and expanding characteristics, making the scene more complex. After these transformations, randomness is measured using lossless compression as an approximation of Kolmogorov Complexity. In a problem with 12 classes, PRA yielded an accuracy of 0.6967 with Shannon's entropy and 0.6350 with compression.

PhD Thesis

Feitosa, R. D. F. (2020). Scene classification using randomness analysis by approximation of Kolmogorov's complexity. Institute of Informatics, Federal University of Goiás.

The source code available was coded in Python 2.7 and tested on Linux-based systems.

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

NOTAÇÃO
- [...] parâmetro opcional
- '*value_1, value_2, value_n*' (**com vírgula**) escolha apenas um dos possíveis valores
- '*value_1 value_2 value_n*' (**sem vírgula**) permite múltiplos valores

### Módulo de classificação
Os modelos pré-treinados disponíveis em **treinedModels** e as sugestões de melhores parâmatros podem ser utilizados para classificar as imagens disponíveis no diretório **dataset**

#### classifierPRR.py
SINTAXE

classifierPRR.py --input-folder *<folder path with images for classification>* --measure-engine *<zip, gzip, bzip2, LZWHuffman or entropy>* --classes-parameters *<tuple of classes and parameters used for classification between "..."*>* --training-file *<training data file>* --quantization-colors *<number of colors>* [--number-processes *<number of parallel processes>* --id-experiment *<identification of experiments>* archive-results verbose-mode report-mode]

\* As tuplas devem ser no formato (('classname', (vector_size, codebook_size)), ('classname', (vector_size, codebook_size)), ..., ('classname', (vector_size, codebook_size)))

- archive-results: mantém os diretórios criados durante a classificação com as imagens separadas por classe
- verbose-mode: ativa as mensagens do script
- report-mode: cria um arquivo externo com a saída do script

EXEMPLO

```
python classifierPRR.py --input-folder ../dataset/partitionA/test --measure-engine entropy --classes-parameters "(('aircrafts', (30, 512)), ('beaches', (5, 128)), ('buildings', (5, 256)), ('cars', (25, 512)), ('fields', (5, 128)), ('fireworks', (30, 256)), ('flowers', (25, 256)), ('moto-racings', (10, 256)), ('motorcycles', (15, 512)), ('mountains', (15, 256)), ('sunsets', (5, 128)), ('trees', (5, 256)))" --training-file ../trainedModels/partitionA/trainingData.pckl.bz2 --quantization-colors 256 --number-processes 4 --id-experiment teste_final archive-results verbose-mode report-mode
```

### Módulo de treinamento

Execute os scripts desse módulo em ordem para seguir o pipeline do método. Todos os scripts geram um arquivo *pckl.bz2* com o resultado e um arquivo auxiliar *txt* com os detalhes da execução. Esses arquivos são gerados na raiz do repositório  */prr*.

#### trainingPrototyping.py
SINTAXE

trainingPrototyping.py --input-folder *<folder path with images for training>* --quantization-colors *<number of colors>* --training-convergence *<convergence value>* [--vectors-sizes *<vectors sizes>* --codebooks-sizes *<number of symbols>* --classes-parameters *<classes and your specific parameters in a list of tuples "(('classname', (vector size, codebook size)), ('classname', (vector size, codebook size)), ..., ('classname', (vector size, codebook size)))">* --number-processes *<number of parallel processes>*]*
  
\* Especifique *--vectors-sizes* e *--codebooks-sizes* para treinar todas as classes com os mesmos parâmetros **OU** *--classes-parameters* para especificar individualmente os parâmetros de treinamento.

EXEMPLO

```
python trainingPrototyping.py --input-folder ../dataset/partitionA/training --quantization-colors 256 --vectors-sizes '5 10 15 20 25 30' --codebooks-sizes '64 128 256 512' --training-convergence 0.1 --number-processes 4
```
```
python trainingPrototyping.py --input-folder ../dataset/partitionA/training --quantization-colors 256 --classes-parameters "(('aircrafts', (30, 512)), ('beaches', (5, 128)), ('buildings', (5, 256)), ('cars', (25, 512)), ('fields', (5, 128)), ('fireworks', (30, 256)), ('flowers', (25, 256)), ('moto-racings', (10, 256)), ('motorcycles', (15, 512)), ('mountains', (15, 256)), ('sunsets', (5, 128)), ('trees', (5, 256)))" --training-convergence 0.1 --number-processes 4
```

#### trainingQuantization.py
SINTAXE

trainingQuantization.py --input-folder *<input folder with images for quantization>* --quantization-colors *<number of colors>* --training-file *<training data file>* [--number-processes *<number of parallel processes>*]

EXEMPLO

```
python trainingQuantization.py --input-folder ../dataset/partitionA/training --quantization-colors 256 --training-file ../trainingData.pckl.bz2 --number-processes 4
```

#### trainingMeasurement.py
SINTAXE

trainingMeasurement.py --input-data *<input with quantizations data file>* [--training-file *<training data file>*]* --measure-engines *<'zip gzip bzip2 LZWHuffman entropy'>* [--number-processes *<number of parallel processes>*]
  
\* Caso utilize apenas a medida *entropy* em *--measure-engines* não é necessário especificar *--training-file*

EXEMPLO

```
python trainingMeasurement.py --input-data ../quantizationsData.pckl.bz2 --training-file ../trainingData.pckl.bz2 --measure-engines 'zip gzip bzip2 LZWHuffman entropy' --number-processes 4
```

#### trainingValidation.py
SINTAXE

trainingValidation.py --input-data *<input measures data file>* --reference-rate *<minimum accuracy desired>* --rate-step *<step of decreasing of the reference rate for scrap round>* [--selected-measures *<'zip gzip bzip2 LZWHuffman entropy'>* --max-memory *<maximum amount of memory to be used>* --number-processes *<number of parallel processes>*]

EXEMPLO

```
python trainingValidation.py --input-data ../measurementsData.pckl.bz2 --reference-rate 0.9 --rate-step 0.1 --selected-measures 'zip gzip bzip2 LZWHuffman entropy' --max-memory 0.7 --number-processes 4
```

#### trainingReportValidation.py

SINTAXE
trainingReportValidation.py --input-data *<file with best scenarios>*
  
* Utilize as tuplas de parâmetros sugeridas para as classes para executar o script *classifierPRR.py*

EXEMPLO

```
python trainingReportValidation.py --input-data ../bestScenarios.pckl.bz2
```
