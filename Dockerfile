FROM python:3

WORKDIR /app
COPY ./app /app

RUN pip3 install --trusted-host pypi.python.org -r ./requirements.txt

#安裝欠缺的字型檔案
COPY ./fonts/msj.ttf /usr/local/lib/python3.8/site-packages/matplotlib/mpl-data/fonts/ttf
RUN   sed -i "s|#font.family  : sans-serif|font.family  : sans-serif |g" /usr/local/lib/python3.8/site-packages/matplotlib/mpl-data/matplotlibrc 
RUN   sed -i "s|#font.serif      : DejaVu Serif,|font.serif      : Microsoft JhengHei, DejaVu Serif, |g" /usr/local/lib/python3.8/site-packages/matplotlib/mpl-data/matplotlibrc 