import json,sys,websocket,urllib.request
tid=sys.argv[1]; expr=sys.stdin.read()
ws=websocket.create_connection(f"ws://localhost:9222/devtools/page/{tid}",suppress_origin=True)
ws.send(json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":expr,"returnByValue":True,"awaitPromise":True}}))
while True:
    r=json.loads(ws.recv())
    if r.get("id")==1: print(json.dumps(r.get("result",{}).get("result",{}).get("value", r),ensure_ascii=False,indent=1)); break
