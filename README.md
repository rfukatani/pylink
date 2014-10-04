pylink
======

Link python model and RTL simulation.


当該のプロジェクトのライセンスはGPLV2です。商用問わずフリーで利用できますが、変更・修整があるないに関わらず再頒布する場合はこのプロジェクトのコードを含んでいることを明記し、ソースコードを全て開示する義務があります。また、このコードを利用したことにより受けた損害の責務を著作者は負いません。詳細はLICENSEをご覧ください。


使用するための準備：

一応全部フリーで揃えられるようにしています(Windows以外)。以下は著者が試した環境ですが、他のverilogシミュレータやPythonのバージョンでもコード自体は動作すると思います。makeの手順は変わると思いますが。

OS:
Windows 7

Python:
ver2.7を使用しています。

numpy,scipy:
2014.10.04時点での最新版を使用

verilog simulator:
Modelsim Altera STARTER EDITION 10.1e


構成の説明:

python file:

pylink.py:
信号の発生とアナログ部のモデル化を行い、タイムドリブンでシミュレートしています。データの記録なども行います。
backend.py:
データの読み込み、グラフの表示、クロス相関による遅延算出を行っています。

C file:

call_python_class.c:
PythonAPIによりpythonクラス、関数を呼ぶためのラッパーです。

system verilog file:
top.sv
DPI-Cタスクを呼び出すtopモジュールとAD信号を処理するモジュールsinc_filterを含んでいます。

使い方:
いずれの場合も結果はbackend.pyを実行したり、dataディレクトリのファイルを見たりして確認します。

python単体の場合:
pylink.pyのmainを実行してください。

cから呼び出す:
call_class_python.cを下記のようにコンパイルして実行してください。

>>>gcc .\call_python_class.c -I C:\Python27\include -L C:\Python27\libs -lpython27 -o call_python_class
>>>call_class

verilog simulatorで：
スマートな手順とは思えませんが、、、
よりよい方法があれば教えてください。

modelsimにて、top.svをコンパイルしてください。
そして以下のコマンドをmodelsim上で入力し、dll作成に必要なファイルを吐き出させます。
>>>vlog -novopt -dpiheader dpiheader.h top.sv
>>>vsim top -dpiexportobj cexports.obj -c
windowsのコマンドプロンプトから、以下を実行し、dllを作成してください。
>>>gcc -c -g -I C:\Python27\include -L C:\Python27\libs -lpython27 call_python_class.c -o call_python_class.obj
>>>gcc -shared -I C:\Python27\include -L C:\Python27\libs -o cimports.dll call_python_class.obj cexports.obj C:\altera\14.0\modelsim_ase\win32aloem\mtipli.dll -lpython27

ここまでがdll作成。dllができたら、再びmodelsimに戻り、
>>>vsim -c -sv_lib cimports top -do "add wave -r /*;run -all;quit -sim"
してください。

改変のコツ:
dllの変更をできるだけ減らす(=.cファイルを編集しない)のがコツです。
dllを固めればpythonは再コンパイルする必要なく、改変することが出来ます。
.svだけが変わる場合もdllは再コンパイルする必要がありません。
DPI-C部分が変わる場合はdllを再コンパイル必要が出てきます。

Python,C,systemverilogのどれがおかしいかわからなくなったら、verilog simulatorで全て同時に動かすのではなく、Pythonだけで動かしたり、C-Pythonで動かしたりしてみてもよいと思います。

C-Pythonで動かす場合もPythonだけの改変であればコンパイルは必要ありません。


履歴
2014.10.04:とりあえず動く版として公開しました。色々と不備はありますが、ご指摘いただければ幸いです。