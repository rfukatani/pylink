pylink
======

Link python model and RTL simulation.

###本プロジェクトの目的:
scipy,numpyに代表される豊富な科学技術計算向けオープンソースライブラリを持つPythonを、DPI-C経由でRTL検証環境から叩くことにより、Pythonで記述されたアナログ回路や物理モデルとRTLで記述されたデジタル回路を並行してシミュレーションすることが目的です。モデル化によってFast SPICE系シミュレータより高速にシステムレベルシミュレーションを行います。結果はこんな感じ↓

<a target="_blank"
    href="./result.PNG">
    <img style="max-width:100%;" alt="my image"
        src="/mino0123/image/raw/master/my_image.png">
</a>

###使用するための準備：
実行環境は全てフリーで揃えられるようにしています(Windows以外)。以下は著者が試した環境ですが、他のverilogシミュレータやPythonのバージョンでもコード自体は動作すると思います。makeの手順は変わると思いますが。

OS:
Windows 7

Python:
ver2.7を使用しています。

numpy,scipy,matplotlib:
2014.10.04時点での最新版を使用

verilog simulator:
Modelsim Altera STARTER EDITION 10.1e


###構成:

Pythonファイル:
pylink.py:
信号の発生(低周波+高周波sin波)とアナログ部(アナログフィルター+デルタシグマAD)のモデル化を行い、タイムドリブンでシミュレートしています。返り値はデルタシグマの出力値です。シミュレーションと同時にデータの記録も行います。また下記のverilogが含むsincフィルターと同等のフィルターのモデルも含むため、結果をRTLと比較することが出来ます。実はなぜか若干結果が違うので、原因を検討しているところです笑。
backend.py:
データの読み込み、グラフの表示、クロス相関による遅延算出を行っています。

Cファイル:
call_python_class.c:
PythonAPIによりpythonクラス、関数を呼ぶためのラッパーです。

systemverilogファイル:
top.sv
DPI-Cタスクを呼び出すtopモジュールとAD信号を処理するモジュールsinc_filterを含んでいます。

###使い方:
①Python単体、②C-Python、③verilog simulator-C-Pythonの三つの環境で実行できます。
①②の場合、RTLからの結果はゼロとみなされデータに格納されます。
いずれの場合も結果はbackend.pyを実行して確認します。

Python単体の場合:
pylink.pyのmainを実行してください。

c-Pythonで実行:
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


###改変のコツ:
dllの変更をできるだけ減らす(=.cファイルを編集しない)のがコツです。
dllを固めれば再コンパイルする必要なく、Pythonは改変することが出来ます。
.svだけが変わる場合もdllは再コンパイルする必要がありません。
DPI-C部分が変わる場合はdllを再コンパイル必要が出てきます。

Python,C,systemverilogのどこがおかしいかわからなくなったら、verilog simulatorで全て同時に動かすのではなく、Pythonだけで動かしたり、C-Pythonで動かしたりしてみてもよいと思います。

###ライセンス：
このプロジェクトGPLV2でライセンスしています。商用非商用問わずフリーで利用できますが、変更・修整のあるなしに関わらず再頒布する場合はこのプロジェクトのコードを含んでいることを明記し、要請がある場合はソースコードを全て開示する義務があります。また、このコードを利用したことにより受けた損害の責務を著作者は負いません。詳細はLICENSEをご覧ください。

###履歴
2014.10.04:とりあえず動く版として公開しました。不備がありましたら、nannyakannya@gmail.comご指摘いただければ幸いです。

###最後に：
このプロジェクトは2014/10/3 Design solution forumにおいて開催されたsystemverilogハッカソンにおいて開発されたものです。モデレータの@vengineer様、Design solution forum運営の皆様、その他ご支援いただいた皆様にこの場を借りてお礼申し上げます。
