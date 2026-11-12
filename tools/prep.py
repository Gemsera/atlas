import json, math, sys, shutil, re
def clean(L): return [re.sub(r'\[([^\]|]+)\]', r'\1', re.sub(r'\[[^\]|]+\|([^\]]+)\]', r'\1', x)) for x in L]
SRC = sys.argv[1]; OUT = sys.argv[2]
A16 = [0,30,45,60,90,120,135,150,180,210,225,240,270,300,315,330]
A40 = [0,10,20,30,40,45,50,60,70,80,90,100,110,120,130,135,140,150,160,170,180,190,200,210,220,225,230,240,250,260,270,280,290,300,310,315,320,330,340,350]
def angle(orbit, idx, spo):
    n = spo[orbit]
    if n == 16: return math.radians(A16[idx])
    if n == 40: return math.radians(A40[idx])
    return 2*math.pi*idx/n
spritesOut = None
for key, fn in [('standard','data.json'),('ruthless','ruthless.json')]:
    d = json.load(open(f'{SRC}/{fn}'))
    C = d['constants']; R = C['orbitRadii']; spo = C['skillsPerOrbit']
    G = d['groups']; N = d['nodes']
    pos = {}
    for k, n in N.items():
        if k == 'root': continue
        g = G[str(n['group'])]
        a = angle(n['orbit'], n['orbitIndex'], spo)
        r = R[n['orbit']]
        pos[k] = (g['x'] + r*math.sin(a), g['y'] - r*math.cos(a))
    S = d['sprites']
    def coords(cat): return S[cat]['0.5']['coords']
    nodes = []
    for k, n in N.items():
        if k == 'root': continue
        t = 'mastery' if n.get('isMastery') else 'wormhole' if n.get('isWormhole') else 'keystone' if n.get('isKeystone') else 'notable' if n.get('isNotable') else 'start' if k=='29045' or (not n.get('name')) else 'normal'
        o = {'id': int(k), 'n': n.get('name',''), 't': t, 'x': round(pos[k][0],1), 'y': round(pos[k][1],1), 'g': n['group'], 'i': n.get('icon','')}
        if n.get('stats'): o['s'] = clean(n['stats'])
        if n.get('reminderText'): o['r'] = clean(n['reminderText'])
        if n.get('flavourText'): o['f'] = n['flavourText']
        if n.get('variantEffects'): o['v'] = [{'e': v['effect'], 's': clean(v['stats'])} for v in n['variantEffects']]
        nodes.append(o)
    edges = []; seen=set()
    conn = {}
    for k, n in N.items():
        for c in n.get('connections', []): conn[(k, c['to'])] = c; conn[(c['to'], k)] = c
    for k, n in N.items():
        if k == 'root': continue
        for o in n['out']:
            if o == 'root': continue
            p = tuple(sorted((k,o)))
            if p in seen: continue
            seen.add(p)
            a, b = N[k], N[o]
            e = {'a': int(k), 'b': int(o)}
            if a.get('isWormhole') and b.get('isWormhole') and a['group'] != b['group']:
                e['w'] = 1
            elif a.get('isMastery') or b.get('isMastery'):
                continue
            else:
                c = conn.get((k,o))
                if c and 'orbitX' in c and c['orbit'] > 0:
                    e['c'] = [round(c['orbitX'],1), round(c['orbitY'],1)]
                elif a['group'] == b['group'] and a['orbit'] == b['orbit'] and a['orbit'] > 0:
                    g = G[str(a['group'])]; e['c'] = [g['x'], g['y']]
            edges.append(e)
    groups = {}
    for gk, g in G.items():
        bg = g.get('background')
        if bg: groups[gk] = {'x': g['x'], 'y': g['y'], 'b': bg['image'], 'ox': bg.get('offsetX',0), 'oy': bg.get('offsetY',0), 'h': bg.get('isHalfImage',False)}
    out = {'version': d['tree'], 'points': d['points']['totalPoints'], 'bounds': [d['min_x'], d['min_y'], d['max_x'], d['max_y']], 'nodes': nodes, 'edges': edges, 'groups': groups}
    json.dump(out, open(f'{OUT}/tree-{key}.json','w'), separators=(',',':'))
    if spritesOut is None:
        spritesOut = {}
        files = set()
        for cat in ['normalActive','notableActive','keystoneActive','wormholeActive','normalInactive','notableInactive','keystoneInactive','wormholeInactive','mastery','groupBackground','startNode','frame']:
            s = S[cat]['0.5']; f = s['filename'].split('/')[-1].split('?')[0]; files.add(f)
            spritesOut[cat] = {'file': 'assets/'+f, 'c': {kk: [v['x'],v['y'],v['w'],v['h']] for kk,v in s['coords'].items()}}
        s = S['masteryOverlay']['1']; f = s['filename'].split('/')[-1].split('?')[0]; files.add(f)
        spritesOut['masteryOverlay'] = {'file':'assets/'+f, 'scale':1, 'c': {kk: [v['x'],v['y'],v['w'],v['h']] for kk,v in s['coords'].items()}}
        s = S['atlasBackground']['0.5']; f = s['filename'].split('/')[-1].split('?')[0]; files.add(f)
        spritesOut['atlasBackground'] = {'file':'assets/'+f, 'c': {kk: [v['x'],v['y'],v['w'],v['h']] for kk,v in s['coords'].items()}}
        s = S['background']['0.5']; f = s['filename'].split('/')[-1].split('?')[0]; files.add(f)
        spritesOut['background'] = {'file':'assets/'+f}
        for f in files: shutil.copy(f'{SRC}/assets/{f}', f'{OUT}/assets/{f}')
        json.dump(spritesOut, open(f'{OUT}/sprites.json','w'), separators=(',',':'))
    # sanity: all icons present
    miss = [n['i'] for n in nodes if n['t'] in ('normal','notable','keystone') and n['i'] not in spritesOut[n['t']+'Active']['c']]
    print(key, len(nodes), len(edges), 'missing', miss[:5])
