# Learn to build my First Docker

2026/3/19

前情提要：因为wwxq需要一个VLN/VLA的验证环境，所以抓了我这个嗨奴去看CVPR25 UniGoal这篇文章。要对齐qy本地的环境和wwxq的环境，那就只能用docker的形式了。虽然我本人对这个活很瞧不上（这个论文的环境不可能支撑得起公司那边的需求），但是因为自己从来没有搞过这种事（打docker），也算比较感兴趣，所以姑且看看该怎么搞，把这个过程固化下来。

## 基础命令
### 构建Dockerfile
* 在`Dockerfile`文件同级路径下执行以下命令：
    ```bash
    docker build -t my-cuda-env .
    ```
    * `-t my-cuda-env`：给镜像起名字，可以加个`:tag`来标识不同的版本；
    * `.`：当前目录（包含 Dockerfile）

### 运行docker
* 通过以下命令来运行docker：
    ```bash
    docker run --gpus all -it --rm my-cuda-env
    ```
    * `--gpus all`：使用 GPU（关键！）
    * `-it`：交互模式
    * `--rm`：退出自动删除容器
    * `my-cuda-env`：刚 build 的镜像


## 开始搭建
### Step 0 - 101 Notes
* docker是可以增量更新的！docker具有缓存机制，可以渐进式build。原则是，如果前面的层不变，后面的层改动时，前面的层会直接复用缓存。如果前面的层没变，就直接用缓存，从哪一层发生变化，就从那一行开始重新build。所以有以下推荐原则：
    1. 把重的、稳定的步骤放前面，比如FROM、apt-get install系统依赖、安装 Python / conda、安装torch；
    2. 把经常改的步骤放后面；
    3. 拆分RUN，让调试更细；
    4. 给不同阶段打tag，比如系统基础层可以起名`-t sxs_test:base`，下一阶段可以起别名叫`-t sxs_test:py`等。
    5. 可以备份多份`Dockerfile`文件，比如`Dockerfile.min`、`Dockerfile.apt`等。
* 因为**Docker里每个RUN是独立shell**，前一行的activate不会传到下一行，所以不要这么写：
    ```docker
    RUN conda activate unigoal
    RUN pip install ...
    ```
    * 而是应该这么写：
    ```docker
    RUN conda run -n unigoal pip install -e third_party/habitat-lab
    ```
* 为了解决docker在build的时候无法访问github的问题，可以将clone和install拆开！在宿主机写一个`bash.sh`文件，里面负责下载和clone，而`Dockerfile`只负责从宿主机拷贝东西和安装：
    ```bash
    #!/usr/bin/env bash
    set -e

    [ -f Miniforge3-Linux-x86_64.sh ] || \
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

    [ -d UniGoal ] || \
    git clone https://github.com/bagh2178/UniGoal.git

    docker build -t unigoal:ver0 .
    ```

### Step 1 - 创建一个Minimal docker
* 在本地新建一个名称为`Dockerfile`的文件，在里面填入以下内容：
    ```docker
    FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

    CMD ["/bin/bash"]
    ```
    其中，
    * `FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04`是直接拿一个已经装好 CUDA 的 Ubuntu 系统；
    * `CMD ["/bin/bash"]`启动容器时默认进入 bash，否则容器会启动就退出（因为没有前台进程）。
* 因为我在反复迭代这个docker，每一次都重新pull基础镜像太慢了，所以有以下两条备选路径：
    * 先提前pull一版基础镜像：
        ```bash
        docker pull nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
        ```
        * 拉完之后，在本地执行`docker images`应该可以看到这个docker；
    * 镜像换源：
        * 在本地新建一个`/etc/docker/daemon.json`文件，并在里面填入以下内容：
            ```json
            {
                bip: 192.168.50.1/24,
                experimental: true,
                registry-mirrors: [
                    https://docker.1ms.run,
                    https://hub.rat.dev,
                    https://docker.1panel.live
                ],
                runtimes: {
                    nvidia: {
                        args: [],
                        path: nvidia-container-runtime
                        }
                    },
                exec-opts: [native.cgroupdriver=cgroupfs],
                default-runtime: nvidia
            }
            ```
        * 接下来重启docker：
            ```bash
            sudo systemctl daemon-reload
            sudo systemctl restart docker
            ```

