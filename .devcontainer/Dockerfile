ARG ARCH_IMAGE=archlinux:latest
FROM ${ARCH_IMAGE}

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
ARG ATCODER_CLI_VERSION=2.2.0
ARG ONLINE_JUDGE_TOOLS_VERSION=11.5.1
ARG ACLOGIN_VERSION=0.2.1
ARG AC_LIBRARY_VERSION=v1.6
ARG AC_LIBRARY_COMMIT=864245a00b00dd008d1abfdc239618fdb7d139da

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=Asia/Tokyo \
    NO_UPDATE_NOTIFIER=1 \
    PIPX_HOME=/opt/pipx \
    PIPX_BIN_DIR=/usr/local/bin

RUN pacman -Syu --noconfirm --needed \
        bash-completion \
        base-devel \
        ca-certificates \
        clang \
        cmake \
        curl \
        gcc \
        gdb \
        git \
        jq \
        less \
        make \
        nano \
        nodejs \
        npm \
        openssh \
        python \
        python-pipx \
        sudo \
        time \
        tzdata \
        unzip \
    && pacman -Scc --noconfirm

RUN groupadd --gid "${USER_GID}" "${USERNAME}" \
    && useradd --uid "${USER_UID}" --gid "${USER_GID}" --create-home --shell /bin/bash "${USERNAME}" \
    && printf '%s ALL=(root) NOPASSWD:ALL\n' "${USERNAME}" > "/etc/sudoers.d/${USERNAME}" \
    && chmod 0440 "/etc/sudoers.d/${USERNAME}"

RUN npm install --global "atcoder-cli@${ATCODER_CLI_VERSION}" \
    && npm cache clean --force \
    && pipx install "online-judge-tools==${ONLINE_JUDGE_TOOLS_VERSION}" \
    && pipx inject online-judge-tools setuptools \
    && pipx install "aclogin==${ACLOGIN_VERSION}"

RUN git clone --depth 1 --branch "${AC_LIBRARY_VERSION}" \
        https://github.com/atcoder/ac-library.git /tmp/ac-library \
    && test "$(git -C /tmp/ac-library rev-parse HEAD)" = "${AC_LIBRARY_COMMIT}" \
    && install -d /usr/local/include /usr/local/share/ac-library /usr/local/share/licenses/ac-library \
    && cp -a /tmp/ac-library/atcoder /usr/local/include/atcoder \
    && printf '%s\n' "${AC_LIBRARY_VERSION}" > /usr/local/share/ac-library/VERSION \
    && printf '%s\n' "${AC_LIBRARY_COMMIT}" > /usr/local/share/ac-library/COMMIT \
    && install -m 0644 /tmp/ac-library/LICENSE /usr/local/share/licenses/ac-library/LICENSE \
    && rm -rf /tmp/ac-library

COPY .devcontainer/scripts/setup-atcoder-user /usr/local/bin/setup-atcoder-user
COPY .devcontainer/scripts/login-atcoder-if-needed /usr/local/bin/login-atcoder-if-needed
COPY .devcontainer/scripts/atcoder-workflow /usr/local/bin/atcoder-workflow
COPY .devcontainer/scripts/verify-atcoder-toolchain /usr/local/bin/verify-atcoder-toolchain
COPY .devcontainer/scripts/entrypoint /usr/local/bin/atcoder-entrypoint
COPY config/atcoder-cli/config.json /usr/local/share/atcoder-cli/config.json
COPY config/atcoder-cli/cpp/main.cpp config/atcoder-cli/cpp/template.json /usr/local/share/atcoder-cli/cpp/

RUN chmod 0755 \
        /usr/local/bin/setup-atcoder-user \
        /usr/local/bin/login-atcoder-if-needed \
        /usr/local/bin/atcoder-workflow \
        /usr/local/bin/verify-atcoder-toolchain \
        /usr/local/bin/atcoder-entrypoint \
    && install -d -o "${USERNAME}" -g "${USERNAME}" \
        "/home/${USERNAME}/.config/atcoder-cli-nodejs" \
        "/home/${USERNAME}/.local/share/online-judge-tools"

ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin

USER ${USERNAME}
WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/atcoder-entrypoint"]
CMD ["sleep", "infinity"]
