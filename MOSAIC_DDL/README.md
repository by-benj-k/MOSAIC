# MOSAIC_DDL - a Dataset Synthesis Framework

We introduce MOSAIC - **M**odular **O**mni-domain **S**ynthesis for **A**rtificial **I**nstance **C**onstruction - a dataset synthesis framework that allows the generation of artificial training data tailored to the user's requirements. It also supports a range of evaluation methods designed to help users understand verbatim and non-verbatim memorization in their chosen LLMs.
## Features

- **D**ataset **D**efinition **L**anguage: specify your custom dataset in an .xml, provide some sampling functions and let the framework do the rest.
- EII selection to control the amount/complexity of personally identifiable information.
- Frequency selection to control how often the attribute is sampled during document generation.
- Co-Occurrence adjustment between entities and between attributes.
- Precise control over which domain attributes or entity attributes are allowed in which text type and how many seeds per text type and documents per seed should be generated.
- Fine-tuning script for Llama-3.1-8B-Instruct.
- Evaluation of verbatim and non-verbatim memorization through Q&A knowledge extraction and prefix extraction attacks.
- A very diverse sample instantiation of the framework which can be found in "MOSAIC_DDL/sample_code/". It provides a diverse selection of domains and supports a variety of text types.
## Getting Started

Please have a look at the sample code in "MOSAIC_DDL/sample_code/" to learn about the specific structure of the .xml file (look at the "MOSAIC_DDL/sample_code/README.md" to get a sample instantiation quickly up and running). A file in which you can register the sampling functions for your dataset will be generated once you start the framework for the first time after having created the .xml file. Make sure not to specify any cyclic relations and register a sampling function for every domain as the framework will otherwise abort with an error!
## Limitations

- An OpenRouter API key with sufficient credit (depending on the selected size of the dataset to be generated) is required.
- The diversity of the generated texts is strongly related to the underlying selection of datasets. The larger these are, the more diverse the generated texts (and vice versa).
- The values of the attributes are not necessarily unique. If you wish to have unique values, you must take care of this yourself in the sampling procedures.
- Currently, only the co-occurrence relation is supported. Other types of relations might follow in the future.
- Currently, you are allowed to have strings, integers/floats or lists of integers/floats as values of attributes. Other constructs might crash the framework.
## Authors

- [@by-benj-k](https://github.com/by-benj-k)