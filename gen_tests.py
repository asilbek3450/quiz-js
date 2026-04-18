#!/usr/bin/env python3
"""
100 ta arena masalasi uchun har biriga 10 ta to'g'ri hidden test generatsiya qiladi.
"""
import sys, os, json, math
sys.path.insert(0, '/Users/asilbek/Desktop/AI-Projects/quiz-js')
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app
from models import db, ArenaProblem

# ─── Reference solutions ─────────────────────────────────────────────────────

def sol_A001(i): a,b=i.strip().split('\n'); return str(int(a)+int(b))
def sol_A002(i): a,b=i.strip().split('\n'); return str(int(a)-int(b))
def sol_A003(i): a,b=i.strip().split('\n'); return str(int(a)*int(b))
def sol_A004(i): a,b=i.strip().split('\n'); return f"{int(a)/int(b):.2f}"
def sol_A005(i): a,b=i.strip().split('\n'); a,b=int(a),int(b); return f"{a//b}\n{a%b}"
def sol_A006(i): n=int(i.strip()); return f"{n*n}\n{n*n*n}"
def sol_A007(i): v=[int(x) for x in i.strip().split('\n')]; return f"{sum(v)/3:.2f}"
def sol_A008(i): r=float(i.strip()); return f"{3.14159265358979*r*r:.2f}"
def sol_A009(i): a,h=i.strip().split('\n'); return f"{float(a)*float(h)/2:.2f}"
def sol_A010(i): a,b=i.strip().split('\n'); return str(2*(int(a)+int(b)))

def sol_A011(i):
    n=int(i.strip())
    return "musbat" if n>0 else ("manfiy" if n<0 else "nol")

def sol_A012(i): return "Juft" if int(i.strip())%2==0 else "Toq"
def sol_A013(i): a,b=i.strip().split('\n'); return str(max(int(a),int(b)))
def sol_A014(i): a,b,c=i.strip().split('\n'); return str(min(int(a),int(b),int(c)))
def sol_A015(i): n=int(i.strip()); return "Ha" if 10<n<100 else "Yo'q"

def sol_A016(i):
    a,b,c=[int(x) for x in i.strip().split('\n')]
    return "Ha" if a+b>c and a+c>b and b+c>a else "Yo'q"

def sol_A017(i):
    y=int(i.strip())
    return "Ha" if (y%4==0 and y%100!=0) or y%400==0 else "Yo'q"

def sol_A018(i):
    c=i.strip()
    return "Harf" if c.isalpha() else ("Raqam" if c.isdigit() else "Boshqa")

def sol_A019(i):
    b=int(i.strip())
    return "A" if b>=90 else ("B" if b>=75 else ("C" if b>=60 else ("D" if b>=40 else "F")))

MONTHS=["","Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktyabr","Noyabr","Dekabr"]
def sol_A020(i): return MONTHS[int(i.strip())]

