from OKanban.bdd import BddOKanbans

bdd = BddOKanbans('192.168.0.11')

print()
dups = {}
for kb in bdd.get_kanbans():
    if len(bdd.get_kanbans(kb['id']))>1:
        if kb['id'] in dups:
            dups[kb['id']].append(kb)
        else:
            dups[kb['id']]=[kb]

for id, kbs in dups.items():
    print(id)
    for kb in kbs:
        print('\t', kb['proref'], kb['qte'])
