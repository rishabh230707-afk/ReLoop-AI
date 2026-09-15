#!/usr/bin/env python3
"""ReLoop AI: offline, single-user reuse matching prototype. Python 3.10+."""
import argparse
import collections
import json
import math
import os
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parent
GLOSSARY = {
    'display': 'monitor', 'displays': 'monitor', 'screen': 'monitor', 'screens': 'monitor', 'monitors': 'monitor',
    'seating': 'chair', 'chairs': 'chair', 'seat': 'chair', 'seats': 'chair',
    'tables': 'desk', 'table': 'desk', 'desks': 'desk', 'workstation': 'desk',
    'shelving': 'shelf', 'shelves': 'shelf', 'rack': 'shelf',
    'whiteboards': 'whiteboard', 'board': 'whiteboard',
    'projectors': 'projector', 'projection': 'projector',
    'notebooks': 'notebook', 'registers': 'notebook', 'register': 'notebook',
    'stands': 'stand', 'retort': 'stand', 'clamps': 'clamp',
}
STOP = set('a an the i we need want looking for some to of and with in our my please spare unused working good condition required units pieces buy procure'.split())
CATEGORIES = {'monitor':'Electronics','projector':'Electronics','chair':'Furniture','desk':'Furniture','shelf':'Furniture','whiteboard':'Teaching','notebook':'Stationery','stand':'Lab equipment','clamp':'Lab equipment'}

def tokens(text):
    return [GLOSSARY.get(t,t) for t in re.findall(r'[a-z0-9]+', text.lower()) if t not in STOP]

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def initial_state():
    return {'inventory':read_json(ROOT/'inventory.json'), 'transfers':[]}

def load_state(path):
    return read_json(path) if Path(path).exists() else initial_state()

def save_state(path, state):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',dir=path.parent,delete=False,encoding='utf-8') as f:
        json.dump(state,f,indent=2); temporary=f.name
    os.replace(temporary,path)

def vector(terms, idf):
    counts=collections.Counter(terms)
    v={t:(1+math.log(n))*idf[t] for t,n in counts.items() if t in idf}
    norm=math.sqrt(sum(x*x for x in v.values()))
    return {t:x/norm for t,x in v.items()} if norm else {}

def partner(partner_id):
    record=next((x for x in read_json(ROOT/'partners.json') if x['id']==partner_id),None)
    if not record or not record['approved']:
        raise ValueError('Choose an approved demo partner: CAMPUS01 or SCHOOL01.')
    return record

def eligible(item, recipient):
    return recipient['id']=='CAMPUS01' or item.get('school_shareable',False)

def match(state, query, quantity=1, max_distance=10, accept_repair=False, recipient_id='CAMPUS01'):
    recipient=partner(recipient_id)
    if not isinstance(quantity,int) or quantity<1: raise ValueError('Quantity must be a positive integer.')
    if not math.isfinite(max_distance) or max_distance<0: raise ValueError('Distance must be finite and non-negative.')
    if len(query)>500: raise ValueError('Use a description of at most 500 characters.')
    qt=tokens(query)
    heads=set(qt)&set(CATEGORIES)
    if not heads: return {'status':'clarify','message':'Name one supported item: monitor, chair, desk, shelf, whiteboard, projector, notebook, stand or clamp.','matches':[]}
    if len(heads)>1: return {'status':'clarify','message':'Search for one item type at a time.','matches':[]}
    if re.search(r'\b(no|not|without|except|instead)\b',query.lower()):
        return {'status':'clarify','message':'Describe only the item you need, without exclusions or negation.','matches':[]}
    if re.search(r'\b(chemicals?|acids?|batter(?:y|ies)|medicines?|medical|food|hazardous)\b',query.lower()):
        return {'status':'clarify','message':'This prototype excludes food, chemicals, batteries and medical items.','matches':[]}
    head=next(iter(heads)); docs=[tokens(x['title']+' '+x['description']+' '+x['category']) for x in state['inventory']]
    df=collections.Counter(t for doc in docs for t in set(doc))
    idf={t:math.log((1+len(docs))/(1+n))+1 for t,n in df.items()}
    qv=vector(qt,idf); matches=[]
    for original,doc in zip(state['inventory'],docs):
        if not eligible(original,recipient): continue
        item={**original,'distance_km':original.get('recipient_distances',{}).get(recipient_id,original['distance_km'])}
        if head not in doc or item['quantity']<=0 or item['distance_km']>max_distance: continue
        if item['condition']=='repairable' and not accept_repair: continue
        dv=vector(doc,idf); similarity=sum(v*dv.get(t,0) for t,v in qv.items())
        if similarity<0.12: continue
        offered=min(quantity,item['quantity'])
        shared=sorted(set(qt)&set(doc))
        matches.append({**item,'offered_quantity':offered,'remaining_need':quantity-offered,
                        'similarity':round(similarity,4),'matched_terms':shared,
                        'explanation':'Shared terms: '+', '.join(shared)+'. Verify all specifications with the owner before transfer.'})
    matches.sort(key=lambda x:(-x['similarity'],x['distance_km'],x['id']))
    return {'status':'matched' if matches else 'no_match','message':'Candidate matches; similarity is not a probability or a suitability guarantee.' if matches else 'No suitable stock in the selected distance and condition limits. Broaden the distance or ask the coordinator.','matches':matches}

