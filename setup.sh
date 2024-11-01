#!/bin/bash

# Set non-interactive mode for package installations
DEBIAN_FRONTEND=noninteractive

# Variables
LLVM_VERSION=14
GCC_VERSION=11

# Update and upgrade system packages
apt-get update && apt-get full-upgrade -y && \
    apt-get install -y --no-install-recommends wget ca-certificates apt-utils && \
    rm -rf /var/lib/apt/lists/*

# Add LLVM repository and key
echo "deb [signed-by=/etc/apt/keyrings/llvm-snapshot.gpg.key] http://apt.llvm.org/jammy/ llvm-toolchain-jammy-${LLVM_VERSION} main" > /etc/apt/sources.list.d/llvm.list && \
    wget -qO /etc/apt/keyrings/llvm-snapshot.gpg.key https://apt.llvm.org/llvm-snapshot.gpg.key

# Install development tools and dependencies
add-apt-repository -y ppa:deadsnakes/ppa

apt-get update && \
    apt-get -y install --no-install-recommends \
        build-essential automake cmake git flex bison \
        ninja-build lld-${LLVM_VERSION} llvm-${LLVM_VERSION} clang-${LLVM_VERSION} \
        gcc-${GCC_VERSION} g++-${GCC_VERSION} gcc-${GCC_VERSION}-plugin-dev \
        libstdc++-${GCC_VERSION}-dev libglib2.0-dev libpixman-1-dev \
        libcapstone-dev python3-setuptools cargo libgtk-3-dev gnuplot-nox bc \
        python3.12 python3.12-dev python3.12-pip python-is-python3 \
        libtool libtool-bin apt-transport-https gnupg dialog cpio \
        xz-utils bzip2 nano bash-completion less vim joe ssh psmisc \
        wget curl && \
    rm -rf /var/lib/apt/lists/*

# Configure alternatives for gcc, g++, clang, clang++
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-${GCC_VERSION} 0 && \
update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-${GCC_VERSION} 0 && \
update-alternatives --install /usr/bin/clang clang /usr/bin/clang-${LLVM_VERSION} 0 && \
update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-${LLVM_VERSION} 0

# Install Rust
wget -qO- https://sh.rustup.rs | CARGO_HOME=/etc/cargo sh -s -- -y -q --no-modify-path
export PATH=$PATH:/etc/cargo/bin

# Clean up package cache
apt clean -y

cd src/utils/
git clone https://github.com/AFLplusplus/AFLplusplus
sudo chmod -R 777 ./AFLplusplus

# Clone and install afl-cov
git clone --depth=1 https://github.com/vanhauser-thc/afl-cov && \
    (cd afl-cov && make install) && rm -rf afl-cov

# Set up AFLplusplus environment variables
export LLVM_CONFIG=llvm-config-${LLVM_VERSION}
export AFL_SKIP_CPUFREQ=1
export AFL_TRY_AFFINITY=1
export AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1


# Copy AFLplusplus source code and build
WORKDIR=/AFLplusplus
cp -r ./AFLplusplus/utils/autodict_ql ./
cp -r ./AFLplusplus ${WORKDIR}

# Build AFLplusplus
sed -i.bak 's/^	-/	/g' ${WORKDIR}/GNUmakefile && \
    cd ${WORKDIR} && make clean && make source-only && \
    mv GNUmakefile.bak GNUmakefile

sudo rm -rf ./AFLplusplus

# Configure shell environment for ease of use
echo "set encoding=utf-8" > /root/.vimrc && \
echo ". /etc/bash_completion" >> ~/.bashrc && \
echo 'alias joe="joe --wordwrap --joe_state -nobackup"' >> ~/.bashrc && \
echo "export PS1='[AFL++ \h] \w \$ '" >> ~/.bashrc
echo 'export PATH="$PATH:/AFLplusplus"' >> ~/.bashrc


# Install audodict ql
cd src/utils/
mkdir codeql-home
cd codeql-home
git clone https://github.com/github/codeql.git codeql-repo
git clone https://github.com/github/codeql-go.git
wget https://github.com/github/codeql-cli-binaries/releases/download/v2.19.2/codeql-linux64.zip
unzip codeql-linux64.zip 
mv codeql codeql-cli
export PATH="$PWD/codeql-cli/:$PATH"
echo "export PATH=\"$(pwd)/codeql-cli:\$PATH\"" >> ~/.bashrc
codeql resolve languages
codeql resolve qlpacks
codeql
source ~/.bashrc
