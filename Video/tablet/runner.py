import drv, time
P="\\left(#0\\right)"; FR="\\frac{#0}{{#?}}"; SQ="#0^2"; PW="#0^{#?}"; NF="#0^{{#?}/{#?}}"
def op(o, pause=0.35):
    if o.startswith("!"): drv.cmd(o[1:], pause=pause)
    elif len(o)==1 and o.isalpha(): drv.tap(f'.pbtn[data-base="{o.lower()}"]', pause=pause)
    else: drv.key(o, pause=pause)
def run(name, ops, prefix="f^{\\\\prime}(x)="):
    drv.js(f"document.getElementById('mf').value='{prefix}'"); drv.tap("#mf"); time.sleep(0.4)
    for o in ops: op(o)
    print(name, "=>", drv.value())
