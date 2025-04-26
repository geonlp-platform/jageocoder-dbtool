Python のインストールと仮想環境作成手順 (Linux)
-----------------------------------------------

# この文書について

この文書では、 `jageocoder-dbcreator` を実行するために必要な Python 3.x のインストールおよび仮想環境の構築手順を説明します。

対象とする環境は Ubuntu, CentOS, Debian などの Linux ディストリビューションを利用している場合で、 Windows 上で WSL2 (Windows Subsystem for Linux) の Ubuntu を利用している場合も含みます。

# Python 3.x のインストール手順

ほとんどの Linux では Python 3.x が標準でインストールされています。シェルプロンプトで `python3 --version` を実行すると、インストールされているバージョンが表示されます。

```
$ python3 --version
Python 3.10.12
```

もし Python のバージョンが 3.10 以上かつ 3.12 以下ではない場合、 [Anaconda](https://www.anaconda.com/docs/getting-started/anaconda/) などの利用を検討してください。

# 仮想環境 (venv) の作成

Python のソフトをインストールすると、実行に必要なライブラリも一緒にインストールされます。その際に他のソフトが利用しているライブラリを上書きインストールしてしまうと動作しなくなってしまうことがあるため、仮想環境を作成してそこにインストールします。

仮想環境についての詳細は Python 公式サイトの [venv --- 仮想環境の作成](https://docs.python.org/ja/3.10/library/venv.html) を参照してください。

説明のため `~/dbcreator/` に環境を作成するとします。他のディレクトリにインストールしたい場合は適宜読み替えてください。また、プロンプトの表示は環境によって異なるので、違っていても大丈夫です。

以下のコマンドを実行して、 `.venv` 内に必要な処理系を作成します。
```
~$ mkdir ~/dbcreator; cd ~/dbcreator
~/dbcreator$ python3 -m venv .venv
```

# 仮想環境の有効化

次に作成した仮想環境を有効化します (「仮想環境に入る」ということもあります) 。

実行するコマンドは、コマンドラインを動かしているソフトウェア (シェル) によって異なります。
たとえば Ubuntu で一般的な `bash` では以下のコマンドを実行します。
```
~/dbcreator$ source .venv/bin/activate
(.venv) ~/dbcreator$
```

`tcsh` 等を使っている場合は以下の通りです。
```
~/dbcreator$ source .venv/bin/activate.csh
(.venv) ~/dbcreator$
```

仮想環境内にいる場合、プロンプトの先頭に `(.venv)` のように表示されます。

# (参考) 仮想環境の無効化と削除

仮想環境内での作業が終了し、無効化する (あるいは「仮想環境から出る」) 場合は `deactivate` を実行します。このコマンドはどのプラットフォームでも共通です。

```
deativate
```

不要になった仮想環境は削除して問題ありません。

```
~/dbcreator$ rm -r .venv/
```
