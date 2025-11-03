### Deployment sur render

1-chosiir un web service

2-technologie python

3-choisir comme `start command`

```bash
gunicorn -c gunicorn.conf.py app:app
````
laisser le reste identique