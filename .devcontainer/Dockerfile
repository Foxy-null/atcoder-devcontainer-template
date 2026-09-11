FROM ubuntu:24.04@sha256:224a1869083a311ef3f13648a154ba79832fbef6364d31493642ca03082da254

ARG BUILD_JOBS=2
ARG UBUNTU_MIRROR=http://archive.ubuntu.com/ubuntu/
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=Asia/Tokyo \
    NO_UPDATE_NOTIFIER=1 \
    PIPX_HOME=/opt/pipx \
    PIPX_BIN_DIR=/usr/local/bin

RUN sed -i "s|http://archive.ubuntu.com/ubuntu/|${UBUNTU_MIRROR}|g" /etc/apt/sources.list.d/ubuntu.sources \
    && printf 'Acquire::Retries "3";\nAcquire::http::Timeout "30";\n' > /etc/apt/apt.conf.d/80-retries \
    && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bash-completion build-essential ca-certificates clang-format cmake curl \
        gdb git jq less lld m4 nano ninja-build nodejs npm openssh-client \
        patch pbzip2 pigz pipx pkg-config python-is-python3 python3 sudo time \
        tzdata unzip wget xz-utils zlib1g-dev libbz2-dev libzstd-dev \
    && test "$(dpkg --print-architecture)" = amd64

COPY .devcontainer/atcoder/gcc.toml .devcontainer/atcoder/prepare.py .devcontainer/atcoder/install-stage /usr/local/share/atcoder-recipe/
RUN python3 /usr/local/share/atcoder-recipe/prepare.py
# Separate layers retain completed builds if a later dependency fails.
ARG COMPILER_BUILD_JOBS=4
RUN --mount=type=cache,target=/tmp/atcoder/gcc \
    BUILD_JOBS=${COMPILER_BUILD_JOBS} bash /usr/local/share/atcoder-recipe/install-stage compiler
ENV PATH=/opt/atcoder/gcc/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin
RUN printf '%s\n' /opt/atcoder/gcc/lib64 /opt/atcoder/gcc/lib > /etc/ld.so.conf.d/atcoder.conf \
    && ldconfig
RUN bash /usr/local/share/atcoder-recipe/install-stage abseil ac_library boost eigen gmp immer range_v3 unordered_dense
RUN bash /usr/local/share/atcoder-recipe/install-stage libtorch
RUN bash /usr/local/share/atcoder-recipe/install-stage light_gbm
ARG OR_TOOLS_BUILD_JOBS=4
RUN --mount=type=cache,id=atcoder-or-tools,target=/tmp/atcoder/gcc \
    export AC_INSTALL_DIR=/opt/atcoder/gcc \
        AC_TEMP_DIR=/tmp/atcoder/gcc \
        AC_NO_GENERATE_CACHES=true \
        CMAKE_BUILD_PARALLEL_LEVEL=${OR_TOOLS_BUILD_JOBS} \
    && for component in COMPILER abseil ac_library boost eigen gmp immer libtorch light_gbm range_v3 unordered_dense z3; do \
        export "AC_NO_BUILD_${component}=true"; \
    done \
    && BUILD_JOBS=${OR_TOOLS_BUILD_JOBS} bash /tmp/install-atcoder.sh
RUN bash /usr/local/share/atcoder-recipe/install-stage z3 \
    && ldconfig \
    && rm -rf /var/lib/apt/lists/* /tmp/install-atcoder.sh
# OR-Tools builds Boost 1.87 as an internal dependency and installs its headers.
# Restore the public Boost version listed for AtCoder's GCC environment.
RUN python3 /usr/local/share/atcoder-recipe/prepare.py \
    && bash /usr/local/share/atcoder-recipe/install-stage boost \
    && ldconfig \
    && rm -f /tmp/install-atcoder.sh

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
ARG ATCODER_CLI_VERSION=2.2.0
ARG ONLINE_JUDGE_TOOLS_VERSION=11.5.1
ARG ACLOGIN_VERSION=0.2.1

# Ubuntu's base image already reserves UID 1000 for an unused default account.
RUN if id ubuntu >/dev/null 2>&1; then userdel -r ubuntu; fi \
    && groupadd --gid "${USER_GID}" "${USERNAME}" \
    && useradd --uid "${USER_UID}" --gid "${USER_GID}" --create-home --shell /bin/bash "${USERNAME}" \
    && printf '%s ALL=(root) NOPASSWD:ALL\n' "${USERNAME}" > "/etc/sudoers.d/${USERNAME}" \
    && chmod 0440 "/etc/sudoers.d/${USERNAME}"

RUN npm install --global "atcoder-cli@${ATCODER_CLI_VERSION}" \
    && npm cache clean --force \
    && pipx install "online-judge-tools==${ONLINE_JUDGE_TOOLS_VERSION}" \
    && pipx inject online-judge-tools setuptools \
    && pipx install "aclogin==${ACLOGIN_VERSION}"

COPY .devcontainer/scripts/ /usr/local/bin/
COPY .devcontainer/atcoder/check-*.cpp /usr/local/share/atcoder-recipe/
COPY config/atcoder-cli/config.json /usr/local/share/atcoder-cli/config.json
COPY config/atcoder-cli/cpp/main.cpp config/atcoder-cli/cpp/template.json /usr/local/share/atcoder-cli/cpp/
RUN chmod 0755 /usr/local/bin/setup-atcoder-user /usr/local/bin/atcoder-workflow \
        /usr/local/bin/verify-atcoder-toolchain /usr/local/bin/atcoder-g++ /usr/local/bin/entrypoint \
    && install -d -o "${USERNAME}" -g "${USERNAME}" \
        "/home/${USERNAME}/.config/atcoder-cli-nodejs" \
        "/home/${USERNAME}/.local/share/online-judge-tools"

USER ${USERNAME}
WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/entrypoint"]
CMD ["sleep", "infinity"]