### Step 2 - 进行一些基础设置
* 在`Dockerfile`里追加这些内容，注意，要在`CMD ["/bin/bash"]`之前（这个是最后的一行内容）：
    ```docker
    ENV DEBIAN_FRONTEND=noninteractive
    WORKDIR /workspace
    ```
    * 其中，`ENV DEBIAN_FRONTEND=noninteractive`的作用是让apt安装软件时不要弹交互界面（不问你问题），因为Docker build是无人值守的，如果某个包弹交互，build会卡住 / 失败。
    * `WORKDIR /workspace`的作用是设置默认工作目录（类似`cd`）
* 接着继续追加以下内容，它的作用是在容器里先换apt源，再安装一批系统级依赖：
    ```docker
    RUN sed -i 's@http://archive.ubuntu.com/ubuntu/@https://mirrors.tuna.tsinghua.edu.cn/ubuntu/@g' /etc/apt/sources.list \
        && sed -i 's@http://security.ubuntu.com/ubuntu/@https://mirrors.tuna.tsinghua.edu.cn/ubuntu/@g' /etc/apt/sources.list \
        && apt-get update \
        && apt-get install -y \
        git wget curl ca-certificates build-essential \
        libglib2.0-0 libsm6 libxext6 libxrender1 libgl1 \
        ffmpeg ninja-build \
        && rm -rf /var/lib/apt/lists/*
    ```
* 接着配置`miniforge`并换源，继续添加以下内容：
    ```docker
    # 安装 Miniforge
    # 如果网络连接不畅，需要从本地取这个包
    # RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O /tmp/miniforge.sh
    COPY Miniforge3-Linux-x86_64.sh /tmp/miniforge.sh
    RUN bash /tmp/miniforge.sh -b -p /opt/conda
    RUN rm /tmp/miniforge.sh
    
    # 配置环境变量
    ENV PATH=/opt/conda/bin:$PATH

    # 换源
    RUN conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge \
        && conda config --set show_channel_urls yes
    ```

### Step 3 - 开始项目相关的配置
* 搭建conda环境：
    ```docker
    RUN mkdir -p /root/.pip && \
        printf "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple\ntrusted-host = pypi.tuna.tsinghua.edu.cn\n" > /root/.pip/pip.conf

    RUN conda create -n unigoal -y python=3.8
    ```
* git clone项目repo：
    ```docker
    RUN git clone https://github.com/bagh2178/UniGoal.git /workspace/UniGoal
    WORKDIR /workspace/UniGoal
    ```
* 搭建`habitat`环境：
    ```docker
    RUN conda install -n unigoal -y habitat-sim==0.2.3 -c conda-forge -c aihabitat
    RUN conda run -n unigoal pip install -e third_party/habitat-lab
    ```
* 安装各种第三方依赖：
    ```docker
    # copy third-party repos prepared on host
    COPY vendor/LightGlue /workspace/vendor/LightGlue
    COPY vendor/detectron2 /workspace/vendor/detectron2
    COPY vendor/pytorch3d /workspace/vendor/pytorch3d
    COPY vendor/Grounded-Segment-Anything /workspace/vendor/Grounded-Segment-Anything

    # install third-party python packages from local source
    RUN conda run -n unigoal pip install /workspace/vendor/LightGlue
    RUN conda run -n unigoal pip install /workspace/vendor/detectron2
    RUN conda run -n unigoal pip install /workspace/vendor/pytorch3d

    # install Grounded-Segment-Anything submodules from local source
    WORKDIR /workspace/vendor/Grounded-Segment-Anything
    RUN conda run -n unigoal pip install -e segment_anything
    RUN conda run -n unigoal pip install --no-build-isolation -e GroundingDINO

    # copy checkpoints into UniGoal expected path
    RUN mkdir -p /workspace/UniGoal/data/models
    COPY assets/models/sam_vit_h_4b8939.pth /workspace/UniGoal/data/models/sam_vit_h_4b8939.pth
    COPY assets/models/groundingdino_swint_ogc.pth /workspace/UniGoal/data/models/groundingdino_swint_ogc.pth
    ```
    * 如果嫌上述`RUN conda run -n <env_name> pip install <package>`命令可视化程度不高（在docker外面看上去就是卡住了），可以改成下面的命令，直接用pip装：
        ```docker
        RUN /opt/conda/envs/<env_name>/bin/pip install -v <package>
        ```
* 最后再安装项目相关的依赖：
    ```docker
    # install faiss-gpu & project requirements
    RUN conda install -n unigoal -y -c pytorch faiss-gpu
    WORKDIR /workspace/UniGoal
    RUN conda run -n unigoal pip install -v --progress-bar off -r requirements.txt
    # sanity check
    RUN conda run -n unigoal python -c "import faiss; print('faiss ok')"
    ```

