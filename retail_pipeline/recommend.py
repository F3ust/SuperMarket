"""Use the frozen recommendation champion selected on temporal validation."""
import argparse,json
from pathlib import Path
import joblib
from .common import ROOT

def recommend(bundle,seed,k=3):
    ranked=bundle['lookup'].get(seed,[])+bundle['popular'] if bundle['winner']=='association' else bundle['popular']
    return [v for v in dict.fromkeys(ranked) if v!=seed][:k]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--category',required=True);parser.add_argument('--k',type=int,default=3);args=parser.parse_args()
    latest=json.loads((ROOT/'outputs/enterprise/latest.json').read_text(encoding='utf-8'));bundle=joblib.load(Path(latest['path'])/'models/basket_recommender.joblib')
    print(json.dumps({'seed':args.category,'champion':bundle['winner'],'recommendations':recommend(bundle,args.category,args.k),'scope':'Category completion, not personalized future purchase'},ensure_ascii=False))

if __name__=='__main__':main()
