# Documentation for the Connection Framework v2 by Redstone_Teddy

The Connection Framework v2 is designed for handling the Server-Client-Connection for a Multiplayer Game. Technically it's also possible to use this Framework for Client-Server-Connections outside of games. 

## General Information
The framework is designed that each client and the server have a dictionary-type variable called "**data**". Everything in *data* the server has should always be synchronized to the client, otherwise there may occur some problems. This isn't true for the other direction. The client can have something in the *data*-variable that the server doesn't need to have (but then it also won't be synchronized to the other clients), for example the server doesn't need your screen resolution if you want to store it inside of *data*.

**Note! :** If you change something in the data-variable the Frameworks won't automatically synchronize it. So if you want to change something in the data-variable and synchronize it, you need to do these two steps separately:
```python
new_element = {"id": 101, "name": "HelloWorld"}
data["elements"].append(new_element)
client_obj.Add("elements", new_element)
```

## Data requirements
As mentioned before, you need the dictionary-type variable called "**data**", this also must contain some information to begin with. For the server it must atleast have these things in it:
```python
data = {
    "players": []
}
```
and for the Client:
```python
data = {
    "players": [],
    "player_id": -1
}
```
These two (or one for the server) will be set and edited by the Connection Framework automatically.

## Game Data Shape Requirements
How your actual game data is stored in the **data** variable needs to follow a pre-determined set of requirements. Everything must be stored in a dictionary in a list. This list can have multiple dictionaries in it. Additionally each element (dictionary) in the list must contain a **id** with an unique id (stored as an integer) the Connections Framework can address the element as. Example:
```python
data_example = {
    "players": [],
    "player_id": -1,
    "buildings:" : [
        {"id:"101, "name":"wall"},
        {"id":102, "name":"house"},
        {"id":103, "name":"shop"}
    ],
    "inventory": [
        {"id:" 201, "slot":1, "name":"wood", "amount":12},
        {"id:" 202, "slot":2, "name":"stone", "amount":105}
    ]
}
```
If you want to store a single variable instead of a list of items, there is a simple workaround, you just make a list with this single variable as the only entry. For example i want to store the in-game time:
```python
data_example = {
    "players": [],
    "player_id": -1,
    "time": [{"id":123, "time": 456}]
}
```

## Dependencies
These are the used libraries of the Connection Framework:
- socket
- ssl
- colorama
- _thread
- json
- copy
- time


## SSL Encryption
Because the Connection Framework uses encryption (TLS v 1.2) provided by the SSL library you need a **server certificate** and a **server key**!


## Functions of the Connection Framework
### Server Setup
To setup it's very simple. Just import the server-Connection Class, set every needed parameter and run the command *Startup_server()*. If the IP-parameter is empty, server automatically checks the IP address of the machine it's running on

```python
import server
data = {
    "players": []
}

server_certificate: str = "server.crt"
server_key: str = "server.key"
ip: str = "" 
port: int = 12345
password: str = "password"
version: str = "123"
max_players: int = 2

server_obj = server.Connection(server_certificate, server_key, ip, port, password, version, max_players)
server_obj.Startup_server(data)
```

If you set the IP-parameter as empty and the server started up and checked the IP itself, you can extract the found IP address with:
```python
print(server_obj.ip)
```

With the *run* variable of the server, you can check if the server is still up and running, or if it closed:

```python
print(server_obj.run)
```


### Client Setup
To setup the client is similarly easy as the server:

```python
import client
data = {
    "players": [],
    "player_id": -1
}

ip: str = "89.67.45.123"
port: int = 12345
password: str = "password"
version: str = "123"
username: str = "HelloWorld"


client_obj = client.Connection()
client_obj.Connect(data, ip, port, password, version, username)
```

To check if the client is currently connected to a server you can use:
```python
print(client_obj.connected)
```

After you started up the client, it's allways a good practice to tell the server, he should send all the data he has:
```python
client_obj.SendAll("")
```

### Client Functions

With the command *Disconnect* the client will disconnect from the server:
```python
client_obj.Disconnect()
```

To tell the server he should send all the server data to the Client use *SendAll*, this has an optional *location* parameter, if you specify a specific key of the data-dictionary, the server will only send this data and not all of it.
```python
client_obj.SendAll(location: str)
```

To add a element in your data-dictionary to a list (=location), this is the command. Note: Each element needs a unique key "id" in it! Example use:
```python
new_element = {
    "id": 123,
    "name": "house"
}
client_obj.Add(location: str = "buildings", element: dict = new_element)
```

To delete a element from a list (=location) you only need it's id and the locationn:
```python
client_obj.Delete(location: str, element_id: int)
```

To change an element to a new one, the element given into the command must have the same id as the element which should be replaced / changed:
```python
client_obj.Change(location: str, element: dict)
```

There is also a command to check, if your data is still up-to-date with the server's data. It's technically not needed to use this command, but for some unknown reason it can happen, that some of the data is not synchronized anymore. For that it is allways a good idea to send all 20 seconds or so a checkData for a specific area. So the command CheckData will check with the server if everything is correct without sending all the data and so creating a lag spike. It does this with multiple different checks. For the command to work, you only need the location. 
```python
client_obj.CheckData(location: str)
```
Note, that the check will not be run immediately, but it will be tried every time the client sends the server something. The check will fail, if the client, another client connected to the server, or the server itself changes some of the data, the check would be performed on. In this failure-case the client will just resend the Check in the next packet. That means in conclusion, that if a location is very frequently accessed / changed, until the check will complete, it can take some time.

### Server Functions
To shutdown the server use:
```python
server_obj.Shutdown_server()
```

A big difference between the client and server according the data-manipulation commands (Add, Delete, Change) is, that the client automatically sends it and the server's command will only return the command, which you afterwards have to give to a different command, which will actually send the command to the clients.

There are three different sending-commands, they are all self-explaining:
```python
server_obj.Send_to_one(command: dict, player_id: int)
server_obj.Send_to_all(command: dict)
server_obj.Send_to_all_except_one(command: dict, except_id: int)
```

To generate the command for sending, there are these four methods, all of them work similarly to the client one's.
```python
server_obj.SaveAll(location: str, data) -> dict
server_obj.Add(location: str, element: dict) -> dict
server_obj.Delete(location: str, element_id: int) -> dict
server_obj.Change(location: str, element: dict) -> dict
```


### ConnectionError
There is also a new exception-type: ConnectionError.
To raise one is the same as any other:
```python
raise ConnectionError("Server refused the Connection")
```

It will print out the message given in a red color in the terminal.