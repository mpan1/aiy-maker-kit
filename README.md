# ELEC 392 - Coral Edge TPU Development Kit

This repository contains code, utilities, and examples for developing machine learning applications with the **Coral USB Accelerator** on the Raspberry Pi. It includes the modified AIY Maker Kit, pre-built object detection scripts, and model training tutorials for ELEC 392 students.

## ⚠️ Critical: Always Use the Virtual Environment

**All code in this repository must be executed within the Python virtual environment created by the `setup_coral.sh` script.** This venv uses Python 3.9 with pinned, older versions of TensorFlow and dependencies specifically tested with the Coral Edge TPU. Running code with system Python will fail.

### Activating the Virtual Environment

After running `setup_coral.sh`, activate the Coral environment:

```bash
source ~/dev/coral/.venv/bin/activate
```

You should see `(.venv)` in your terminal prompt. All commands in this repository must be run with this environment active.

## Overview

This repo provides three main capabilities:

1. **Model Training** - Google Colab notebooks to train custom object detection models
2. **Real-time Detection** - Scripts to run inference on the Raspberry Pi with Coral TPU
3. **Inter-Process Communication** - UDP-based detection sharing between the Coral TPU pipeline and PiCar-X autonomous control

## Workflow

### 1. Train a Custom Model (Google Colab)

Use the tutorials in `model_training_tutorials/` to help you train object detection models:

- **Road Sign Detector**: `model_training_tutorials/road_sign_detector/`
- **Salad Detector**: `model_training_tutorials/salad_detector/`

These notebooks run in **Google Colab** (free GPU/TPU) and output:
- `*.tflite` - Uncompiled model
- `*_edgetpu.tflite` - Coral-optimized model
- `*-labels.txt` - Label file

### 2. Deploy to Raspberry Pi

Transfer your trained model to the Raspberry Pi:

```bash
scp my_model_edgetpu.tflite pi@<pi-ip>:~/elec392_project/
scp my_labels.txt pi@<pi-ip>:~/elec392_project/
```

### 3. Run Detection Scripts

There are two detection modes:

#### Option A: Visual Inspection (Testing)

```bash
# Activate venv
source ~/dev/coral/.venv/bin/activate

# Visualize detections with bounding boxes
python projects/object_detector_visual.py \
    --model my_model_edgetpu.tflite \
    --labels my_labels.txt \
    --confidence 0.5
```

Use this to debug and tune your model before autonomous deployment.

#### Option B: Send Detections to PiCar-X (Autonomous Mode)

The Coral detection pipeline and PiCar-X control code run in separate Python environments (different venvs or system Python). They communicate via **UDP sockets on localhost** (`127.0.0.1:5005`):

**Terminal 1 - Coral TPU Detection:**
```bash
source ~/dev/coral/.venv/bin/activate
cd ~/elec392_project
python projects/object_detector_udp.py \
    --model my_model_edgetpu.tflite \
    --labels my_labels.txt \
    --confidence 0.5
```

**Terminal 2 - PiCar-X Autonomous Control:**
```bash
cd ~/elec392_project
python examples/06_recieve_detections_udp.py
```

The PiCar-X control code receives detection data and reacts accordingly (steer, stop, etc.).

## Project Structure

```
elec392-coral-starter-kit/
├── aiymakerkit/                    # Modified AIY Maker Kit library
├── model_training_tutorials/       # Google Colab notebooks for model training
│   ├── road_sign_detector/
│   │   ├── ELEC 392 - EfficientDet-Lite Detector...ipynb
│   │   ├── train_road_signs_model.py
│   │   └── test_road_signs_model.py
│   └── salad_detector/
│       └── ELEC 392 - EfficientDet-Lite Detector...ipynb
├── projects/                       # Detection scripts for Raspberry Pi
│   ├── object_detector_visual.py   # Visualize detections (debug/test)
│   ├── object_detector_udp.py      # Send detections via UDP (autonomous)
│   ├── security_camera.py          # Example: perimeter detection
│   └── smart_camera.py             # Example: smart camera application
├── ipc/                            # Inter-process communication utilities
│   └── udp.py                      # UDP detection sender/receiver
├── examples/                       # pycoral examples from Google
└── scripts/                        # Utility scripts
```

## Setup Instructions

### 1. On Your Computer - Train a Model

1. Open a notebook from `model_training_tutorials/` in Google Colab
2. Follow the instructions to train your custom model
3. Download the compiled model and labels file

### 2. On Raspberry Pi - Install Coral Environment

Run the setup script in the `elec392_project` repository:

```bash
cd ~/dev/elec392_project
bash setup_coral.sh
```

