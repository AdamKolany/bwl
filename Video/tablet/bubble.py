import json, drv
GOAL = r"\frac{\sqrt{x^2+1}}{(2x-3)^3}-\frac{x}{\sqrt{x^2+1}}+e^{-\frac{x}{2}}"
def show(latex=GOAL, label="Ziel:"):
    drv.js("""(()=>{let b=document.getElementById('vidBubble'); if(b) b.remove();
      b=document.createElement('div'); b.id='vidBubble';
      b.style.cssText='position:fixed;top:12px;right:14px;z-index:9999;background:#fffbe6;border:2px solid #d9a400;'+
        'border-radius:18px;padding:10px 16px 12px;box-shadow:0 4px 14px rgba(0,0,0,.25);pointer-events:none;font:16px sans-serif;color:#333';
      b.innerHTML='<div style="font-weight:bold;margin-bottom:4px">'+%s+'</div><math-field read-only style="font-size:26px;border:none;background:transparent;pointer-events:none"></math-field>'+
        '<div style="position:absolute;left:-14px;bottom:18px;width:0;height:0;border-top:10px solid transparent;border-bottom:10px solid transparent;border-right:14px solid #d9a400"></div>';
      document.body.appendChild(b); b.querySelector('math-field').value=%s; return true})()""" % (json.dumps(label), json.dumps(latex)))
def hide(): drv.js("(document.getElementById('vidBubble')||{remove(){}}).remove()")
def task(latex=GOAL, text="Geben Sie die folgende Formel in das Antwortfeld ein:", prefix="f(x)="):
    """Ersetzt (nur im Browser, nur fürs Video) den Aufgabentext durch die Ziel-Formel."""
    return drv.js("""(()=>{const q=document.querySelector('p.q'); if(!q) return 'kein p.q';
      q.innerHTML='<span>'+%s+'</span><span style="display:block;text-align:center;margin:10px 0 4px">'+
        '<math-field read-only style="font-size:30px;border:none;background:transparent;pointer-events:none;display:inline-block"></math-field></span>';
      q.querySelector('math-field').value=%s;
      const mf=document.getElementById('mf'); mf.value=%s; return q.innerText})()""" % (json.dumps(text), json.dumps(prefix + latex), json.dumps(prefix)))
