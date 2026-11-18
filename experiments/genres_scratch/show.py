import json,sys,glob
for f in sorted(glob.glob('experiments/genres_scratch/out/main_*.json')):
  r=json.load(open(f)); m=r['model']
  print(r['corpus'],m,'K',r['K'],'best',r['K_best'],'cv',{k:round(v,2) for k,v in r['cv_means'].items()})
  print('  ho',round(r['ho_ll_K'],3),round(r['ho_ll_1'],3),[round(x,3) for x in r['ho_diff_ci']],'S1',r['S1'],'sizes',r['sizes_train'],'secs',r['secs'])
  for k,v in r['tests'].items(): print('   ',k,{a:(round(b,4) if isinstance(b,float) else b) for a,b in v.items()})
  print('   stab',r.get('stability'))
