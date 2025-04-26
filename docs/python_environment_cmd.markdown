Python のインストールと仮想環境作成手順 (cmd.exe)
-------------------------------------------------

# この文書について

この文書では、 `jageocoder-dbcreator` を実行するために必要な Python 3.x のインストールおよび仮想環境の構築手順を説明します。

対象とする環境は Windows 11 上のコマンドプロンプト (cmd.exe) です。

# Python 3.x のインストール手順

Microsoft Store を開き、 `Python 3.12` をインストールしてください。 3.13 は Jageocoder が依存している一部のパッケージがまだ 3.13 に対応していないため、利用できません。

インストールが完了したら、コマンドプロンプトを開いて `python3.12` が実行できることを確認してください。

```
C:\> python3.12 --version
Python 3.12.10
```

# 仮想環境 (venv) の作成

Python のソフトをインストールすると、実行に必要なライブラリも一緒にインストールされます。その際に他のソフトが利用しているライブラリを上書きインストールしてしまうと動作しなくなってしまうことがあるため、仮想環境を作成してそこにインストールします。

仮想環境についての詳細は Python 公式サイトの [venv --- 仮想環境の作成](https://docs.python.org/ja/3.10/library/venv.html) を参照してください。

説明のため `C:\Users\foo\dbcreator` に環境を作成するとします。プロンプト (`C:\Users\foo>` など) の foo はユーザ名なので適宜置き換えてください。

以下のコマンドを実行して、 `.venv` 内に必要な処理系を作成します。
```
C:\Users\foo> cd %HOMEPATH% & mkdir dbcreator & cd dbcreator
C:\Users\foo\dbcreator> python3.12 -m venv .venv
```

# 仮想環境の有効化

次に作成した仮想環境を有効化します (「仮想環境に入る」ということもあります) 。

以下のコマンドを実行します。

```
C:\Users\foo\dbcreator> .venv\Scripts\activate.bat
(.venv) C:\Users\foo\dbcreator> 
```

仮想環境内にいる場合、プロンプトの先頭に `(.venv)` のように表示されます。

# (参考) 仮想環境の無効化と削除

仮想環境内での作業が終了し、無効化する (あるいは「仮想環境から出る」) 場合は `deactivate` を実行します。このコマンドはどのプラットフォームでも共通です。

```
deativate
```

不要になった仮想環境は削除して問題ありません。

```
C:\Users\foo\dbcreator> rmdir /S .venv
```
