# Pattern Recognition by Randomness (PRR)
PRR is a machine learning technique for scenes classification that explores the image randomness after data transformations. These transformations are based on the relationship between natural perception of randomness and Kolmogorov's Theory. The more complex the stimulus, the more random it will be perceived. The image data transformations are performed using a lossy compression technique, called Vector Quantization. The quantization eliminates details and expands characteristics, turning the scene more complex. After the transformations, the image randomness is measured using lossless compression as an approximation of Kolmogorov Complexity. In a problem with 12 classes, PRR yielded 0.6967 of accuracy with Shannon's entropy and 0.6350 with compression.

The PRR was developed in the PhD Thesis supervised by Professor PhD Anderson da Silva Soares.

Feitosa, R. D. F. (2020). Scene classification using randomness analysis by approximation of Kolmogorov's complexity. Institute of Informatics, Federal University of Goiás.

The available source code was implemented in Python 2.7 and tested on Linux-based systems.

## Directories structure
```bash
- prr
- ├── codes
- │   └── include
- ├── dataset
- │   ├── images
- │   ├── partitionA
- │   ├── partitionB
- │   └── partitionC
- └── trainedModels
-     ├── partitionA
-     ├── partitionB
-     └── partitionC
```
   
The **codes** directory contains the scripts for all the method steps described below, as well as auxiliary functions. The **dataset** directory contains the images used in the experiments and 3 suggestions for partitioning between training and test sets. The **trainedModels** directory contains models trained in each of the suggested partitions and the best training parameters for each class.

