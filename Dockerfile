FROM python:3

WORKDIR /app
COPY ./app /app
COPY ./fonts /app/fonts

RUN pip3 install --trusted-host pypi.python.org -r ./requirements.txt

#安裝欠缺的字型檔案 - 先取得 Python 版本
RUN python3 -c "import sys; print(f'/usr/local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages')" > /tmp/python_site_packages_path

#複製字型並配置 matplotlib
RUN PYTHON_SITE_PACKAGES=$(cat /tmp/python_site_packages_path) && \
    cp /app/fonts/msj.ttf "${PYTHON_SITE_PACKAGES}/matplotlib/mpl-data/fonts/ttf/" && \
    sed -i "s|#font.family  : sans-serif|font.family  : sans-serif |g" "${PYTHON_SITE_PACKAGES}/matplotlib/mpl-data/matplotlibrc" && \
    sed -i "s|#font.serif      : DejaVu Serif,|font.serif      : Microsoft JhengHei, DejaVu Serif, |g" "${PYTHON_SITE_PACKAGES}/matplotlib/mpl-data/matplotlibrc" 