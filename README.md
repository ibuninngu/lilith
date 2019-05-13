# Lilith
本格的なサービスの提供ではなく、ペネトレーションテストやその他特殊な目的のために開発されています。
全てのバージョンのHTTPサーバーでCGIに似た機能をサポートしています。  
※2.0-syndroMEからPythonのバージョンを27から3に変更しています。
    
___ I don't eat cookies because it's high calorie.

## 0.0-SCETCH
・Python27  
Blocking HTTP.

## 1.0-DiCE
・Python27  
Blocking HTTPS.

## 2.0-syndroME
・Python3  
Non-Blocking mode HTTP/2, Non-Blocking HTTP(S), Blocking HTTP(S).

## 3.0-STiCK
・Julia-1.1  
Juliaへの移行を検討するため、ひとまずPythonで使っている方法と同じように実装してみます。  
Windows:Chromeでのページの読み込み速度は6倍(100ms vs 600ms)ほど遅いという結果になりました・・・書き方が悪いだけの可能性が高いです。  
※その後調整を行い、HTTPの比較では同じ速度となりました。