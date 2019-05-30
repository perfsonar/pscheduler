





text = None
with open('./stderr.out') as f:
  text = f.read()#.decode('utf8')
'''
for i, line in enumerate(text.split('\n')):
  for idx in line.split(' '):
    if idx != '': print(idx, ' ', end='')
  
  print('\n' + '*'*10, i)
'''
lines = text.split('\n')
stats = lines[-2].split(' ')
stats = [stat for stat in stats if stat != '']
dSpeed = stats[6]
tBytes = stats[2]
print("Download speed:", dSpeed)
print("Total Bytes:", tBytes)
#[print(s) for s in stats]
#print(lines[-2])
#print(text)
