source /opt/conda/etc/profile.d/conda.sh

conda activate finbert

python3 main.py
python3 index.py &
ip="$(hostname -I)"
echo "Servers running at $ip on port 8050 and 8051"
# python3 app.py 

