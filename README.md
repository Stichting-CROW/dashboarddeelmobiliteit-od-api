# README

od-api aggregates makes it possible to query OD data. 

This software can be run locally by running
```bash
python3 -m venv ENV
source ENV/bin/activate
pip install -r requirements.txt
./start.sh
```

# ssh tunnels
```bash
ssh -L 5433:10.133.75.95:5432 root@auth.deelfietsdashboard.nl
```

# Building:
```bash
docker build -t ghcr.io/stichting-crow/dashboarddeelmobiliteit-od-matrix-aggregator:x.y .
docker push ghcr.io/stichting-crow/dashboarddeelmobiliteit-od-matrix-aggregator:x.y
```