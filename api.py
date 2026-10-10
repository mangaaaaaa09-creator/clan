from flask import Flask, request, jsonify
import requests, warnings
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)
warnings.filterwarnings("ignore")

K = b"Yg&tc%DEuh6%Zc^8"
IV = b"6oyZDr22E3ychjM%"

def aesEnc(b):
    n = 16 - (len(b) % 16)
    d = b + bytes([n] * n)
    c = Cipher(algorithms.AES(K), modes.CBC(IV), backend=default_backend())
    e = c.encryptor()
    return e.update(d) + e.finalize()

def varint(n):
    r = b""
    while True:
        b = n & 0x7F
        n >>= 7
        if n: r += bytes([b | 0x80])
        else: r += bytes([b]); break
    return r

@app.route('/clan', methods=['GET'])
def join_clan():
    u = request.args.get('uid')
    p = request.args.get('pass')
    cid = request.args.get('id_clan')

    if not u or not p or not cid:
        return jsonify({"result": "Error", "message": "Missing parameters"})

    try:
        api_url = f"https://ff-jwt-gen-api.lovable.app/api/public/token?uid={u}&password={p}"
        r_api = requests.get(api_url, verify=False)
        at = r_api.json().get("token") or r_api.json().get("access_token")
        
        if not at:
            return jsonify({"result": "Error", "message": "Failed to get token"})

        headers = {
            "Authorization": f"Bearer {at}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB55",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; A063)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip"
        }

        body = aesEnc(varint((1 << 3) | 0) + varint(int(cid)))
        r = requests.post(
            "https://clientbp.ggpolarbear.com/RequestJoinClan",
            data=body,
            headers=headers,
            verify=False
        )

        if r.status_code == 200:
            return jsonify({"result": "Done"})
        else:
            return jsonify({"result": "Error", "status": r.status_code})

    except Exception as e:
        return jsonify({"result": "Error", "message": str(e)})

# ملاحظة: لا تستخدم app.run هنا لأن Vercel يديره تلقائياً عبر الـ Handler