## PRR architecture
![](https://github.com/rdffeitosa/prr/blob/master/prr.png)

The figure above describes the main steps of the PRR, grouped in *Training* and *Classification Modules*. The basis of the *Training Module* is *step #1*, *Prototyping*. In the *Prototyping*, the training images provide samples for a heuristic designed for obtaining class prototypes (*codevectors*) organized in *codebooks*. The *codebook* consists of different block sizes and number of prototypes, defined in parameters. In *step #2*, *Quantization*, the training images are reconstructed with the *codevectors* obtained in the previous step. A measure of information complexity is calculated in *step #3*, *Measurement*. The best training parameters for each class are selected in *step #4*, *Validation*. These validated parameters are applied over *Classification Module* in *step #5*, *Quantization* of the test images. Finally, in *step #6*, the decision process for the test samples is performed. Each of these steps was implemented in Python scripts available in the *codes* directory and will be detailed below.

## Dataset
The GHIM-10k dataset [1] was used, originally composed of 20 scene categories, each one with 500 images of dimensions 400x300 or 300x400 pixels in JPEG format. Twelve classes were selected, with 100 images each, from the original dataset: *tree, aircraft, field, car, building, moto-racing, flower, firework, mountain, motorcycle, sunset and beach. Some classes were selected so that contained common elements, to avoid biased models. The figure below shows a sample of each class used in the experiments.

![](https://github.com/rdffeitosa/prr/blob/master/dataset/dataset.png)

[1] Liu, Guang-Hai *et al.*. Content-based image retrieval using computational visual attention model, Pattern Recognition, 48(8) (2015) 2554-2566.

## Run the PRR

NOTATION
- [...] optional parameter
- '*value_1, value_2, value_n*' (**with comma**) escolha apenas um dos possíveis valoreschoose only one of the possible values
- '*value_1 value_2 value_n*' (**without comma**) alows multiple values

### Classification module
The treined models avaliable in **treinedModels** and the best parameters suggested can be used for classification the images of **dataset**.

#### classifierPRR.py
SYNTAX

classifierPRR.py --input-folder *<folder path with images for classification>* --measure-engine *<zip, gzip, bzip2, LZWHuffman or entropy>* --classes-parameters *<tuple of classes and parameters used for classification between "..."*>* --training-file *<training data file>* --quantization-colors *<number of colors>* [--number-processes *<number of parallel processes>* --id-experiment *<identification of experiments>* archive-results verbose-mode report-mode]

\* The tuples must be in format (('classname', (vector_size, codebook_size)), ('classname', (vector_size, codebook_size)), ..., ('classname', (vector_size, codebook_size)))

- archive-results: maintains directories created in the classification, with images separated by class
- verbose-mode: enables script messages
- report-mode: creates a external file with script's output

EXAMPLE

```
python classifierPRR.py --input-folder ../dataset/partitionA/test --measure-engine entropy --classes-parameters "(('aircrafts', (30, 512)), ('beaches', (5, 128)), ('buildings', (5, 256)), ('cars', (25, 512)), ('fields', (5, 128)), ('fireworks', (30, 256)), ('flowers', (25, 256)), ('moto-racings', (10, 256)), ('motorcycles', (15, 512)), ('mountains', (15, 256)), ('sunsets', (5, 128)), ('trees', (5, 256)))" --training-file ../trainedModels/partitionA/trainingData.pckl.bz2 --quantization-colors 256 --number-processes 4 --id-experiment teste_final archive-results verbose-mode report-mode
```

### Módulo de treinamento

Run the below scripts in ordered sequence to follow the method pipeline. All scripts generate a *pckl.bz2* file with the result that will used in the next step and an auxiliary *txt* file with the execution details. These files are saved in the root of repository */prr*.

#### trainingPrototyping.py
SYNTAX

trainingPrototyping.py --input-folder *<folder path with images for training>* --quantization-colors *<number of colors>* --training-convergence *<convergence value>* [--vectors-sizes *<vectors sizes>* --codebooks-sizes *<number of symbols>* --classes-parameters *<classes and your specific parameters in a list of tuples "(('classname', (vector size, codebook size)), ('classname', (vector size, codebook size)), ..., ('classname', (vector size, codebook size)))">* --number-processes *<number of parallel processes>*]*
  
\* Specify *--vectors-sizes* and *--codebooks-sizes* to train all classes with the same parameters **OR** *--classes-parameters* to determine training parameters individually.

EXAMPLE

```
python trainingPrototyping.py --input-folder ../dataset/partitionA/training --quantization-colors 256 --vectors-sizes '5 10 15 20 25 30' --codebooks-sizes '64 128 256 512' --training-convergence 0.1 --number-processes 4
```
```
python trainingPrototyping.py --input-folder ../dataset/partitionA/training --quantization-colors 256 --classes-parameters "(('aircrafts', (30, 512)), ('beaches', (5, 128)), ('buildings', (5, 256)), ('cars', (25, 512)), ('fields', (5, 128)), ('fireworks', (30, 256)), ('flowers', (25, 256)), ('moto-racings', (10, 256)), ('motorcycles', (15, 512)), ('mountains', (15, 256)), ('sunsets', (5, 128)), ('trees', (5, 256)))" --training-convergence 0.1 --number-processes 4
```

#### trainingQuantization.py
SYNTAX

trainingQuantization.py --input-folder *<input folder with images for quantization>* --quantization-colors *<number of colors>* --training-file *<training data file>* [--number-processes *<number of parallel processes>*]

EXAMPLE

```
python trainingQuantization.py --input-folder ../dataset/partitionA/training --quantization-colors 256 --training-file ../trainingData.pckl.bz2 --number-processes 4
```

#### trainingMeasurement.py
SYNTAX

trainingMeasurement.py --input-data *<input with quantizations data file>* [--training-file *<training data file>*]* --measure-engines *<'zip gzip bzip2 LZWHuffman entropy'>* [--number-processes *<number of parallel processes>*]
  
\* If using only the *entropy* measure in *--measure-engines* isn't necessary to specify *--training-file*.

EXAMPLE

```
python trainingMeasurement.py --input-data ../quantizationsData.pckl.bz2 --training-file ../trainingData.pckl.bz2 --measure-engines 'zip gzip bzip2 LZWHuffman entropy' --number-processes 4
```

#### trainingValidation.py
SYNTAX

trainingValidation.py --input-data *<input measures data file>* --reference-rate *<minimum accuracy desired>* --rate-step *<step of decreasing of the reference rate for scrap round>* [--selected-measures *<'zip gzip bzip2 LZWHuffman entropy'>* --max-memory *<maximum amount of memory to be used>* --number-processes *<number of parallel processes>*]

EXAMPLE

```
python trainingValidation.py --input-data ../measurementsData.pckl.bz2 --reference-rate 0.9 --rate-step 0.1 --selected-measures 'zip gzip bzip2 LZWHuffman entropy' --max-memory 0.7 --number-processes 4
```

#### trainingReportValidation.py

SYNTAX
trainingReportValidation.py --input-data *<file with best scenarios>*
  
* Use the suggested parameter tuples for the classes to run the script *classifierPRR.py*

EXAMPLE

```
python trainingReportValidation.py --input-data ../bestScenarios.pckl.bz2
```