def sol_A021(i): n=int(i.strip()); return " ".join(str(x) for x in range(1,n+1))
def sol_A022(i): n=int(i.strip()); return str(n*(n+1)//2)
def sol_A023(i):
    n=int(i.strip()); r=1
    for x in range(2,n+1): r*=x
    return str(r)

def sol_A024(i):
    ls=i.strip().split('\n'); n=int(ls[0])
    return str(sum(int(ls[k+1]) for k in range(n)))

def sol_A025(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    mx=nums[0]
    for x in nums[1:]: mx=x if x>mx else mx
    return str(mx)

def sol_A026(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    return str(sum(1 for x in nums if x%2==0))

def sol_A027(i):
    n=int(i.strip()); cnt=0
    for d in range(1,int(n**0.5)+1):
        if n%d==0: cnt+=2 if d!=n//d else 1
    return str(cnt)

def sol_A028(i):
    n=int(i.strip())
    if n<2: return "Yo'q"
    for d in range(2,int(n**0.5)+1):
        if n%d==0: return "Yo'q"
    return "Ha"

def sol_A029(i): return str(sum(int(c) for c in i.strip()))
def sol_A030(i): return str(int(i.strip()[::-1]))

def sol_A031(i): s=i.strip(); return "YES" if s==s[::-1] else "NO"
def sol_A032(i):
    n=int(i.strip())
    if n<=2: return "1"
    a,b=1,1
    for _ in range(n-2): a,b=b,a+b
    return str(b)

def sol_A033(i):
    n=int(i.strip()); r=[]
    while n>0: r.append(str(n%2)); n//=2
    return "".join(reversed(r))

def sol_A034(i):
    a,b=i.strip().split('\n'); a,b=int(a),int(b)
    while b: a,b=b,a%b
    return str(a)

def sol_A035(i):
    a,b=i.strip().split('\n'); a,b=int(a),int(b)
    def gcd(x,y):
        while y: x,y=y,x%y
        return x
    return str(a*b//gcd(a,b))

def sol_A036(i): n=int(i.strip()); return f"{sum(1/k for k in range(1,n+1)):.4f}"
def sol_A037(i):
    a,b=i.strip().split('\n'); a,b=int(a),int(b)
    r=1
    for _ in range(b): r*=a
    return str(r)

DIGITS=["nol","bir","ikki","uch","to'rt","besh","olti","yetti","sakkiz","to'qqiz"]
def sol_A038(i): return DIGITS[int(i.strip())]

def sol_A039(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    seen=set()
    for x in nums:
        if x in seen: return str(x)
        seen.add(x)
    return ""

def sol_A040(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    mx=cur=1
    for k in range(1,len(nums)):
        cur=(cur+1) if nums[k]>nums[k-1] else 1
        mx=max(mx,cur)
    return str(mx)

def sol_A041(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    mx=nums[0]
    for x in nums[1:]: mx=x if x>mx else mx
    return str(mx)

def sol_A042(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    return " ".join(map(str,nums[::-1]))

def sol_A043(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    return str(sum(1 for x in nums if x%2==0))

def sol_A044(i):
    ls=i.strip().split('\n'); n=int(ls[0]); nums=list(map(int,ls[1].split()))
    return f"{sum(nums)/n:.2f}"

def sol_A045(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split())); n=len(nums)
    for a in range(n):
        for b in range(0,n-a-1):
            if nums[b]>nums[b+1]: nums[b],nums[b+1]=nums[b+1],nums[b]
    return " ".join(map(str,nums))

def sol_A046(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split())); k=int(ls[2])
    return "Ha" if k in nums else "Yo'q"

def sol_A047(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    from collections import Counter; c=Counter(nums)
    return str(sum(1 for v in c.values() if v>=2))

def sol_A048(i):
    ls=i.strip().split('\n')
    n1=int(ls[0]); a=list(map(int,ls[1].split()))
    n2=int(ls[2]); b=list(map(int,ls[3].split()))
    return " ".join(map(str,a+b))

def sol_A049(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    return str(max(nums)-min(nums))

def sol_A050(i):
    ls=i.strip().split('\n'); n,k=map(int,ls[0].split()); nums=list(map(int,ls[1].split()))
    k=k%n if n else 0
    return " ".join(map(str,(nums[-k:]+nums[:-k]) if k else nums))

def sol_A051(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    return str(nums.count(0))

def sol_A052(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    return f"{sum(1 for x in nums if x>0)}\n{sum(1 for x in nums if x<0)}"

def sol_A053(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    return " ".join(str(x*x) for x in nums)

def sol_A054(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    return " ".join(str(nums[k]) for k in range(1,len(nums),2))

def sol_A055(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    return " ".join(str(nums[k]+nums[k+1]) for k in range(len(nums)-1))

def sol_A056(i):
    ls=i.strip().split('\n'); n=int(ls[0]); nums=list(map(int,ls[1].split()))
    mid=(n+1)//2
    return " ".join(map(str,nums[:mid]))+"\n"+" ".join(map(str,nums[mid:]))

def sol_A057(i): return sol_A040(i)  # same logic

def sol_A058(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split()))
    a,b=map(int,ls[2].split()); nums[a],nums[b]=nums[b],nums[a]
    return " ".join(map(str,nums))

def sol_A059(i):
    ls=i.strip().split('\n'); n=int(ls[0]); nums=list(map(int,ls[1].split()))
    return str(nums[n//2])

def sol_A060(i):
    ls=i.strip().split('\n'); n,k=map(int,ls[0].split()); nums=list(map(int,ls[1].split()))
    k=k%n if n else 0
    return " ".join(map(str,(nums[k:]+nums[:k]) if k else nums))

def sol_A061(i): return str(len(i.rstrip('\n')))
def sol_A062(i): s=i.strip(); return str(sum(1 for c in s if c in 'aeiouAEIOU'))
def sol_A063(i): return i.rstrip('\n')[::-1]

def sol_A064(i):
    s=''.join(c.lower() for c in i.strip() if c.isalpha())
    return "YES" if s==s[::-1] else "NO"

def sol_A065(i): return str(len(i.strip().split()))
def sol_A066(i): return str(sum(1 for c in i.strip() if c.isupper()))
def sol_A067(i): return str(sum(1 for c in i.strip() if c.isdigit()))

def sol_A068(i):
    ls=i.strip().split('\n'); s,old,new=ls[0],ls[1],ls[2]
    return s.replace(old,new)

def sol_A069(i):
    from collections import Counter; s=i.strip(); c=Counter(s)
    mx=max(c.values()); return min(k for k,v in c.items() if v==mx)

def sol_A070(i): return "\n".join(i.strip().split())
def sol_A071(i):
    ls=i.strip().split('\n'); n=int(ls[0])
    return " ".join(ls[k+1] for k in range(n))

def sol_A072(i): return " ".join(reversed(i.strip().split()))

def sol_A073(i):
    s=i.strip(); cnt=0
    for c in s:
        if c=='(': cnt+=1
        elif c==')':
            cnt-=1
            if cnt<0: return "Yo'q"
    return "Ha" if cnt==0 else "Yo'q"

def sol_A074(i):
    from collections import Counter; c=Counter(i.strip())
    return str(sum(1 for v in c.values() if v>=2))

def sol_A075(i): return max(i.strip().split(), key=len)

def sol_A076(i):
    from collections import Counter; c=Counter(i.strip().split())
    return "\n".join(f"{k}: {v}" for k,v in sorted(c.items()))

def sol_A077(i): return " ".join(sorted(i.strip().split()))
def sol_A078(i): return " ".join(sorted(i.strip().split(), key=lambda w:(len(w),w)))
def sol_A079(i): return i.rstrip('\n').upper()
def sol_A080(i): return i.rstrip('\n').title()

def sol_A081(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split())); k=int(ls[2])
    lo,hi=0,len(nums)-1
    while lo<=hi:
        mid=(lo+hi)//2
        if nums[mid]==k: return str(mid)
        elif nums[mid]<k: lo=mid+1
        else: hi=mid-1
    return "-1"

def sol_A082(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split())); n=len(nums); sw=0
    for a in range(n):
        for b in range(0,n-a-1):
            if nums[b]>nums[b+1]: nums[b],nums[b+1]=nums[b+1],nums[b]; sw+=1
    return f"{sw}\n"+" ".join(map(str,nums))

def sol_A083(i): return sol_A023(i)

def sol_A084(i):
    n=int(i.strip())
    if n<=2: return "1"
    a,b=1,1
    for _ in range(n-2): a,b=b,a+b
    return str(b)

def sol_A085(i): n=int(i.strip()); return str(2**n-1)

def sol_A086(i):
    n=int(i.strip()); f=[]; d=2
    while d*d<=n:
        while n%d==0: f.append(d); n//=d
        d+=1
    if n>1: f.append(n)
    return " ".join(map(str,f))

def sol_A087(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split())); t=int(ls[2])
    return str(min(nums, key=lambda x:(abs(x-t),x)))

def sol_A088(i):
    ls=i.strip().split('\n'); nums=sorted(set(map(int,ls[1].split())),reverse=True)
    return f"{nums[0]}\n{nums[1]}"

def sol_A089(i):
    ls=i.strip().split('\n'); nums=sorted(set(map(int,ls[1].split())))
    return f"{nums[0]}\n{nums[1]}"

def sol_A090(i):
    ls=i.strip().split('\n'); nums=list(map(int,ls[1].split())); t=int(ls[2])
    cnt=0; n=len(nums)
    for a in range(n):
        for b in range(a+1,n):
            if nums[a]+nums[b]==t: cnt+=1
    return str(cnt)

def sol_A091(i):
    ls=i.strip().split('\n'); n,m=map(int,ls[0].split())
    mtx=[[int(x) for x in ls[r+1].split()] for r in range(n)]
    tr=[[mtx[r][c] for r in range(n)] for c in range(m)]
    return "\n".join(" ".join(map(str,row)) for row in tr)

def sol_A092(i):
    ls=i.strip().split('\n'); n=int(ls[0])
    A=[[int(x) for x in ls[r+1].split()] for r in range(n)]
    B=[[int(x) for x in ls[n+r+1].split()] for r in range(n)]
    C=[[sum(A[r][k]*B[k][c] for k in range(n)) for c in range(n)] for r in range(n)]
    return "\n".join(" ".join(map(str,row)) for row in C)

def sol_A093(i):
    ls=i.strip().split('\n'); n=int(ls[0])
    m=[[int(x) for x in ls[r+1].split()] for r in range(n)]
    if n==2: return str(m[0][0]*m[1][1]-m[0][1]*m[1][0])
    return str(m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
              -m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
              +m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))

def sol_A094(i):
    ls=i.strip().split('\n'); X,Y=ls[0],ls[1]; m,n=len(X),len(Y)
    dp=[[0]*(n+1) for _ in range(m+1)]
    for a in range(1,m+1):
        for b in range(1,n+1):
            dp[a][b]=dp[a-1][b-1]+1 if X[a-1]==Y[b-1] else max(dp[a-1][b],dp[a][b-1])
    return str(dp[m][n])

def sol_A095(i):
    n=int(i.strip())
    VS=[(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),
        (50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
    r=""
    for v,s in VS:
        while n>=v: r+=s; n-=v
    return r

def sol_A096(i):
    s=i.strip(); V={'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}; r=0
    for k in range(len(s)):
        r+=V[s[k]] if k+1==len(s) or V[s[k]]>=V[s[k+1]] else -V[s[k]]
    return str(r)

def sol_A097(i):
    s=i.strip(); r=[]; k=0
    while k<len(s):
        c=s[k]; cnt=1
        while k+cnt<len(s) and s[k+cnt]==c: cnt+=1
        r.append(f"{c}{cnt}"); k+=cnt
    return "".join(r)

def sol_A098(i):
    s=i.strip(); r=[]; k=0
    while k<len(s):
        c=s[k]; k+=1; num=""
        while k<len(s) and s[k].isdigit(): num+=s[k]; k+=1
        r.append(c*int(num))
    return "".join(r)

def sol_A099(i):
    ls=i.strip().split('\n')
    return "YES" if sorted(ls[0].lower())==sorted(ls[1].lower()) else "NO"

def sol_A100(i):
    s=i.strip(); st=[]; P={')':'(',']':'[','}':'{'}
    for c in s:
        if c in '([{': st.append(c)
        elif c in ')]}':
            if not st or st[-1]!=P[c]: return "Yo'q"
            st.pop()
    return "Ha" if not st else "Yo'q"

# ─── Test inputs ──────────────────────────────────────────────────────────────

TESTS = {
'A001': ["0\n0","1\n1","-5\n5","1000000000\n-1000000000","123456789\n987654321",
         "-999999999\n-1","50\n50","0\n-1","777\n223","100\n-99"],
'A002': ["0\n0","10\n3","-5\n-3","1000000000\n999999999","-10\n10",
         "0\n1000000000","500\n250","999\n-1","-100\n-50","42\n0"],
'A003': ["0\n5","1\n1","-3\n4","10000\n10000","-100\n-100",
         "7\n8","0\n-1","-1\n-1","9999\n-1","123\n81"],
'A004': ["10\n2","1\n3","22\n7","-10\n4","100\n-3",
         "0\n5","7\n7","1000000000\n3","-1\n-4","50\n8"],
'A005': ["13\n4","17\n5","100\n7","0\n1","1000000000\n3",
         "999\n1000","6\n2","1\n1","7\n3","1000000000\n1000000000"],
'A006': ["1","2","5","10","100","999","1000","7","13","50"],
'A007': ["3\n7\n11","10\n20\n30","0\n0\n0","-10\n0\n10","100\n200\n300",
         "1\n2\n3","-1000000\n0\n1000000","7\n7\n7","999999\n-1\n-999998","1\n1\n4"],
'A008': ["1","2","5","10","3.5","0.5","100","7.7","0.1","50"],
'A009': ["6\n4","8\n5","1\n1","100\n200","3.5\n4.2",
         "10\n10","0.5\n0.5","99\n1","7\n3","50\n20"],
'A010': ["5\n3","13\n7","1\n1","1000000\n1000000","10\n20",
         "7\n7","100\n1","500\n300","999\n1","3\n4"],
'A011': ["5","-17","0","1000000000","-1000000000","1","-1","42","-42","100"],
'A012': ["4","2025","0","1","1000000000","999999999","2","7","100","13"],
'A013': ["7\n3","73\n58","-5\n-10","0\n0","1000000000\n-1000000000",
         "5\n5","-1\n1","100\n99","0\n-1","42\n43"],
'A014': ["5\n2\n8","45\n12\n67","0\n0\n0","-1\n-2\n-3","1000000000\n-1000000000\n0",
         "5\n5\n5","3\n1\n2","99\n100\n1","-5\n0\n5","7\n7\n3"],
'A015': ["50","100","55","10","11","99","0","-5","101","200"],
'A016': ["1\n1\n10","3\n4\n5","1\n1\n2","5\n5\n5","10\n6\n8",
         "1\n2\n3","100\n100\n1","3\n3\n3","7\n10\n5","4\n5\n6"],
'A017': ["2000","1900","2024","2100","2400","1","4","100","2023","1600"],
'A018': ["A","7","!","a","Z","0"," ","9","b","#"],
'A019': ["95","82","55","75","90","60","39","100","0","70"],
'A020': ["1","9","12","2","3","4","5","6","7","8"],
'A021': ["5","7","1","10","20","3","15","100","2","50"],
'A022': ["5","100","1","10","1000","50","7","1000000","3","999"],
'A023': ["5","10","0","1","15","20","3","7","12","2"],
'A024': ["3\n1\n2\n3","4\n10\n20\n30\n40","1\n0","5\n-1\n-2\n-3\n-4\n-5",
         "2\n1000000000\n1000000000","3\n-1000000000\n0\n1000000000",
         "1\n42","5\n1\n2\n3\n4\n5","3\n100\n200\n300","4\n-1\n-1\n-1\n-1"],
'A025': ["5\n3 1 4 1 5","6\n3 1 4 1 5 9","1\n42","3\n-1 -2 -3",
         "4\n5 5 5 5","5\n1000000000 -1000000000 0 1 -1",
         "3\n100 200 50","7\n7 6 5 4 3 2 1","2\n1 2","4\n-5 -4 -3 -2"],
'A026': ["5\n1 2 3 4 5","8\n1 2 3 4 5 6 7 8","3\n1 3 5","3\n2 4 6",
         "4\n0 0 0 0","5\n1 1 1 1 1","6\n-2 -1 0 1 2 3","4\n10 20 30 40","1\n7","3\n2 -2 3"],
'A027': ["12","36","1","7","100","1000000","2","13","24","30"],
'A028': ["7","15","97","2","4","101","1000003","999983","100","17"],
'A029': ["123","98765","1","999","1000000000000000000","10000","42","111111111","987654321","100"],
'A030': ["12345","987654","1","100","1000","99999","12300","987654321","10","5"],
'A031': ["121","12321","12345","1","11","1221","12211","999","1000000001","123321"],
'A032': ["7","10","1","2","15","20","5","50","3","30"],
'A033': ["10","42","1","255","1024","7","100","1000000000","15","128"],
'A034': ["12\n8","48\n18","1\n1","1000000000\n999999999","100\n25",
         "7\n13","36\n24","15\n25","100\n100","17\n51"],
'A035': ["4\n6","12\n18","1\n1","7\n13","100\n25","15\n25","36\n24","1000\n500","8\n12","9\n6"],
'A036': ["4","10","1","2","100","50","5","1000","20","3"],
'A037': ["2\n10","3\n8","1\n30","10\n5","5\n3","2\n0","100\n0","2\n30","7\n4","3\n5"],
'A038': ["0","6","9","1","2","3","4","5","7","8"],
'A039': ["5\n1 2 3 2 4","6\n1 3 4 2 5 3","2\n1 1","4\n3 1 3 2",
         "5\n4 3 2 1 2","7\n1 2 3 4 5 6 5","3\n2 1 2","6\n5 4 3 2 1 4","4\n1 2 2 3","5\n3 3 2 1 4"],
'A040': ["7\n1 2 3 1 2 6 7","8\n1 2 3 1 2 3 4 5","1\n5","5\n5 4 3 2 1",
         "5\n1 2 3 4 5","6\n1 1 1 1 1 1","7\n3 1 2 3 1 2 3","4\n1 3 2 4","6\n5 1 2 3 1 2","3\n1 2 1"],
'A041': ["5\n3 1 4 1 5","7\n5 8 1 9 3 7 2","1\n42","3\n-5 -3 -1",
         "4\n10 10 10 10","5\n0 0 0 0 1","6\n1000000000 -1000000000 0 500 -500 999999999",
         "3\n7 3 9","2\n1 2","5\n-1 -2 -3 -4 -5"],
'A042': ["4\n1 2 3 4","5\n10 20 30 40 50","1\n7","3\n-1 0 1",
         "2\n5 3","6\n6 5 4 3 2 1","5\n100 200 300 400 500",
         "3\n1000000000 0 -1000000000","4\n1 1 1 1","7\n7 6 5 4 3 2 1"],
'A043': ["6\n1 2 3 4 5 6","8\n2 3 4 5 6 7 8 9","3\n1 3 5","3\n2 4 6",
         "1\n0","5\n0 2 4 6 8","4\n-2 -4 -6 -8","5\n1 2 3 4 5","2\n7 9","6\n-1 0 1 2 3 4"],
'A044': ["4\n1 2 3 4","5\n10 20 30 40 50","1\n7","3\n-1 0 1",
         "2\n3 7","4\n0 0 0 4","3\n1 1 1","5\n5 5 5 5 5","2\n1 2","4\n-10 10 -10 10"],
'A045': ["5\n5 3 1 4 2","6\n5 3 8 1 9 2","1\n42","3\n3 2 1",
         "3\n1 2 3","5\n5 5 5 5 5","4\n-3 -1 -4 -2","4\n10 7 3 1","3\n0 -1 1","5\n100 50 25 75 10"],
'A046': ["5\n1 2 3 4 5\n3","5\n3 7 1 9 5\n9","5\n3 7 1 9 5\n6","3\n10 20 30\n20",
         "1\n7\n7","1\n7\n8","6\n-3 -2 -1 0 1 2\n-2","4\n100 200 300 400\n150","3\n5 5 5\n5","5\n1 3 5 7 9\n4"],
'A047': ["6\n1 2 2 3 3 4","7\n1 2 2 3 3 3 4","3\n1 2 3","3\n1 1 1",
         "5\n1 1 2 2 3","4\n7 7 7 7","6\n1 2 3 4 5 6","5\n1 2 1 2 1","4\n0 0 1 1","3\n3 3 3"],
'A048': ["3\n1 2 3\n3\n4 5 6","2\n10 20\n3\n30 40 50","1\n1\n1\n2","3\n-1 0 1\n2\n2 3",
         "2\n5 10\n2\n15 20","4\n1 2 3 4\n4\n5 6 7 8","1\n100\n1\n200",
         "3\n7 8 9\n3\n1 2 3","2\n0 0\n2\n0 0","3\n10 20 30\n1\n40"],
'A049': ["5\n1 3 5 2 8","6\n4 8 2 15 3 11","1\n5","3\n1 1 1",
         "4\n-10 -5 0 10","5\n100 0 50 25 75","2\n1 1000000000","3\n-5 0 5","4\n7 3 9 1","5\n1 2 3 4 5"],
'A050': ["5 2\n1 2 3 4 5","5 3\n1 2 3 4 5","4 1\n1 2 3 4","6 6\n1 2 3 4 5 6",
         "3 0\n1 2 3","5 5\n1 2 3 4 5","4 2\n10 20 30 40","6 3\n1 2 3 4 5 6","3 1\n7 8 9","5 4\n1 2 3 4 5"],
'A051': ["6\n0 1 0 2 0 3","8\n0 1 0 2 0 3 0 4","3\n1 2 3","3\n0 0 0",
         "1\n0","1\n5","5\n0 0 0 0 0","5\n1 2 3 4 5","4\n0 1 0 1","6\n0 0 1 0 0 1"],
'A052': ["5\n1 -2 3 -4 5","7\n1 -2 3 -4 5 -6 0","3\n1 2 3","3\n-1 -2 -3",
         "1\n0","4\n0 0 0 0","5\n-5 -4 0 4 5","3\n100 0 -100","2\n1 -1","6\n1 2 3 -1 -2 -3"],
'A053': ["4\n1 2 3 4","5\n1 2 3 4 5","3\n-1 0 1","1\n10",
         "3\n5 10 15","4\n-3 -2 -1 0","5\n0 1 4 9 16","2\n100 -100","3\n7 8 9","4\n2 4 6 8"],
'A054': ["5\n10 20 30 40 50","6\n10 20 30 40 50 60","2\n1 2","4\n1 2 3 4",
         "6\n6 5 4 3 2 1","4\n100 200 300 400","8\n1 2 3 4 5 6 7 8","3\n10 20 30","5\n-1 -2 -3 -4 -5","6\n0 1 0 1 0 1"],
'A055': ["4\n1 2 3 4","5\n1 2 3 4 5","2\n5 3","3\n10 20 30",
         "4\n-1 0 1 2","5\n0 0 0 0 0","3\n100 200 300","6\n1 2 3 4 5 6","3\n-5 5 -5","4\n1 -1 1 -1"],
'A056': ["4\n1 2 3 4","6\n1 2 3 4 5 6","2\n10 20","4\n5 10 15 20",
         "6\n-3 -2 -1 1 2 3","4\n100 200 300 400","8\n1 2 3 4 5 6 7 8","2\n0 0","4\n7 3 9 1","6\n10 20 30 40 50 60"],
'A057': ["7\n5 1 2 3 0 7 8","8\n1 2 3 1 2 3 4 5","1\n5","5\n5 4 3 2 1",
         "5\n1 2 3 4 5","6\n1 1 1 1 1 1","7\n3 1 2 3 1 2 3","4\n1 3 2 4","6\n5 1 2 3 1 2","3\n1 2 1"],
'A058': ["5\n1 2 3 4 5\n0 4","5\n1 2 3 4 5\n1 3","3\n10 20 30\n0 2","4\n1 2 3 4\n0 3",
         "5\n5 4 3 2 1\n1 3","2\n7 8\n0 1","6\n1 2 3 4 5 6\n2 4","4\n-1 -2 -3 -4\n0 3","3\n3 3 3\n0 2","5\n10 20 30 40 50\n0 4"],
'A059': ["5\n1 2 3 4 5","7\n10 20 30 40 50 60 70","1\n42","3\n-1 0 1",
         "3\n5 3 7","5\n100 200 300 400 500","7\n1 1 1 1 1 1 1","3\n0 0 0","5\n9 7 5 3 1","3\n-10 0 10"],
'A060': ["5 2\n1 2 3 4 5","6 4\n1 2 3 4 5 6","4 1\n1 2 3 4","6 0\n1 2 3 4 5 6",
         "3 3\n1 2 3","5 5\n1 2 3 4 5","4 2\n10 20 30 40","6 3\n1 2 3 4 5 6","3 1\n7 8 9","5 4\n1 2 3 4 5"],
'A061': ["salom","Assalomu alaykum","a","Python dasturlash tili",
         "1234567890","hello world","test string here","a b c d","one","x"],
'A062': ["salom dunyo","Programming is fun","aeiou","bcdfg",
         "Hello World","Python","AaBbCcDd","the quick brown fox","aaaa","xyz"],
'A063': ["salom","Python","a","ab","abcde","12345","Hello World","racecar","xyz","ABCDEF"],
'A064': ["radar","A man a plan a canal Panama","hello","level",
         "Was it a car or a cat I saw","python","racecar","Never odd or even","hello world","Madam Im Adam"],
'A065': ["salom dunyo biz","men kitob o'qiyapman","a","one two three four",
         "hello world","the quick brown fox jumps","Python dasturlash tili juda qiziqarli","single","a b c d e","test"],
'A066': ["Hello World","Hello World from Python","ALL CAPS","no caps here",
         "Python3","ABCDE","aAbBcC","123ABC","Mixed Case String","hello"],
'A067': ["abc123def456","abc123def456gh7","no digits","1234567890",
         "Python3","test123test","a1b2c3d4","hello world","999","abc"],
'A068': ["salom\na\ne","salom dunyo\no\na","hello\nl\nr","aaa\na\nb",
         "abcabc\na\nz","test\nt\nT","python\np\nP","hello world\no\n0","xyx\nx\ny","aaaa\na\nX"],
'A069': ["aababc","abracadabra","aaabbbccc","zzz",
         "abcdef","aabb","mississippi","hello","aaaaabbb","bcaaa"],
'A070': ["salom dunyo","Python juda qiziqarli","one","a b c",
         "hello world foo bar","the quick brown fox","one two","Python is fun","test case here","a b"],
'A071': ["3\nsalom\ndunyo\nbiz","4\nPython\njuda\nqiziqarli\ntil",
         "1\nhello","2\nfoo\nbar","5\na\nb\nc\nd\ne","3\none\ntwo\nthree",
         "2\nhello\nworld","4\nI\nlove\nPython\nprogramming","3\ntest\ncase\ninput","2\nfirst\nsecond"],
'A072': ["salom dunyo biz","men dastur yozmoqdaman","one","a b c d",
         "hello world","one two three four five","Python is fun","reverse these words","the end","single"],
'A073': ["(())","((()))","(()","()","((((","))))","()()()","(()(()))","(()())",")" ],
'A074': ["aabbcc","aabbccddee","abc","aaaa","aabb","abcabc","hello","mississippi","aabbccdd","abcd"],
'A075': ["salom dunyo biz","bu satr ichidagi eng uzun soz bormi","one",
         "hello world","python programming language","a bb ccc dddd","short longer longest",
         "test testing tested","a bc def ghij","the quick brown fox"],
'A076': ["a b a c b a","olma nok olma banan nok olma","a a a","a b c",
         "hello hello world","one one two two three","a a b b c c d","x y z x y x",
         "python python java java c","test"],
'A077': ["banan olma gilos","banan olma gilos anor","c b a","a",
         "zebra apple mango","z y x w v","one two three four five","python java c ruby","dog cat bird ant","one two one"],
'A078': ["bu katta kichik sozlar","Python bu kuchli dasturlash tili","a","abc de f",
         "one two three","hello hi hey","python java c","aaa bb c dddd","cat dog bird ant","z ab abc abcd"],
'A079': ["hello world","salom dunyo","python","abc","Hello World",
         "lowercase","test string","programming","a b c","python is great"],
'A080': ["salom dunyo","men python o'rganmoqdaman","hello world","one two three",
         "python programming","the quick brown fox","a b c","learning to code","test case input","hello"],
'A081': ["7\n1 3 5 7 9 11 13\n7","8\n1 3 5 7 9 11 13 15\n9","5\n1 2 3 4 5\n1",
         "5\n1 2 3 4 5\n5","5\n1 2 3 4 5\n3","5\n1 3 5 7 9\n6",
         "1\n42\n42","1\n42\n43","6\n2 4 6 8 10 12\n8","6\n2 4 6 8 10 12\n5"],
'A082': ["4\n4 3 2 1","6\n5 3 8 1 9 2","3\n1 2 3","3\n3 2 1",
         "1\n5","4\n1 2 3 4","5\n5 4 3 2 1","4\n2 1 4 3","3\n3 1 2","5\n1 5 2 4 3"],
'A083': ["6","12","0","1","10","15","5","20","3","8"],
'A084': ["8","12","1","2","15","20","35","5","10","30"],
'A085': ["3","8","1","2","10","5","15","20","30","4"],
'A086': ["12","360","2","7","100","1000000000","30","1024","315","17"],
'A087': ["5\n1 3 5 7 9\n6","6\n1 3 5 7 9 11\n6","3\n1 5 10\n3","4\n1 2 3 4\n5",
         "3\n10 20 30\n15","5\n1 2 3 4 5\n1","3\n100 200 300\n250","4\n-5 0 5 10\n3","3\n1 3 5\n4","2\n1 10\n6"],
'A088': ["5\n5 3 8 1 9","7\n3 1 4 1 5 9 2","2\n1 2","3\n5 5 3",
         "4\n1 2 3 4","5\n10 10 10 5 5","4\n-1 -2 -3 -4","3\n100 50 50","5\n7 7 7 7 1","4\n0 -1 5 3"],
'A089': ["5\n5 3 8 1 9","7\n3 1 4 1 5 9 2","2\n1 2","3\n5 5 3",
         "4\n4 3 2 1","5\n10 10 5 5 1","4\n-4 -3 -2 -1","3\n0 0 1","5\n7 7 7 7 1","4\n0 -1 5 3"],
'A090': ["5\n1 2 3 4 5\n5","6\n1 2 3 4 5 6\n7","4\n1 2 3 4\n10","3\n1 1 1\n2",
         "5\n0 0 0 0 0\n0","4\n-1 0 1 2\n1","4\n1 2 3 4\n3","5\n5 5 5 5 5\n10","3\n1 2 3\n4","4\n2 4 6 8\n10"],
'A091': ["2 3\n1 2 3\n4 5 6","3 3\n1 2 3\n4 5 6\n7 8 9","1 1\n5","2 2\n1 2\n3 4",
         "3 2\n1 2\n3 4\n5 6","1 3\n1 2 3","2 4\n1 2 3 4\n5 6 7 8","3 1\n1\n2\n3",
         "2 2\n0 0\n0 0","3 3\n9 8 7\n6 5 4\n3 2 1"],
'A092': ["2\n1 2\n3 4\n5 6\n7 8","2\n1 0\n0 1\n5 6\n7 8","2\n1 1\n1 1\n1 1\n1 1","1\n5\n3",
         "2\n2 3\n1 4\n5 6\n7 8","3\n1 2 3\n4 5 6\n7 8 9\n9 8 7\n6 5 4\n3 2 1",
         "2\n0 0\n0 0\n1 2\n3 4","2\n1 2\n3 4\n1 0\n0 1",
         "3\n1 0 0\n0 1 0\n0 0 1\n1 2 3\n4 5 6\n7 8 9","2\n-1 2\n3 -4\n5 6\n7 8"],
'A093': ["2\n1 2\n3 4","3\n1 2 3\n4 5 6\n7 8 10","2\n5 3\n2 1","2\n1 0\n0 1",
         "3\n2 0 0\n0 3 0\n0 0 4","2\n0 0\n0 0","3\n1 2 3\n0 1 4\n5 6 0","2\n3 7\n1 -4",
         "3\n6 1 1\n4 -2 5\n2 8 7","2\n2 5\n1 3"],
'A094': ["AGGTAB\nGXTXAYB","ABCBDAB\nBDCABA","ABC\nABC","ABC\nDEF",
         "ABCDE\nACE","ABCDE\nBCDE","A\nA","A\nB","AAAA\nAA","XMJYAUZ\nMZJAWXU"],
'A095': ["14","2024","1","9","58","1994","3999","400","44","100"],
'A096': ["XIV","MCMXCIX","I","IX","IV","XLII","MMXXIV","CDXLIV","MMMCMXCIX","L"],
'A097': ["aaabbc","aaabbbbcccd","a","aaaaaa","abcdef","aabb","aaabbbccc","zzzzz","aab","abcccdd"],
'A098': ["a3b2c1","a3b4c3d1","a1","a6","a1b1c1d1e1f1","a2b2","a3b3c3","z5","a2b1","a1b2c3d2"],
'A099': ["listen\nsilent","Triangle\nIntegral","hello\nworld","dusty\nstudy",
         "abc\ncba","abc\nabd","aaa\naab","python\ntyphon","rat\ntar","cat\ncar"],
'A100': ["([{}])","([)]","(())","((())","()",
         "[]{}","{}[]","{[}]","((()))","[({})]{[]}"],
}

SOLUTIONS = {
    'A001':sol_A001,'A002':sol_A002,'A003':sol_A003,'A004':sol_A004,'A005':sol_A005,
    'A006':sol_A006,'A007':sol_A007,'A008':sol_A008,'A009':sol_A009,'A010':sol_A010,
    'A011':sol_A011,'A012':sol_A012,'A013':sol_A013,'A014':sol_A014,'A015':sol_A015,
    'A016':sol_A016,'A017':sol_A017,'A018':sol_A018,'A019':sol_A019,'A020':sol_A020,
    'A021':sol_A021,'A022':sol_A022,'A023':sol_A023,'A024':sol_A024,'A025':sol_A025,
    'A026':sol_A026,'A027':sol_A027,'A028':sol_A028,'A029':sol_A029,'A030':sol_A030,
    'A031':sol_A031,'A032':sol_A032,'A033':sol_A033,'A034':sol_A034,'A035':sol_A035,
    'A036':sol_A036,'A037':sol_A037,'A038':sol_A038,'A039':sol_A039,'A040':sol_A040,
    'A041':sol_A041,'A042':sol_A042,'A043':sol_A043,'A044':sol_A044,'A045':sol_A045,
    'A046':sol_A046,'A047':sol_A047,'A048':sol_A048,'A049':sol_A049,'A050':sol_A050,
    'A051':sol_A051,'A052':sol_A052,'A053':sol_A053,'A054':sol_A054,'A055':sol_A055,
    'A056':sol_A056,'A057':sol_A057,'A058':sol_A058,'A059':sol_A059,'A060':sol_A060,
    'A061':sol_A061,'A062':sol_A062,'A063':sol_A063,'A064':sol_A064,'A065':sol_A065,
    'A066':sol_A066,'A067':sol_A067,'A068':sol_A068,'A069':sol_A069,'A070':sol_A070,
    'A071':sol_A071,'A072':sol_A072,'A073':sol_A073,'A074':sol_A074,'A075':sol_A075,
    'A076':sol_A076,'A077':sol_A077,'A078':sol_A078,'A079':sol_A079,'A080':sol_A080,
    'A081':sol_A081,'A082':sol_A082,'A083':sol_A083,'A084':sol_A084,'A085':sol_A085,
    'A086':sol_A086,'A087':sol_A087,'A088':sol_A088,'A089':sol_A089,'A090':sol_A090,
    'A091':sol_A091,'A092':sol_A092,'A093':sol_A093,'A094':sol_A094,'A095':sol_A095,
    'A096':sol_A096,'A097':sol_A097,'A098':sol_A098,'A099':sol_A099,'A100':sol_A100,
}

# ─── Main ─────────────────────────────────────────────────────────────────────

app = create_app()
with app.app_context():
    problems = ArenaProblem.query.filter_by(is_active=True).order_by(ArenaProblem.code).all()
    ok = 0; skip = 0; err = 0

    for p in problems:
        code = p.code
        if code not in SOLUTIONS:
            print(f"  SKIP {code}: no solution defined")
            skip += 1
            continue

        sol_fn = SOLUTIONS[code]
        inp_list = TESTS[code]
        tests = []
        for inp in inp_list:
            try:
                out = sol_fn(inp)
                tests.append({'input': inp, 'output': str(out)})
            except Exception as e:
                print(f"  ERROR {code} inp={repr(inp)}: {e}")
                err += 1

        if len(tests) >= 10:
            p.hidden_tests = json.dumps(tests, ensure_ascii=False, indent=2)
            ok += 1
            print(f"  OK {code}: {len(tests)} tests saved")
        else:
            print(f"  WARN {code}: only {len(tests)} tests generated")
            err += 1

    db.session.commit()
    print(f"\nDone: {ok} updated, {skip} skipped, {err} errors")
