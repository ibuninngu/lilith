# Lilith
本格的なサービスの提供ではなく、とりあえず動くゴミを手っ取り早くでっち上げるために開発されています。とはいえ最近ではWebサーバーの動作はかなり安定しており、いくつかのサービスでAPIサーバーとして利用されています。
全てのバージョンのHTTPサーバーでCGIに似た機能をサポートしています。  
※2.0-syndroMEからPythonのバージョンを27から3に変更しています。  
3.0からは流行りの非同期サーバーになりました  
ドキュメントは・・・ない。  

<img src="https://raw.githubusercontent.com/ibuninngu/Lilith/master/4.0-AmnesiA/Files/Web/l4header.png">
  
## Lilithで動いているサービス
Eve.Familia, Inc.|Eve.Security™|EveEye  
セキュリティのために利用される様々なツールをWeb上から利用できる日本初のサービスです。  
<a href="https://eye.eve.ninja">
<img src="https://www.eve.familia.inc/img/eve_eye.png">
</a>
  
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
