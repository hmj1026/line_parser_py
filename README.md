# Line對話紀錄剖析

取自rz12345的[gist](https://gist.github.com/rz12345/f9719dc8ccfab2bdda4340a690f3386f)套上docker環境。

使用步驟：
1. 將要分析的檔案放到`./data/line_chat`資料夾內分析
2. 先將要分析的對話轉成CSV後再處理後續的分析圖表製作
    * 執行`docker build -t parser .`建立python image
    * 執行`docker run -it --rm -v "%cd%":/tmp parser python line_group_msg_to_csv.py`
    * 執行`docker run -it --rm -v "%cd%":/tmp parser python line_group_msg_stat_plot.py`
    * 執行`docker run -it --rm -v "%cd%":/tmp parser python line_group_msg_sna_plot.py`