def confirm(state, item_id, quantity, purchase_price, transport, refurbishment, inspected=False, recipient_id='CAMPUS01'):
    recipient=partner(recipient_id)
    if not inspected: raise ValueError('Confirm physical inspection before recording a transfer.')
    if not isinstance(quantity,int) or quantity<1: raise ValueError('Quantity must be a positive integer.')
    for n in (purchase_price, transport, refurbishment):
        if not math.isfinite(n) or n<0: raise ValueError('Costs must be finite and non-negative.')
    item=next((x for x in state['inventory'] if x['id']==item_id),None)
    if item is None: raise ValueError('Unknown item ID.')
    if not eligible(item,recipient): raise ValueError('This listing is reserved for internal campus reuse.')
    if item['quantity']<quantity: raise ValueError('Insufficient stock. Refresh your search.')
    if item['condition']=='repairable' and refurbishment<=0: raise ValueError('Enter a refurbishment cost for a repairable item.')
    transfer={'id':f"T{len(state['transfers'])+1:03d}",'item_id':item_id,'title':item['title'],'quantity':quantity,'recipient_id':recipient['id'],'recipient_name':recipient['name'],'recipient_type':recipient['type'],
              'purchase_price_per_unit':purchase_price,'transport_total':transport,'refurbishment_per_unit':refurbishment,
              'estimated_net_savings':round(quantity*(purchase_price-refurbishment)-transport,2),
              'estimated_mass_reused_kg':round(quantity*item['mass_kg'],2),
              'note':'Demo transfer. Savings depend on a replacement purchase actually being avoided. Mass is reused mass, not proven landfill diversion or CO2 savings.'}
    item['quantity']-=quantity; state['transfers'].append(transfer)
    return transfer

def summary(state):
    return {'confirmed_demo_transfers':len(state['transfers']),
            'school_units_supplied':sum(t['quantity'] for t in state['transfers'] if t.get('recipient_type')=='school'),
            'recipient_partners_served':len({t.get('recipient_id','CAMPUS01') for t in state['transfers']}),
            'units_reused':sum(t['quantity'] for t in state['transfers']),
            'estimated_net_savings_inr':round(sum(t['estimated_net_savings'] for t in state['transfers']),2),
            'estimated_mass_reused_kg':round(sum(t['estimated_mass_reused_kg'] for t in state['transfers']),2),
            'disclosure':'Synthetic inventory and demo transactions. No measured campus impact.'}

