### 1-construire l'image docker
```
docker build -t fare-calculator-api 
```
### une fois que l'image est cosntruite,lancer

```bash
docker run -d -p 5000:8000 --name fare-calculator-container fare-calculator-api
```