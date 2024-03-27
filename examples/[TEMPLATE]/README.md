# [insert model name] Optimization with [insert EP]
This sample shows how to optimize [insert model name w/ Hugging Face model link] on [insert device / EP name] with Olive using ONNX Runtime tools.

The optimization pipeline performed is as follows:

*PyTorch Model* &rarr; *ONNX Model* &rarr; *Transformers Optimized ONNX Model* &rarr; *[insert quantization / precision] Quantized ONNX Model*

**Contents:**
- [Pre-Requisites]([TEMPLATE]#Pre-Requisites)
- [Setup]([TEMPLATE]#Setup)
- [Run Optimization]([TEMPLATE]#Run)
- [Test Inference]([TEMPLATE]#Test)
- [Known Issues (if necessary)]([TEMPLATE]#Known)

## Pre-Requisites
- transformers>=[insert version #]
- optimum>=[insert version #]
- onnxruntime>=[insert version #]

## Setup
Install Olive and the necessary requirements as follows:
```
conda create -n olive python=[insert python version #] -y
conda activate olive
git clone https://github.com/microsoft/Olive.git
cd Olive
pip install -e .
cd examples/[insert example path]
pip install -r requirements.txt
```

*Note: In the above steps, please run the following command in Administrator command prompt if you hit "Filename too long" when installing the packages.*
```
git config --system core.longpaths true
```

## Run Optimization
To optimize the model, run the following:
```
python [insert model .py file name] --optimize --config [insert model .json file name]
```

*Note: You can run the optimization for a locally saved model by setting the `model_id` to the path of the model.*

## Test Inference
To test inference on the model, run the optimization script with `–inference` as follows:
```
python [insert model .py file name]  --config [insert model .json file name] --inference
```

*Notes:*
- *You can provide your own prompts using `--prompt argument`. For example:*
  ```
  python [insert model .py file name] --config [insert model .json file name] --inference --prompt "Language models are very useful" "What is the meaning of life?"
  ```
- *`--max_length` can be used to specify the maximum length of the generated sequence.*
- *Use `CUDA_VISIBLE_DEVICES` to specify the GPU to run the inference on. For example:*
  ```
  CUDA_VISIBLE_DEVICES=6 python [insert model .py file name] --config [insert model .json file name] --inference
  ```

## Known Issues (as necessary)