### Step 4 - 组织数据集文件并挂载运行docker
* 准备一个数据下载的bash脚本，详略；该脚本的作用是下载数据集后，按照项目要求组织目录；
* 将宿主机的数据目录挂载到docker中，执行以下命令：
    ```bash
    docker run --gpus all -it --rm \
        -v "$(pwd)/data:/workspace/UniGoal/data" \
        <image_name>:<tag_name> /bin/bash
    ```

### Step 5 - 在宿主机上启动ollama服务，并做端口映射
* 在宿主机上这么启动`ollama`服务，并将它绑定到所有网卡：
    ```bash
    OLLAMA_HOST=0.0.0.0:11434 ollama serve
    ```
* 运行docker时，让容器能解析到宿主机地址：
    ```bash
    docker run --gpus all -it --rm \
        --add-host=host.docker.internal:host-gateway \
        -v "$(pwd)/data:/workspace/UniGoal/data" \
        -w /workspace/UniGoal \
        unigoal:ver0 /bin/bash
    ```

### Finally
* 最终的`Dockerfile`长成这个样子：
    ```docker
    FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

    ENV DEBIAN_FRONTEND=noninteractive
    WORKDIR /workspace

    RUN sed -i 's@http://archive.ubuntu.com/ubuntu/@https://mirrors.tuna.tsinghua.edu.cn/ubuntu/@g' /etc/apt/sources.list \
    && sed -i 's@http://security.ubuntu.com/ubuntu/@https://mirrors.tuna.tsinghua.edu.cn/ubuntu/@g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y \
        git wget curl ca-certificates build-essential \
        vim\
        libglib2.0-0 libsm6 libxext6 libxrender1 libgl1 \
        ffmpeg ninja-build \
    && rm -rf /var/lib/apt/lists/*

    # miniforge  
    # use local file if github inacessible  
    # RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O /tmp/miniforge.sh
    COPY Miniforge3-Linux-x86_64.sh /tmp/miniforge.sh
    RUN bash /tmp/miniforge.sh -b -p /opt/conda
    RUN rm /tmp/miniforge.sh
        
    ENV PATH=/opt/conda/bin:$PATH

    RUN conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge \
    && conda config --set show_channel_urls yes

    # conda env
    RUN mkdir -p /root/.pip && \
        printf "[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple\ntrusted-host = pypi.tuna.tsinghua.edu.cn\n" > /root/.pip/pip.conf

    RUN conda create -n unigoal -y python=3.8

    # repo clone
    # RUN git clone https://github.com/bagh2178/UniGoal.git /workspace/UniGoal
    # if git clone fails, use local files.
    COPY UniGoal /workspace/UniGoal
    WORKDIR /workspace/UniGoal

    # habitat
    RUN conda install -n unigoal -y habitat-sim==0.2.3 -c conda-forge -c aihabitat
    RUN conda run -n unigoal pip install -e third_party/habitat-lab

    # copy third-party repos prepared on host
    COPY vendor/LightGlue /workspace/vendor/LightGlue
    COPY vendor/detectron2 /workspace/vendor/detectron2
    COPY vendor/pytorch3d /workspace/vendor/pytorch3d
    COPY vendor/Grounded-Segment-Anything /workspace/UniGoal/third_party/Grounded-Segment-Anything

    # install third-party python packages from local source
    RUN conda run -n unigoal pip install /workspace/vendor/LightGlue
    RUN conda run -n unigoal pip install /workspace/vendor/detectron2
    RUN conda run -n unigoal pip install /workspace/vendor/pytorch3d

    # install Grounded-Segment-Anything submodules from local source
    WORKDIR /workspace/UniGoal/third_party/Grounded-Segment-Anything
    RUN conda run -n unigoal pip install -e segment_anything
    RUN conda run -n unigoal pip install --no-build-isolation -e GroundingDINO

    # copy checkpoints into UniGoal expected path
    RUN mkdir -p /workspace/UniGoal/data/models
    COPY assets/models/sam_vit_h_4b8939.pth /workspace/UniGoal/data/models/sam_vit_h_4b8939.pth
    COPY assets/models/groundingdino_swint_ogc.pth /workspace/UniGoal/data/models/groundingdino_swint_ogc.pth

    # install faiss-gpu & project requirements
    RUN conda install -n unigoal -y -c pytorch faiss-gpu
    WORKDIR /workspace/UniGoal
    RUN conda run -n unigoal pip install -v --progress-bar off -r requirements.txt
    # sanity check
    RUN conda run -n unigoal python -c "import faiss; print('faiss ok')"


    WORKDIR /workspace/UniGoal
    CMD ["/bin/bash"]
    ```

