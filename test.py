import httpx

response = httpx.post('https://6z456hpazwuzluajqn5kka7htu0ltqnf.lambda-url.eu-west-2.on.aws/location',
           json={"command":"temp", "lat":6.0, "lon":6.0, "name":"test", "team":"test", "browser_info":"test"})
print(response.status_code)
print(response.text)

response = httpx.get('https://6z456hpazwuzluajqn5kka7htu0ltqnf.lambda-url.eu-west-2.on.aws/location')
print(response.status_code)
print(response.text)