def gui(state_path):
    """Desktop workspace with human-readable search, transfer and impact views."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        root = tk.Tk()
    except Exception as error:
        raise ValueError('Desktop UI unavailable. Use the match and demo commands, or install Python with Tk support.') from error

    BG, WHITE, INK, MUTED = '#F2F5F8', '#FFFFFF', '#182C36', '#536674'
    GREEN, DARK, LINE, PALE = '#16704A', '#112F28', '#DCE5E9', '#EAF5EE'
    FONT = 'Helvetica Neue' if root.tk.call('tk', 'windowingsystem') == 'aqua' else 'Arial'
    root.title('ReLoop AI — Campus-to-School Resource Reuse')
    root.geometry('1220x820'); root.minsize(980, 660); root.configure(bg=BG)
    style = ttk.Style(root); style.theme_use('clam')
    style.configure('TEntry', padding=10, font=(FONT, 13), fieldbackground=WHITE, bordercolor=LINE)
    style.configure('TCombobox', padding=9, font=(FONT, 13), fieldbackground=WHITE)
    style.configure('Primary.TButton', font=(FONT, 13, 'bold'), padding=(18, 11), background=GREEN, foreground=WHITE, borderwidth=0)
    style.map('Primary.TButton', background=[('active', '#105936'), ('disabled', '#899C93')])
    style.configure('Soft.TButton', font=(FONT, 12, 'bold'), padding=(13, 9), background=PALE, foreground=GREEN, borderwidth=0)
    style.map('Soft.TButton', background=[('active', '#D8ECDC')])
    style.configure('TCheckbutton', background=WHITE, foreground=INK, font=(FONT, 12))

    def label(parent, value, size=13, color=INK, bold=False, bg=None, **kw):
        return tk.Label(parent, text=value, font=(FONT, size, 'bold' if bold else 'normal'),
                        fg=color, bg=bg or parent.cget('bg'), anchor='w', justify='left', **kw)

    def card(parent, **kw):
        return tk.Frame(parent, bg=WHITE, highlightbackground=LINE, highlightthickness=1, **kw)

    sidebar = tk.Frame(root, bg=DARK, width=230); sidebar.pack(side='left', fill='y'); sidebar.pack_propagate(False)
    label(sidebar, 'ReLoop AI', 27, '#C6F58C', True).pack(anchor='w', padx=23, pady=(32, 5))
    label(sidebar, 'RESOURCE REUSE NETWORK', 10, '#B7CCC3').pack(anchor='w', padx=24)
    label(sidebar, 'Campus resources.\nA longer useful life.', 14, WHITE).pack(anchor='w', padx=24, pady=(26, 32))
    nav = tk.Frame(sidebar, bg=DARK); nav.pack(fill='x', padx=14)
    foot = tk.Frame(sidebar, bg=DARK); foot.pack(side='bottom', fill='x', padx=24, pady=26)
    label(foot, 'SDG 04   /   12   /   17', 12, '#C6F58C', True).pack(anchor='w')
    label(foot, 'Education · Reuse\nInstitutional partnerships', 11, '#B7CCC3').pack(anchor='w', pady=(8, 18))
    label(foot, 'Offline demonstration\nAll sample records are fictional.', 10, '#B7CCC3').pack(anchor='w')

    main = tk.Frame(root, bg=BG); main.pack(side='left', fill='both', expand=True)
    canvas = tk.Canvas(main, bg=BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y'); canvas.pack(side='left', fill='both', expand=True)
    canvas.configure(yscrollcommand=scrollbar.set)
    content = tk.Frame(canvas, bg=BG)
    window = canvas.create_window((0, 0), window=content, anchor='nw')
    content.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.bind('<Configure>', lambda e: canvas.itemconfigure(window, width=e.width))
    def wheel(event):
        # Leave dropdowns and modal forms to their native scrolling behavior.
        if event.widget.winfo_toplevel() != root or isinstance(event.widget, ttk.Combobox): return
        delta = -event.delta if root.tk.call('tk', 'windowingsystem') == 'aqua' else -int(event.delta / 120)
        canvas.yview_scroll(delta, 'units')
    root.bind('<MouseWheel>', wheel)
    root.bind('<Button-4>', lambda e: canvas.yview_scroll(-2, 'units'))
    root.bind('<Button-5>', lambda e: canvas.yview_scroll(2, 'units'))

    query = tk.StringVar(value='display for computer lab'); quantity = tk.StringVar(value='2')
    radius = tk.StringVar(value='10'); repair = tk.BooleanVar(value=False)
    approved = {f"{p['name']} ({p['type'].title()})": p['id'] for p in read_json(ROOT/'partners.json') if p['approved']}
    recipient = tk.StringVar(value=next((name for name, pid in approved.items() if pid == 'SCHOOL01'), next(iter(approved))))
    nav_buttons = {}; current_view = {'name': 'Find resources'}

    def clear(title, subtitle):
        current_view['name'] = title
        for child in content.winfo_children(): child.destroy()
        for name, button in nav_buttons.items():
            button.configure(bg='#254C3F' if name == title else DARK)
        canvas.yview_moveto(0)
        header = tk.Frame(content, bg=BG); header.pack(fill='x', padx=28, pady=(26, 22))
        label(header, title, 27, INK, True).pack(anchor='w')
        label(header, subtitle, 12, MUTED, wraplength=650).pack(anchor='w', pady=(6, 0))

    def note(parent, title, detail):
        box = card(parent); box.pack(fill='x', padx=28, pady=(0, 14))
        label(box, title, 15, INK, True).pack(anchor='w', padx=20, pady=(16, 5))
        label(box, detail, 12, MUTED, wraplength=620).pack(anchor='w', padx=20, pady=(0, 18))

    def transfer_form(item, recipient_id):
        # Freeze the selected recipient while the dialog is open.
        target = partner(recipient_id)
        win = tk.Toplevel(root); win.title('Record a reuse transfer'); win.configure(bg=WHITE)
        win.geometry('560x650'); win.minsize(520, 620); win.transient(root); win.grab_set()
        label(win, 'Give this resource a next home', 21, INK, True).pack(anchor='w', padx=26, pady=(24, 8))
        label(win, item['title'], 16, GREEN, True).pack(anchor='w', padx=26)
        label(win, f"To {target['name']}\n{item['quantity']} units currently available", 12, MUTED).pack(anchor='w', padx=26, pady=(6, 18))
        fields = tk.Frame(win, bg=WHITE); fields.pack(fill='x', padx=26)
        fields.columnconfigure(1, weight=1)
        values = {}
        defaults = [('quantity', 'Units to transfer', str(item['offered_quantity'])),
                    ('price', 'New purchase benchmark / unit (INR)', '0'),
                    ('transport', 'Total transport cost (INR)', '0'),
                    ('refurb', 'Refurbishment / unit (INR)', '0')]
        for row, (key, title, value) in enumerate(defaults):
            label(fields, title, 11).grid(row=row, column=0, sticky='w', padx=(0, 12), pady=8)
            values[key] = tk.StringVar(value=value)
            ttk.Entry(fields, textvariable=values[key], width=10).grid(row=row, column=1, sticky='ew', pady=8)
        label(win, 'Enter your demo assumptions. A zero benchmark makes no\navoided-purchase claim; costs can produce negative savings.', 11, MUTED).pack(anchor='w', padx=26, pady=14)
        inspected = tk.BooleanVar(value=False)
        ttk.Checkbutton(win, text='I inspected and approved these demo items', variable=inspected).pack(anchor='w', padx=26)
        error = label(win, '', 11, '#AB3030', wraplength=490); error.pack(fill='x', padx=26, pady=10)
        def finish():
            try:
                state = load_state(state_path)
                result = confirm(state, item['id'], int(values['quantity'].get()), float(values['price'].get()),
                                 float(values['transport'].get()), float(values['refurb'].get()), inspected.get(), recipient_id)
                save_state(state_path, state)
            except (ValueError, OSError) as exc:
                error.configure(text=str(exc)); return
            win.destroy(); impact_view(f"Transfer {result['id']} recorded: {result['quantity']} units supplied to {target['name']}.")
        actions = tk.Frame(win, bg=WHITE); actions.pack(side='bottom', fill='x', padx=26, pady=24)
        ttk.Button(actions, text='Cancel', style='Soft.TButton', command=win.destroy).pack(side='left')
        ttk.Button(actions, text='Confirm demo transfer', style='Primary.TButton', command=finish).pack(side='right')

    def search_view():
        clear('Find resources', 'Match surplus campus stock with the needs of your department or partner school.')
        form = card(content); form.pack(fill='x', padx=28, pady=(0, 18))
        for col in range(3): form.columnconfigure(col, weight=1)
        label(form, 'What do you need?', 12, INK, True).grid(row=0, column=0, columnspan=3, sticky='w', padx=18, pady=(18, 6))
        entry = ttk.Entry(form, textvariable=query, font=(FONT, 14))
        entry.grid(row=1, column=0, columnspan=3, sticky='ew', padx=18, pady=(0, 14))
        for col, title in enumerate(['Recipient institution', 'Quantity', 'Collection radius (km)']):
            label(form, title, 11, MUTED).grid(row=2, column=col, sticky='w', padx=18, pady=(0, 5))
        ttk.Combobox(form, textvariable=recipient, values=list(approved), state='readonly', width=26).grid(row=3, column=0, sticky='ew', padx=(18, 8))
        ttk.Entry(form, textvariable=quantity, width=6).grid(row=3, column=1, sticky='ew', padx=8)
        ttk.Entry(form, textvariable=radius, width=6).grid(row=3, column=2, sticky='ew', padx=(8, 18))
        ttk.Checkbutton(form, text='Include items needing repair', variable=repair).grid(row=4, column=0, columnspan=2, sticky='w', padx=18, pady=18)
        results = tk.Frame(content, bg=BG); results.pack(fill='x', padx=28, pady=(0, 24))
        def search():
            for child in results.winfo_children(): child.destroy()
            try:
                recipient_id = approved[recipient.get()]
                result = match(load_state(state_path), query.get(), int(quantity.get()), float(radius.get()), repair.get(), recipient_id)
            except (ValueError, OSError) as exc:
                label(results, str(exc), 13, '#AB3030', wraplength=620).pack(anchor='w'); return
            matches = result['matches']
            label(results, f"{len(matches)} matching resources" if matches else 'Let’s refine your search', 17, INK, True).pack(anchor='w', pady=(0, 6))
            label(results, 'Ranked by text relevance. Inspect specifications before approving a transfer.' if matches else result['message'], 11, MUTED, wraplength=650).pack(anchor='w', pady=(0, 15))
            for index, item in enumerate(matches):
                box = card(results); box.pack(fill='x', pady=(0, 12))
                top = tk.Frame(box, bg=WHITE); top.pack(fill='x', padx=18, pady=(16, 4))
                label(top, item['category'].upper(), 10, GREEN, True).pack(side='left')
                label(top, 'TOP TEXT MATCH' if index == 0 else f"MATCH {index+1:02d}", 10, MUTED).pack(side='right')
                label(box, item['title'], 19, INK, True, wraplength=620).pack(anchor='w', padx=18, pady=(4, 3))
                label(box, item['department'], 12, MUTED).pack(anchor='w', padx=18)
                label(box, f"{item['quantity']} available   ·   {item['distance_km']:g} km away   ·   {item['condition'].capitalize()}", 12, INK).pack(anchor='w', padx=18, pady=(12, 5))
                label(box, 'Matched words: '+', '.join(item['matched_terms'])+f"   /   Text similarity {item['similarity']:.2f}", 11, MUTED, wraplength=620).pack(anchor='w', padx=18)
                bottom = tk.Frame(box, bg=WHITE); bottom.pack(fill='x', padx=18, pady=(12, 16))
                supply = f"Can supply {item['offered_quantity']} of {quantity.get()} requested"
                if item['remaining_need']: supply += f" · {item['remaining_need']} still needed"
                label(bottom, supply, 11, GREEN, True, wraplength=390).pack(side='left')
                ttk.Button(bottom, text='Review transfer', style='Soft.TButton', command=lambda m=item, pid=recipient_id: transfer_form(m, pid)).pack(side='right')
        ttk.Button(form, text='Find matches', style='Primary.TButton', command=search).grid(row=4, column=2, sticky='e', padx=18, pady=18)
        entry.bind('<Return>', lambda e: search()); search()

    def impact_view(success=None):
        clear('Reuse impact', 'Recorded demo transfers across the campus-to-school network.')
        state = load_state(state_path); totals = summary(state)
        if success: note(content, 'Transfer recorded', success)
        metrics = tk.Frame(content, bg=BG); metrics.pack(fill='x', padx=28, pady=(0, 18))
        for col in range(3): metrics.columnconfigure(col, weight=1, uniform='metrics')
        stats = [('Units kept in use', str(totals['units_reused']), 'Recorded transfer quantities'),
                 ('Resources for schools', str(totals['school_units_supplied']), 'Units supplied to school partners'),
                 ('Estimated reused mass', f"{totals['estimated_mass_reused_kg']:g} kg", 'Based on sample item weights'),
                 ('Estimated net savings', f"INR {totals['estimated_net_savings_inr']:,.0f}", 'Entered benchmark less transfer costs'),
                 ('Completed transfers', str(totals['confirmed_demo_transfers']), 'Local demo records'),
                 ('Partners served', str(totals['recipient_partners_served']), 'Distinct recipient institutions')]
        for index, (title, value, explanation) in enumerate(stats):
            box = card(metrics); box.grid(row=index//3, column=index%3, sticky='nsew', padx=(0, 10), pady=(0, 10))
            label(box, title, 11, MUTED, wraplength=190).pack(anchor='w', padx=16, pady=(16, 8))
            label(box, value, 23, GREEN, True, wraplength=195).pack(anchor='w', padx=16)
            label(box, explanation, 10, MUTED, wraplength=180).pack(anchor='w', padx=16, pady=(8, 16))
        note(content, 'What these figures mean', 'Synthetic demonstration only. Reused mass is not verified landfill diversion. Savings depend on a purchase actually being avoided. No carbon reductions or learning outcomes are measured.')
        if not state['transfers']:
            note(content, 'Your reuse story starts with one transfer', 'Find a suitable resource, inspect it, then record a demo transfer. Your summary will update here.')
            ttk.Button(content, text='Find resources', style='Primary.TButton', command=search_view).pack(anchor='w', padx=28, pady=(0, 24))
        else:
            label(content, 'Recent transfers', 17, INK, True).pack(anchor='w', padx=28, pady=(6, 14))
            for record in reversed(state['transfers'][-10:]):
                note(content, f"{record['id']}  ·  {record['title']}", f"{record['quantity']} units to {record.get('recipient_name','Demo Campus')}\nEstimated reused mass: {record['estimated_mass_reused_kg']:g} kg   /   Net savings: INR {record['estimated_net_savings']:,.0f}")

    def partners_view():
        clear('Partner network', 'The demo connects campus resources with institutions that can use them.')
        for record in read_json(ROOT/'partners.json'):
            note(content, record['name'], f"{record['type'].title()}   /   {'Approved demo partner' if record['approved'] else 'Awaiting review — transfers unavailable'}\nReference: {record['id']}")
        note(content, 'Partnerships with a purpose', 'SDG 4: access to learning equipment. SDG 12: keep usable resources in service. SDG 17: coordinated institutional sharing. Real agreements and outcomes still need validation.')

    for title, command in [('Find resources', search_view), ('Reuse impact', impact_view), ('Partner network', partners_view)]:
        button = tk.Label(nav, text=title, font=(FONT, 13, 'bold'), fg=WHITE, bg=DARK, anchor='w', padx=14, pady=13, cursor='hand2', takefocus=True)
        button.pack(fill='x', pady=3); button.bind('<Button-1>', lambda e, c=command: c()); button.bind('<Return>', lambda e, c=command: c()); button.bind('<space>', lambda e, c=command: c())
        nav_buttons[title] = button
    search_view(); root.mainloop()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',default=str(ROOT/'local_state.json'),help='Local single-user state file')
    sub=parser.add_subparsers(dest='command',required=True)
    search=sub.add_parser('match');search.add_argument('query');search.add_argument('--quantity',type=int,default=1);search.add_argument('--max-distance',type=float,default=10);search.add_argument('--accept-repair',action='store_true');search.add_argument('--recipient',default='CAMPUS01')
    transfer=sub.add_parser('confirm');transfer.add_argument('item_id');transfer.add_argument('--quantity',type=int,required=True);transfer.add_argument('--purchase-price',type=float,required=True);transfer.add_argument('--transport',type=float,default=0);transfer.add_argument('--refurbishment',type=float,default=0);transfer.add_argument('--inspected',action='store_true');transfer.add_argument('--recipient',default='CAMPUS01')
    sub.add_parser('partners');sub.add_parser('school-demo');sub.add_parser('summary');sub.add_parser('gui');sub.add_parser('demo')
    args=parser.parse_args()
    try:
        if args.command=='gui':gui(args.state);return
        state=load_state(args.state)
        if args.command=='match':result=match(state,args.query,args.quantity,args.max_distance,args.accept_repair,args.recipient)
        elif args.command=='confirm':
            result=confirm(state,args.item_id,args.quantity,args.purchase_price,args.transport,args.refurbishment,args.inspected,args.recipient);save_state(args.state,state)
        elif args.command=='partners':result=read_json(ROOT/'partners.json')
        elif args.command=='school-demo':
            state=initial_state();result={'query':'display for computer lab','recipient':partner('SCHOOL01'),'results':match(state,'display for computer lab',2,10,False,'SCHOOL01'),'example_transfer':confirm(state,'RL01',2,6000,300,250,True,'SCHOOL01'),'impact':summary(state),'note':'Synthetic example. No measured learning outcomes or real partnerships. Does not modify local state.'}
        elif args.command=='summary':result=summary(state)
        else:
            state=initial_state();result={'query':'display for computer lab','results':match(state,'display for computer lab',2,10),'example_transfer':confirm(state,'RL01',2,6000,300,250,True),'impact':summary(state),'note':'demo command does not modify local state'}
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,json.JSONDecodeError) as e:parser.exit(2,f'Error: {e}\n')

if __name__=='__main__':main()