* 此外，还有搭配的`build.sh`文件：
    ```bash
    #!/usr/bin/env bash
    set -e

    mkdir -p vendor assets/models

    # 1. miniforge
    [ -f Miniforge3-Linux-x86_64.sh ] || \
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

    # 2. unigoal
    [ -d UniGoal ] || \
    git clone https://github.com/bagh2178/UniGoal.git

    # 3. LightGlue
    if [ ! -d vendor/LightGlue ]; then
    git clone https://github.com/cvg/LightGlue.git vendor/LightGlue
    fi

    # 4. detectron2
    if [ ! -d vendor/detectron2 ]; then
    git clone https://github.com/facebookresearch/detectron2.git vendor/detectron2
    fi

    # 5. pytorch3d
    if [ ! -d vendor/pytorch3d ]; then
    git clone https://github.com/facebookresearch/pytorch3d.git vendor/pytorch3d
    fi

    # 6. Grounded-Segment-Anything
    if [ ! -d vendor/Grounded-Segment-Anything ]; then
    git clone https://github.com/IDEA-Research/Grounded-Segment-Anything.git vendor/Grounded-Segment-Anything
    cd vendor/Grounded-Segment-Anything
    git checkout 5cb813f
    cd ../../
    fi

    # double check the branch
    if [ -d vendor/Grounded-Segment-Anything ]; then
    cd vendor/Grounded-Segment-Anything
    git fetch --all || true
    git checkout 5cb813f
    cd ../../
    fi

    # 7. checkpoints
    if [ ! -f assets/models/sam_vit_h_4b8939.pth ]; then
    wget -O assets/models/sam_vit_h_4b8939.pth \
        https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
    fi

    if [ ! -f assets/models/groundingdino_swint_ogc.pth ]; then
    wget -O assets/models/groundingdino_swint_ogc.pth \
        https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
    fi


    docker build -t unigoal:ver0 .
    ```

