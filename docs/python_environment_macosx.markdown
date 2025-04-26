Python のインストールと仮想環境作成手順 (MacOSX)
------------------------------------------------

# この文書について

この文書では、 `jageocoder-dbcreator` を実行するために必要な Python 3.x のインストールおよび仮想環境の構築手順を説明します。

対象とする環境は `Mac OS X version 15.2` です。

# Python 3.x のインストール手順

最新の MacOSX に標準インストールされている Python は 3.13 で、 Jageocoder が依存している一部のパッケージがまだ 3.13 に対応していないため、そのままでは利用できません。

[Anaconda](https://www.anaconda.com/docs/getting-started/anaconda/) などを利用してもよいですが、より汎用性の高い [Homebrew](https://brew.sh/ja/) を利用する方法を示します。

まず Homebrew をインストールし、 `pyenv` パッケージをインストールして、 Python 3.12 をインストールします。

```
% /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
% brew install pyenv
% pyenv install 3.12.10
```

これで `~/.pyenv/versions/3.12.10/bin/python3` に 3.12.10 がインストールされます。実行できることを確認します。

```
% ~/.pyenv/versions/3.12.10/bin/python3 --version
Python 3.12.10
```

# 仮想環境 (venv) の作成

Python のソフトをインストールすると、実行に必要なライブラリも一緒にインストールされます。その際に他のソフトが利用しているライブラリを上書きインストールしてしまうと動作しなくなってしまうことがあるため、仮想環境を作成してそこにインストールします。

仮想環境についての詳細は Python 公式サイトの [venv --- 仮想環境の作成](https://docs.python.org/ja/3.10/library/venv.html) を参照してください。

説明のため `~/dbcreator/` に環境を作成するとします。他のディレクトリにインストールしたい場合は適宜読み替えてください。また、プロンプトの表示は環境によって異なるので、違っていても大丈夫です。

以下のコマンドを実行して、 `.venv` 内に必要な処理系を作成します。
```
~ % mkdir ~/dbcreator; cd ~/dbcreator
dbcreator % ~/.pyenv/versions/3.12.10/bin/python3 -m venv .venv
```

# 仮想環境の有効化

次に作成した仮想環境を有効化します (「仮想環境に入る」ということもあります) 。

実行するコマンドは、コマンドラインを動かしているソフトウェア (シェル) によって異なります。
MacOSX では標準で `zsh` が使われています。

```
dbcreator % source .venv/bin/activate
((.venv) ) dbcreator %
```

`tcsh` 等を使っている場合は以下の通りです。
```
dbcreator % source .venv/bin/activate.csh
((.venv) ) dbcreator %
```

仮想環境内にいる場合、プロンプトの先頭に `((.venv) )` のように表示されます。

# (参考) 仮想環境の無効化と削除

仮想環境内での作業が終了し、無効化する (あるいは「仮想環境から出る」) 場合は `deactivate` を実行します。このコマンドはどのプラットフォームでも共通です。

```
deativate
```

不要になった仮想環境は削除して問題ありません。

```
dbcreator % rm -r .venv/
```
