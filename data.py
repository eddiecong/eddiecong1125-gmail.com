import http.client

conn = http.client.HTTPSConnection("covid-19-coronavirus-statistics.p.rapidapi.com")

headers = {
    'x-rapidapi-host': "covid-19-coronavirus-statistics.p.rapidapi.com",
    'x-rapidapi-key': "5f728b6756msh8dddad515ae5b37p14463cjsnad2a940fff4b"
    }

conn.request("GET", "/v1/stats?country=China", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))