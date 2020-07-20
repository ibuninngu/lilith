# Lilith
本格的なサービスの提供ではなく、とりあえず動くゴミを手っ取り早くでっち上げるために開発されています。とはいえ最近ではWebサーバーの動作はかなり安定しており、いくつかのサービスでAPIサーバーとして利用されています。
全てのバージョンのHTTPサーバーでCGIに似た機能をサポートしています。  
※2.0-syndroMEからPythonのバージョンを27から3に変更しています。  
ドキュメントは・・・ない。  
    
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
・Python37  
asyncioに切り替えました。  
HTTP(S), HTTP/2, POP3, SMTP(PLAIN-AUTH)
### 3.1-STiCK-CookieMoguMogu
Cookieを食べてみたバージョン。次に引き継ぐかは未定。

## 4.0-AmnesiA
・Python38  
HTTP(S), ...  
今回はCookieを食べられます。VirtualHost利用可能  
WebSocket実装！
