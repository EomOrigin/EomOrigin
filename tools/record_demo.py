"""Record frames of the SPOT-DETR web demo: python record_demo.py <demo URL> <frame dir>."""
import asyncio, sys
from playwright.async_api import async_playwright
URL, OUT = sys.argv[1], sys.argv[2]
CLIP = {'x': 120, 'y': 60, 'width': 1440, 'height': 990}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1680, 'height': 1100})
        await pg.goto(URL, wait_until='networkidle', timeout=60000)
        await pg.wait_for_timeout(1500)
        n = 0
        async def shot(tag):
            nonlocal n
            await pg.screenshot(path=f'{OUT}/{n:02d}_{tag}.png', clip=CLIP); n += 1
        await shot('landing')
        exs = await pg.query_selector_all('#examples button.ex')
        titles = [await e.get_attribute('title') for e in exs]
        target = exs[titles.index('Dense parking')]
        await target.hover(); await pg.wait_for_timeout(300); await shot('hover')
        await target.click(); await pg.wait_for_timeout(120); await shot('running')
        await pg.wait_for_selector('#outPanels:not([hidden])', timeout=60000)
        await pg.wait_for_timeout(900); await shot('result')
        for v in ('0.30', '0.70', '0.50'):
            await pg.eval_on_selector('#thr', "(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); }", v)
            await pg.wait_for_timeout(500); await shot(f'thr{v}')
        await b.close()
asyncio.run(main())
