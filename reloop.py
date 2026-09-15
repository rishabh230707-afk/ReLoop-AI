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
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        root=tk.Tk()
    except Exception as error:
        raise ValueError('Desktop UI unavailable. Use the match and demo commands, or install Python with Tk support.') from error
    root.title('ReLoop AI | Campus-to-school reuse exchange'); root.geometry('1250x800'); root.configure(bg='#102821')
    style=ttk.Style(); style.theme_use('clam'); style.configure('TButton',font=('Arial',12),padding=8)
    tk.Label(root,text='ReLoop AI',font=('Arial',30,'bold'),bg='#102821',fg='#AEED83').pack(anchor='w',padx=30,pady=(22,3))
    tk.Label(root,text='Check reusable stock before buying new.',font=('Arial',16),bg='#102821',fg='white').pack(anchor='w',padx=30)
    tk.Label(root,text='OFFLINE DEMO  /  Synthetic campus inventory  /  No accounts or shared database',font=('Arial',11),bg='#102821',fg='#CAE0D7').pack(anchor='w',padx=30,pady=10)
    form=tk.Frame(root,bg='#102821'); form.pack(fill='x',padx=30)
    def field(label,value,width):
        frame=tk.Frame(form,bg='#102821'); frame.pack(side='left',padx=(0,14))
        tk.Label(frame,text=label,bg='#102821',fg='white',font=('Arial',12)).pack(anchor='w')
        v=tk.StringVar(value=value); ttk.Entry(frame,textvariable=v,width=width,font=('Arial',13)).pack(pady=5); return v
    query=field('What do you need?','display for computer lab',38); qty=field('Quantity','2',8); distance=field('Max distance (km)','10',12); recipient=field('Partner ID','SCHOOL01',12)
    repair=tk.BooleanVar(); tk.Checkbutton(root,text='Include items needing repair',variable=repair,bg='#102821',fg='white',selectcolor='#102821',activebackground='#102821',activeforeground='white').pack(anchor='w',padx=30)
    output=tk.Text(root,wrap='word',font=('Arial',13),bg='#F4F8F3',fg='#15271D',padx=18,pady=16,height=17)
    def show(data):
        output.configure(state='normal');output.delete('1.0','end');output.insert('end',data);output.configure(state='disabled')
    def search():
        try:
            result=match(load_state(state_path),query.get(),int(qty.get()),float(distance.get()),repair.get(),recipient.get().strip())
            lines=[result['message'],'']
            for m in result['matches'][:5]:
                lines.extend([f"{m['id']}  {m['title']}  |  {m['department']}",
                  f"Available: {m['quantity']}   Offer: {m['offered_quantity']}   Still needed: {m['remaining_need']}   Distance: {m['distance_km']} km",
                  f"Condition: {m['condition']}   Text similarity: {m['similarity']:.2f}",m['explanation'],''])
            show('\n'.join(lines))
        except (ValueError,OSError) as e: messagebox.showerror('Check your input',str(e))
    ttk.Button(root,text='Find reusable stock',command=search).pack(anchor='w',padx=30,pady=8)
    output.pack(fill='both',expand=True,padx=30,pady=(0,10))
    actions=tk.Frame(root,bg='#102821'); actions.pack(fill='x',padx=30,pady=(0,20))
    def record():
        win=tk.Toplevel(root);win.title('Record inspected demo transfer');win.geometry('470x420'); values={}
        ttk.Label(win,text='Recipient: '+recipient.get()).pack()
        for key,label,default in [('item','Item ID','RL01'),('quantity','Quantity','1'),('price','New purchase benchmark per unit (INR)','6000'),('transport','Total transport cost (INR)','200'),('refurb','Refurbishment per unit (INR)','0')]:
            ttk.Label(win,text=label).pack(anchor='w',padx=20,pady=(8,0));values[key]=tk.StringVar(value=default);ttk.Entry(win,textvariable=values[key]).pack(fill='x',padx=20)
        inspected=tk.BooleanVar();ttk.Checkbutton(win,text='I inspected and approved these demo items',variable=inspected).pack(pady=10)
        def finish():
            try:
                s=load_state(state_path);t=confirm(s,values['item'].get().strip(),int(values['quantity'].get()),float(values['price'].get()),float(values['transport'].get()),float(values['refurb'].get()),inspected.get(),recipient.get().strip());save_state(state_path,s);win.destroy();show(json.dumps(t,indent=2))
            except (ValueError,OSError) as e:messagebox.showerror('Transfer not recorded',str(e))
        ttk.Button(win,text='Record transfer',command=finish).pack()
    ttk.Button(actions,text='Record demo transfer',command=record).pack(side='left')
    ttk.Button(actions,text='View demo impact',command=lambda:show(json.dumps(summary(load_state(state_path)),indent=2))).pack(side='left',padx=10)
    search();root.mainloop()

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