* 最后，还有`data_download.sh`文件：
    ```bash
    #!/usr/bin/env bash
    set -euo pipefail

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
    DATA_ROOT="${PROJECT_ROOT}/data"

    HM3D_TAR="${DATA_ROOT}/hm3d-val-habitat-v0.2.tar"
    HM3D_URL="https://api.matterport.com/resources/habitat/hm3d-val-habitat-v0.2.tar"
    IMAGENAV_ZIP="${DATA_ROOT}/instance_imagenav_hm3d_v3.zip"
    IMAGENAV_URL="https://dl.fbaipublicfiles.com/habitat/data/datasets/imagenav/hm3d/v3/instance_imagenav_hm3d_v3.zip"
    TEXTNAV_GDRIVE_ID="1KNdv6isX1FDZi4KCVPiECYDxijg9cZ3L"

    HM3D_ROOT="${DATA_ROOT}/scene_datasets/hm3d_v0.2"
    HM3D_VAL_DIR="${HM3D_ROOT}/val"

    IMAGENAV_ROOT="${DATA_ROOT}/datasets/instance_imagenav/hm3d/v3"
    IMAGENAV_VAL_DIR="${IMAGENAV_ROOT}/val"
    IMAGENAV_NESTED_DIR="${IMAGENAV_ROOT}/instance_imagenav_hm3d_v3"

    TEXTNAV_DIR="${DATA_ROOT}/datasets/textnav/val"
    TEXTNAV_FILE="${TEXTNAV_DIR}/val_text.json.gz"

    mkdir -p "${DATA_ROOT}"
    mkdir -p "${DATA_ROOT}/datasets"
    mkdir -p "${DATA_ROOT}/scene_datasets"
    mkdir -p "${HM3D_VAL_DIR}"
    mkdir -p "${IMAGENAV_ROOT}"
    mkdir -p "${TEXTNAV_DIR}"

    echo "Project root: ${PROJECT_ROOT}"
    echo "Data root: ${DATA_ROOT}"

    ###############################################################################
    # 1) HM3D scenes
    ###############################################################################

    if [ -f "${HM3D_TAR}" ]; then
    echo "[HM3D] Found local tar: ${HM3D_TAR}"
    else
    echo "[HM3D] Local tar not found. Trying to download from Matterport..."
    if command -v wget >/dev/null 2>&1; then
        wget -O "${HM3D_TAR}" "${HM3D_URL}" || true
    elif command -v curl >/dev/null 2>&1; then
        curl -L "${HM3D_URL}" -o "${HM3D_TAR}" || true
    fi
    fi

    if [ -f "${HM3D_TAR}" ]; then
    if [ -z "$(find "${HM3D_VAL_DIR}" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
        echo "[HM3D] Extracting to ${HM3D_VAL_DIR} ..."
        tar -xf "${HM3D_TAR}" -C "${HM3D_VAL_DIR}"
    else
        echo "[HM3D] ${HM3D_VAL_DIR} already contains extracted files, skipping extraction."
    fi
    else
    echo "[HM3D] Download not completed."
    echo "Please manually obtain:"
    echo "  ${HM3D_URL}"
    echo "and place the file at:"
    echo "  ${HM3D_TAR}"
    echo "then rerun this script."
    fi

    ###############################################################################
    # 2) Instance-image-goal episodes
    ###############################################################################

    if [ ! -f "${IMAGENAV_ZIP}" ]; then
    echo "[ImageNav] Downloading instance-image-goal episodes..."
    if command -v wget >/dev/null 2>&1; then
        wget -O "${IMAGENAV_ZIP}" "${IMAGENAV_URL}"
    elif command -v curl >/dev/null 2>&1; then
        curl -L "${IMAGENAV_URL}" -o "${IMAGENAV_ZIP}"
    else
        echo "[ImageNav] Neither wget nor curl is available."
        exit 1
    fi
    else
    echo "[ImageNav] Found local zip: ${IMAGENAV_ZIP}"
    fi

    if [ ! -d "${IMAGENAV_VAL_DIR}" ]; then
    echo "[ImageNav] Extracting to ${IMAGENAV_ROOT} ..."
    unzip -o "${IMAGENAV_ZIP}" -d "${IMAGENAV_ROOT}"

    if [ -d "${IMAGENAV_NESTED_DIR}" ]; then
        echo "[ImageNav] Flattening nested directory ${IMAGENAV_NESTED_DIR} ..."
        if [ -d "${IMAGENAV_NESTED_DIR}/train" ]; then
        mv "${IMAGENAV_NESTED_DIR}/train" "${IMAGENAV_ROOT}/"
        fi
        if [ -d "${IMAGENAV_NESTED_DIR}/val" ]; then
        mv "${IMAGENAV_NESTED_DIR}/val" "${IMAGENAV_ROOT}/"
        fi
        if [ -d "${IMAGENAV_NESTED_DIR}/val_mini" ]; then
        mv "${IMAGENAV_NESTED_DIR}/val_mini" "${IMAGENAV_ROOT}/"
        fi
        rmdir "${IMAGENAV_NESTED_DIR}" 2>/dev/null || true
    fi
    else
    echo "[ImageNav] ${IMAGENAV_VAL_DIR} already exists, skipping extraction."
    fi

    ###############################################################################
    # 3) Text-goal episodes
    ###############################################################################

    if [ ! -f "${TEXTNAV_FILE}" ]; then
    echo "[TextNav] Downloading text-goal episodes from Google Drive..."

    if command -v gdown >/dev/null 2>&1; then
        gdown --id "${TEXTNAV_GDRIVE_ID}" -O "${TEXTNAV_FILE}"
    else
        echo "[TextNav] gdown not found. Installing it with pip..."
        python3 -m pip install --user gdown
        python3 -m gdown --id "${TEXTNAV_GDRIVE_ID}" -O "${TEXTNAV_FILE}"
    fi
    else
    echo "[TextNav] Found local file: ${TEXTNAV_FILE}"
    fi

    ###############################################################################
    # 4) Final structure check
    ###############################################################################
    echo
    echo "===== Expected key files ====="

    echo "[Check] HM3D:"
    if [ -d "${HM3D_VAL_DIR}" ] && [ -n "$(find "${HM3D_VAL_DIR}" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
    echo "  OK: ${HM3D_VAL_DIR}"
    else
    echo "  MISSING OR EMPTY: ${HM3D_VAL_DIR}"
    fi

    echo "[Check] ImageNav:"
    if [ -f "${IMAGENAV_VAL_DIR}/val.json.gz" ]; then
    echo "  OK: ${IMAGENAV_VAL_DIR}/val.json.gz"
    else
    echo "  MISSING: ${IMAGENAV_VAL_DIR}/val.json.gz"
    fi

    echo "[Check] TextNav:"
    if [ -f "${TEXTNAV_FILE}" ]; then
    echo "  OK: ${TEXTNAV_FILE}"
    else
    echo "  MISSING: ${TEXTNAV_FILE}"
    fi

    echo
    echo "Done."
    ```



