# [model name] Optimization with [EP]
This sample shows how to optimize [model name + insert HF link] on [device / EP name] with Olive using ONNX Runtime tools.

The optimization pipeline performed is as follows:

*PyTorch Model* --> *ONNX Model* --> *Transformers Optimized ONNX Model* --> *[insert quantization / precision] Quantized ONNX Model*

**Contents:**
- [Pre-Requisites]([TEMPLATE]#Pre-Requisites)
- [Setup]([TEMPLATE]#Setup)
- [Run Optimization]([TEMPLATE]#Run Optimization)
- [Test Inference]([TEMPLATE]#Test Inference)
- [Known Issues (if necessary)]([TEMPLATE]#Known Issues (if necessary))

## Pre-Requisites
- transformers>=[insert version #]
- optimum>=[insert version #]
- onnxruntime>=[insert version #]

## Setup
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
```
python [insert model .py file name] --optimize --config [insert model .json file name]
```

*Note: You can run the optimization for a locally saved model by setting the `model_id` to the path of the model.*

## Test Inference
To test inference on the model, run the script with `–inference`:
```
python [insert model .py file name]  --config [insert model .json file name] --inference
```

*Notes:*
- You can provide your own prompts using `--prompt argument`. For example:
  ```
  python [insert model .py file name] --config [insert model .json file name] --inference --prompt "Language models are very useful" "What is the meaning of life?"
  ```
- `--max_length` can be used to specify the maximum length of the generated sequence.
- Use `CUDA_VISIBLE_DEVICES` to specify the GPU to run the inference on. For example:
  ```
  CUDA_VISIBLE_DEVICES=6 python [insert model .py file name] --config [insert model .json file name] --inference
  ```

## Known Issues (as necessary)
