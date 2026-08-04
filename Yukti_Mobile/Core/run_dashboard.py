from waitress import serve
from Mobile_Control import app

print("="*60)
print("Yukti Dashboard Started")
print("http://0.0.0.0:5050")
print("="*60)

serve(
    app,
    host="0.0.0.0",
    port=5050,
    threads=8
)