## 历史经验
这一堆是之前在飞书上写的，现在搬过来同步一下。
- Docker 镜像本质上与 CPU 架构绑定（如 x86_64、ARM64 等）
  - 若构建的镜像需要在其他架构的机器上运行（如在 ARM 宿主机上构建 x86 镜像），可能出现兼容性错误
  - 可通过 `--platform` 参数指定目标架构（需 Docker 支持多架构构建）
- docker有两种导入/创建方式，分别是从本地材料中build或者导入已经build好的image或container：
  - 从本地根据配置文件build：
      - Dockerfile 是一个包含构建指令的文本文件（如安装依赖、复制代码、配置环境等），docker build 会按照这些指令自动执行构建步骤，避免手动配置环境的繁琐和不一致性。
        ```bash
        docker build [选项] <Dockerfile 所在目录>
        ```
        - `-t` 参数为镜像添加标签（如版本号），便于版本管理和追溯（例如 docker build -t myapp:v1.0）
        - `--no-cache`参数为强制忽略所有缓存，从头开始构建，避免缓存对docker build的影响；
  - 导入已储存的镜像文件或容器文件：
      - 导入docker save的镜像文件（这类文件包含完整的镜像元数据，如 json 文件、层数据等）：
        ```bash
        docker load -i <镜像文件路径>
        ```
        - `-i`是 `--input` 的缩写，用于指定要加载的镜像归档文件的路径
  - 导入docker export的容器文件（这类文件是通过 docker export 生成的容器快照，无镜像必需的元数据）：
        ```bash
        docker import <容器文件路径> <镜像名称:标签>
        ```
### 查看本地已有镜像：
```bash
docker images
```
### 运行镜像（创建并启动镜像）
```bash
docker run [选项] 镜像名 [命令]
```
- e.g.  `docker run -it --name my-ubuntu ubuntu:latest /bin/bash`
- 下列所述选项要放到镜像名之前！
- `-it`：`-i`（保持标准输入打开）和 `-t`（分配伪终端），组合使用可进入交互模式。
- `--name my-ubuntu`：给容器命名（可选，不指定则自动生成）。
- `/bin/bash`：容器启动后执行的命令（进入 Bash 终端）。
- `--privileged`: 赋予容器特权模式；默认情况下，Docker 容器运行在隔离的受限环境中，仅拥有有限的 Linux 内核权限。指定这个flag后，会赋予容器几乎与宿主机相同的权限，使其能够访问宿主机的所有设备（如 /dev 目录下的硬件设备），并执行一些需要高权限的操作（如修改内核参数、挂载文件系统等）。
- `-v`：挂载数据卷（Volume），用于将宿主机的文件或目录与容器内的文件或目录建立映射（绑定挂载），实现数据在宿主机和容器之间的共享或持久化，语法为`docker run -v <宿主机路径>:<容器内路径>[:权限选项]`，例如，当宿主机和容器的系统都是Linux时，将宿主机的usb设备挂载到容器上，可以`-v /dev/bus/usb:/dev/bus/usb`。
- 也可以后台运行容器，示例如下：
```bash
docker run -d -p 8080:80 --name my-bg-container my-app:v1
```
- `-d`：后台运行
- `-p 8080:80`：端口映射（主机端口：容器端口）
### 查看容器状态
```bash
docker ps         # 列出正在运行的容器
docker ps -a      # 列出所有容器（包括停止的）
```
### 进入正在运行的容器
```bash
docker exec -it <container_name> /bin/bash
```
- `exec`：在运行的容器中执行命令。
- `-it` 和 `/bin/bash`：同上，进入交互式终端。
### 退出容器
- 临时退出（容器继续运行）：在容器终端中按 `Ctrl + P + Q`。
- 完全退出（终止容器）：在容器终端中输入 `exit` 或按 `Ctrl + D`。
### 启动 / 停止 / 重启容器
```bash
docker start my-ubuntu    # 启动已停止的容器
docker stop my-ubuntu     # 停止运行中的容器
docker restart my-ubuntu  # 重启容器
```
### 删除容器与镜像
- 删除容器
    ```bash
    docker rm my-ubuntu          # 删除已停止的容器
    docker rm -f my-ubuntu       # 强制删除运行中的容器
    ```
- 删除镜像
    ```bash
    docker rmi ubuntu:latest     # 删除指定镜像
    ```
