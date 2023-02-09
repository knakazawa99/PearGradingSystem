# How to use
1. raspi起動
2. raspiにssh接続
　 (win) ssh pi@smartlife.local
3. (raspi) cd AVISController
           python3 main.py
4. (win) exec_script.bat 起動
5. 好きなだけ撮る!
6. 終了するときは右上xボタン
　 raspi側は勝手に終了する

<!--
    "序数 242 がダイナミック ライブラリ 
    C:\Users\yamazaki\Anaconda3\Library\bin\mkl_intel_thread.dll から見つかりませんでした" 
    というエラーが出る場合は，以下のコマンドを実行する． 
    (win) conda install mkl=2018.0.2
-->

<!--
    hogehoge not avilable的なエラーが出た場合は
    カメラにつながったUSBケーブルを抜き差しする
    （カメラの再認識に少し時間がかかります）
-->



python = "^3.10"
PyQt5 = "^5.15.7"
numpy = "^1.23.3"
opencv-python = "^4.6.0.66"
pyspin = "^1.1.1"

poetry env use 3.6.8 ができない、ぱすが通ってないかもしれないため、さいきどう

```
PS C:\Users\yamazaki\Desktop\pear-imaging> pyenv which python
C:\Users\yamazaki\.pyenv\pyenv-win\versions\3.6.8\python.exe
PS C:\Users\yamazaki\Desktop\pear-imaging> poetry env use C:\Users\yamazaki\.pyenv\pyenv-win\versions\3.6.8\python.exe
Creating virtualenv pear-imaging in C:\Users\yamazaki\Desktop\pear-imaging\.venv
Using virtualenv: C:\Users\yamazaki\Desktop\pear-imaging\.venv
PS C:\Users\yamazaki\Desktop\pear-imaging> poetry install C:\Users\yamazaki\.pyenv\pyenv-win\versions\3.6.8\python.exe
```

poetry add numpy==1.19.5 opencv-python==4.4.0.46
numpy>=1.2でpython3.6のサポートが途切れたので、1.19系のさいしんばんを使用
opencv-pythonの4.5.1系以降は、numpy1.21以降が必要のようなので、それ以下の最新を使用
PyQT5>=1.15.*はpython3.7>=が必要なため、それ以下で最新のものを
poetry add .\spinnaker_python-1.15.0.63-cp36-cp36m-win_amd64.whl