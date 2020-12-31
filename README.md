mtg_bert is interface for using Bidirectional Encoder Representations from Transformers (BERT) to search for synergies between Magic: the Gathering cards.
To run it you will need [Anaconda](https://anaconda.org/). [Nvidia'a CUDA](https://developer.nvidia.com/CUDA-zone) is also strongly recommended.<br/>
To download:

```
git clone https://github.com/Sajemiur/mtg_bert.git
cd mtg_bert
conda env create -f environment.yml
```
BERT model is not included in this repository and has to be loaded from [here](https://drive.google.com/file/d/1roRkkLNFfptbX7tkbBvrRWQTlD_MQzLe/view?usp=sharing) and saved in mtg folder.<br/>
To run:
```
conda activate mtgenv
uvicorn mtg_django.asgi:application --ws websockets
```