This automatically:
- Installs Python 3.9 via pyenv
- Creates a dedicated venv at `~/dev/coral/.venv`
- Installs libedgetpu (Coral USB runtime)
- Installs pycoral, aiymakerkit, and dependencies
- Clones this repository into `~/dev/coral/elec392-coral-starter-kit`

### 3. Transfer Your Model to Raspberry Pi

```bash
scp my_model_edgetpu.tflite pi@<pi-ip>:~/elec392_project/
scp my_labels.txt pi@<pi-ip>:~/elec392_project/
```

### 4. Run Detection

See **Workflow** section above.

## Architecture: Why Two Environments?

- **Coral venv** (`~/dev/coral/.venv`): Runs TensorFlow + pycoral on Python 3.9. Detects objects from camera.
- **System Python**: Runs PiCar-X control code (picar-x library, servo control). May use different dependencies.

These communicate via **UDP localhost sockets**:

```
Camera Feed
    ↓
[Coral venv - object_detector_udp.py] ← TensorFlow + pycoral on Python 3.9
    ↓ (UDP to 127.0.0.1:5005)
[System Python - elec392_project] ← PiCar-X control code
    ↓
Motor/Servo Control
```

This separation ensures:
- No dependency conflicts between TensorFlow (Coral) and picar-x libraries
- Coral TPU inference is isolated and stable
- Clean inter-process communication

## Common Commands

```bash
# Activate Coral environment
source ~/dev/coral/.venv/bin/activate

# Check TPU is connected
python ~/dev/coral/list_tpus.py

# Visualize detections (test a model)
cd ~/elec392_project
python projects/object_detector_visual.py --model model.tflite --labels labels.txt

# Run object detection + UDP broadcast (for autonomous mode)
python projects/object_detector_udp.py --model model.tflite --labels labels.txt

# Receive detections in PiCar-X control code
python examples/06_recieve_detections_udp.py
```

## Troubleshooting

**Q: "Command not found: python" or dependency errors**
- A: Make sure the venv is activated: `source ~/dev/coral/.venv/bin/activate`

**Q: "TPU_NOT_DETECTED" when running list_tpus.py**
- A: Check Coral USB Accelerator is plugged in, try a different USB port/cable, or run `lsusb | grep Google`

**Q: ModuleNotFoundError for TensorFlow/pycoral**
- A: Ensure venv is activated and `setup_coral.sh` completed successfully

**Q: UDP detection data not received in PiCar-X code**
- A: Ensure both processes (object_detector_udp.py and 06_recieve_detections_udp.py) are running simultaneously

## Learn More

- [Coral Edge TPU Docs](https://coral.ai/)
- [TensorFlow Lite](https://www.tensorflow.org/lite)
- [AIY Maker Kit Documentation](https://aiyprojects.withgoogle.com/maker/)
- [ELEC 392 Course Resources](https://elec392.gitbook.io/)

## AIY Maker Kit Python API and examples

The aiymakerkit API greatly simplifies the amount of code needed to
perform common operations with TensorFlow Lite models, such as performing image
classification, object detection, pose estimation, and speech recognition
(usually in combination with the Coral Edge TPU).

This repo also includes
scripts to collect training images and perform transfer learning with an image
classification model, directly on your device (such as a Raspberry Pi).

This project was designed specifically for the
[AIY Maker Kit](https://aiyprojects.withgoogle.com/maker/), which uses a
Raspberry Pi with a Coral USB Accelerator, camera, and microphone.

## Learn more

To get started, see the [AIY Maker Kit documentation](https://aiyprojects.withgoogle.com/maker/).
It includes complete setup instructions with a Raspberry Pi, project tutorials,
and the **[aiymakerkit API reference](https://aiyprojects.withgoogle.com/maker/#reference)**.


## Install on Raspberry Pi OS (Don't do this in ELEC 392)

If you're on a Raspberry Pi, we recommend you flash our custom Raspberry Pi OS
system image before installing this library, as documented at
https://aiyprojects.withgoogle.com/maker/. That way, you're sure to have
all the required software installed and there should be no trouble.

But if you want to do things differently and can tolerate some extra steps and risk troubleshooting,
you can build our system image yourself and/or install the required libraries
on an existing RPI OS system as documented at
https://github.com/google-coral/aiy-maker-kit-tools (but we
do not recommend it).


## Install manually

For other situations where you want to install only the `aiymakerkit` library,
**you must manually install the `libedgetpu` and `pycoral` libraries first**.
Assuming that you are also using the Coral USB
Accelerator, you can get these libraries by following the [Coral USB Accelerator
setup guide at coral.ai](https://coral.ai/docs/accelerator/get-started/).

Then you can clone this repo and install the library as follows:

```
git clone https://github.com/google-coral/aiy-maker-kit.git

cd aiymakerkit

python3 -m pip install .
```
