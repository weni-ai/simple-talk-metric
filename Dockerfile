# syntax = docker/dockerfile:1

ARG PYTHON_VERSION="3.13"
ARG DEBIAN_VERSION="bookworm"

ARG BUILD_DEPS="\
  python3-dev \
  libpq-dev \
  build-essential \
  unzip \
"

ARG RUNTIME_DEPS="\
  libpq-dev \
"

ARG PLATFORM_PAIR=linux-amd64

FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION} AS base

# Stage: base# FOLDUP
ARG APP_UID=1999
ARG APP_GID=1999

ARG BUILD_DEPS
ARG RUNTIME_DEPS

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  DEBIAN_FRONTEND=noninteractive \
  PROJECT=appname \
  APP_PATH=/app \
  APP_USER=app_user \
  APP_GROUP=app_group \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PATH="/install/bin:${PATH}" \
  APP_NAME="appname" \
  RUNTIME_DEPS=${RUNTIME_DEPS} \
  BUILD_DEPS=${BUILD_DEPS} \
  PYTHONIOENCODING=UTF-8

RUN addgroup --gid "${APP_GID}" "${APP_GROUP}" \
  && useradd --system -m -d "${APP_PATH}" -u "${APP_UID}" -g "${APP_GID}" "${APP_USER}"

WORKDIR "${APP_PATH}"

RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# UNFOLD

FROM base AS build

# Stage: build# FOLDUP

ARG BUILD_DEPS
ARG PLATFORM_PAIR

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update \
  && apt-get install --no-install-recommends --no-install-suggests -y ${BUILD_DEPS}

# aws lambda get-layer-version-by-arn --arn arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:17 --region us-east-1 --query 'Content.Location' --output text
# aws lambda get-layer-version-by-arn --arn arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension-Arm64:17 --region us-east-1 --query 'Content.Location' --output text
COPY requirements.txt extensions/AWS-Parameters-and-Secrets-Lambda-Extension-17-${PLATFORM_PAIR}.zip /tmp

RUN --mount=type=cache,mode=0755,target=/pip_cache,id=pip \
  pip install --cache-dir /pip_cache --prefix=/install -r /tmp/requirements.txt \
  && unzip /tmp/AWS-Parameters-and-Secrets-Lambda-Extension-17-${PLATFORM_PAIR}.zip -d /opt \
  && rm /tmp/AWS-Parameters-and-Secrets-Lambda-Extension-17-${PLATFORM_PAIR}.zip /tmp/requirements.txt

# UNFOLD

FROM base

# Stage: final# FOLDUP

ARG BUILD_DEPS
ARG RUNTIME_DEPS

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update \
  && SUDO_FORCE_REMOVE=yes apt-get remove --purge -y ${BUILD_DEPS} \
  && apt-get autoremove -y \
  && apt-get install -y --no-install-recommends ${RUNTIME_DEPS} \
  && rm -rf /usr/share/man /usr/share/doc

COPY --from=build /install /usr/local
COPY --from=build /opt /opt
#COPY --chown=${APP_USER}:${APP_GROUP} src/* ${APP_PATH}
COPY src/* ${APP_PATH}

USER "${APP_USER}:${APP_GROUP}"

#EXPOSE 8000

# Set runtime interface client as default command for the container runtime
ENTRYPOINT ["/usr/local/bin/python", "-m", "awslambdaric"]
# Pass the name of the function handler as an argument to the runtime
CMD ["lambda_handler.lambda_handler"]

# UNFOLD

# vim: nu ts=4 fdm=marker fmr=FOLDUP,UNFOLD noet ft=dockerfile:
