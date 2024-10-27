# SyntaxError

Project Description

## 1. Clone the repository

To get started, clone this repository using the following command:

```bash
git clone https://github.com/DiscoverVoice/SyntaxError.git
cd SyntaxError
```

## 2. Installation

### 2.1 Install poetry for python projects

First, install Poetry to manage the Python dependencies:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Once installed, confirmed the Poetry installation by checking the version:

```bash
poetry --version
```

Next, install the Python dependencies and active the virtual environment:

```bash
poetry install
poetry shell
```

### 2.2 Install npm modules for JS/TS projects

```bash
npm install
```

### 2.3 Install afl

```bash
git submodule update --init
cd src/utils/AFLplusplus
make distrib
sudo make install
```


## 3. How to debug Extension prototype

1. press f5
2. crt + shift + p 
3. Enter "Show Menu"
4. To start new work, choose "Ask ChatGPT". Then write an explanation about your code request
5. To load last work, choose "Load works". Then select your previous works with date and time
6. To verify the generated codes, choose "QA Test" and "Fuzzing". This function is not completed yet
