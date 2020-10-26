import MySQLdb
import pandas as pd
import numpy as np
import ipaddress
import itertools
import math
import time
import scipy.special
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

db = MySQLdb.connect(host=config.get('DBConnection', 'host'),  # your host, usually localhost
                     user=config.get('DBConnection', 'user'),  # your username
                     passwd=config.get('DBConnection', 'passwd'),  # your password
                     db=config.get('DBConnection', 'db'))  # name of the data base

cur = db.cursor()
cur.execute("SELECT path, hostname FROM accesslog WHERE path LIKE 'node/%'")
res = cur.fetchall()

nodes = []
hosts = []

for r in res:
    try:
        nodes.append(int(r[0].split('/')[1]))
    except ValueError:
        continue
    hosts.append(int(ipaddress.IPv4Address(r[1])))

print("{:d} visitas para serem processadas".format(len(hosts)))

data = pd.DataFrame({'node': nodes, 'hostname': hosts})

# 1. descobrir todos os nós envolvidos e ordenar
nodesToCombine = np.sort(data['node'].unique())
print(nodesToCombine)

# 2. para cada nó, contar quantos ips diferentes visitaram

numVisits = dict()
for n in nodesToCombine:
    numVisits[n] = len(data[data['node'] == n]['hostname'].unique())

# 3. contruir todas as combinações possíveis de nós
# 4. iterar pelas combinações de todos os nós e contar para cada combinação quantas vezes
# um mesmo ip visita ambas as páginas (nós)

similarities = dict()
n_combs = scipy.special.binom(len(numVisits), 2)

i = 0
for j in itertools.combinations(nodesToCombine, 2):
    i += 1
    A = set(data[data['node'] == j[0]]['hostname'])
    B = set(data[data['node'] == j[1]]['hostname'])
    similarities[j] = len(A & B) / (math.sqrt(numVisits[j[0]]) * math.sqrt(numVisits[j[1]]))

t = time.time()

for i in similarities.keys():

    if similarities[(i[0], i[1])] == 0:
        continue

    cur.execute("SELECT id FROM history_rec_item_similarity " +
                "WHERE eid1 = {:d} AND eid2 = {:d}".format(i[0], i[1]))

    if cur.rowcount == 0:
        cur.execute("INSERT INTO history_rec_item_similarity(eid1, eid2, score, updated) " +
                    "VALUES({:d}, {:d}, {:.8f}, {:.0f});".format(i[0], i[1], similarities[(i[0], i[1])], t))
        cur.execute("INSERT INTO history_rec_item_similarity(eid1, eid2, score, updated) " +
                    "VALUES({:d}, {:d}, {:.8f}, {:.0f});".format(i[1], i[0], similarities[(i[0], i[1])], t))
    else:
        cur.execute("UPDATE history_rec_item_similarity "
                    "SET score = {:.8f}, updated = {:.0f} WHERE eid1 = {:d} AND eid2 = {:d};".format(
                        similarities[(i[0], i[1])], t, i[0], i[1]))
        cur.execute("UPDATE history_rec_item_similarity "
                    "SET score = {:.8f}, updated = {:.0f} WHERE eid1 = {:d} AND eid2 = {:d};".format(
                        similarities[(i[0], i[1])], t, i[0], i[1]))
db.commit()
db.close()
