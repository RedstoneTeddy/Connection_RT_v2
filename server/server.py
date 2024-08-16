import socket
import ssl
from colorama import Fore as Print_color
from colorama import Style as Print_style
import _thread
import json
from copy import deepcopy



##############################################################
####This Connection Framework is written by Redstone_Teddy####
####  It can for example be used for a Multiplayer Game   ####
################################### ###########################



class Connection():
    """
    Class to handle a connection as the server.\n
    Connection Framework by Redstone_Teddy
    """

    def __init__(self, server_cert: str = "", server_key: str = "", ip: str = "", port: int = 12345, password: str = "", version: str = "", max_players: int = 2) -> None:
        self.socket_server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4 & TCP
        self.client_quenes: list[list[dict]] = []
        self.max_players: int = max_players
        self.run: bool = False
        
        # Set IP
        if ip == "": # If the user didn't specify an IP address, the Server should bind to, it will automatically try to detect the current IP of the machine it's running on
            self.ip: str = self.Get_ip()
        else:
            self.ip: str = ip

        # Set Port
        if port > 65535:
            raise ConnectionError("The Port is above 65535 (the allowed maximum)!")
        elif port < 1:
            raise ConnectionError("The Port is smaller than 1 (the allowed minimum)!")
        else:
            self.port: int = port

        if server_cert == "":
            raise ConnectionError("No Server certificate was specified!")
        if server_key == "":
            raise ConnectionError("No Server key was specified!")
        
        try:
            self.socket_server.bind((self.ip, self.port))
        except OSError:
            raise ConnectionError("An Error occured while binding the Server to the IP and Port!")
        
        try:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(certfile=server_cert, keyfile=server_key)
        except Exception:
            raise ConnectionError("SSL Context couldn't be made!")
        
        if password == "":
            print(Print_color.YELLOW + "You haven't set up a password, this is a security issue!")
            print(Print_style.RESET_ALL)
        self.password: str = password

        if version == "":
            print(Print_color.YELLOW + "You haven't specified the software version, server won't check for it! This can lead to problems!")
            print(Print_style.RESET_ALL)
        self.version: str = version

            

        


    def Get_ip(self) -> str:
        """
        Get the IP address of the current machine running the code
        """
        socket_ip_get: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            socket_ip_get.connect(('10.255.255.255', 1))
            IP: str = socket_ip_get.getsockname()[0]
        except Exception:
            IP: str = '127.0.0.1'
        finally:
            socket_ip_get.close()
        return IP
    


    def Startup_server(self,data: dict) -> None:
        """
        This function will startup the server, afterwards Clients can connect to the server.
        """
        _thread.start_new_thread(self.__Wait_for_client, (data,))


    def Shutdown_server(self) -> None:
        print("Server is shutting down...")
        self.run = False

        

    def __Wait_for_client(self, data: dict):
        # Wait for new clients to connect
        self.socket_server.listen()
        self.run = True
        while True:
            # Get Client information
            new_client: tuple[socket.socket, str] = self.socket_server.accept()
            client_socket: socket.socket = new_client[0]
            client_address: str = new_client[1]
            client_socket: socket.socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
            # Start new thread for Client   
            _thread.start_new_thread(self.__Threaded_client, (data, client_socket, client_address))   



    def __Threaded_client(self, data: dict, client_socket: socket.socket, client_address: str):
        print(f"Establishing a connection from {client_address}")

        # Get Clients init_request
        init_request_data: str = client_socket.recv(1048576).decode('utf-8')
        init_request: dict = json.loads(init_request_data)

        # Check if everything with the init_request is correct
        accept_client: str = "new"
        if self.version != "":
            if init_request.get("version") != self.version:
                accept_client = "wrong version"
        if self.password != "":
            if init_request.get("password") != self.password:
                accept_client = "wrong password"
        if len(data["players"]) >= self.max_players:
            accept_client = "server full"
        for player in data["players"]:
            if init_request.get("username") == player.get("username"):
                if player.get("online") == True:
                    accept_client = "user already exists"
                else:
                    accept_client = "rejoin"
        
        # Respond to the init_request
        init_response: dict
        match accept_client:
            case "wrong version": # Client has another version than the server
                init_response: dict = {"accepted": False, "reason": "wrong version"}
                init_response_data: str = json.dumps(init_response)
                client_socket.send(init_response_data.encode('utf-8'))
                client_socket.close()
                print(f"User: {client_address} has the wrong version inst0alled")
                _thread.exit()
            case "wrong password": # Client has given a wrong password
                init_response: dict = {"accepted": False, "reason": "wrong password"}
                init_response_data: str = json.dumps(init_response)
                client_socket.send(init_response_data.encode('utf-8'))
                client_socket.close()
                print(f"User: {client_address} wrote an incorrect password")
                _thread.exit()
            case "user already exists": # If a user with this name already exists and is logged in
                init_response: dict = {"accepted": False, "reason": "user already exists"}
                init_response_data: str = json.dumps(init_response)
                client_socket.send(init_response_data.encode('utf-8'))
                client_socket.close()
                print(f"User: {client_address} logged in with a username, that already exists: {init_request.get('username')}")
                _thread.exit()
            case "server full": # Server is full
                init_response: dict = {"accepted": False, "reason": "server full"}
                init_response_data: str = json.dumps(init_response)
                client_socket.send(init_response_data.encode('utf-8'))
                client_socket.close()
                print(f"User: {client_address} couldn't join, server is full")
                _thread.exit()
            case "rejoin": # If a user with this name already exists, but is not logged in, rejoin as him
                for player in data["players"]:
                    if init_request.get("username") == player.get("username"):
                        if player.get("online") == False:
                            player_id: int = player.get("id")
            case "new": # If a new user wants to join
                player_id: int = 0
                for player in data["players"]:
                    if player.get("id") >= player_id:
                        player_id: int = player.get("id")+1
                self.client_quenes.append([])
            case _:
                raise ConnectionError("Client sent an invalid init_request")
        
        # If user can join, send him the User ID
        init_response: dict = {"accepted": True, "player_id": player_id}
        init_response_data: str = json.dumps(init_response)
        client_socket.send(init_response_data.encode('utf-8'))
        
        if accept_client == "rejoin":
            print(f"User: {client_address} rejoined as {init_request.get('username')} (id: {player_id})")
        elif accept_client == "new":
            print(f"User: {client_address} joined as {init_request.get('username')} (id: {player_id})")

        # Send to all user that a player joined
        if accept_client == "rejoin":
            player_index: int = self.__Get_index_of_id(data, "players", player_id)
            data["players"][player_index]["online"] = True
            self.Send_to_all_except_one(self.Change("players", data["players"][player_index]), player_id)
            self.client_quenes[player_id] = [] # Empty this clients quene
        elif accept_client == "new":
            data["players"].append({
                "id": player_id,
                "username": init_request.get('username'),
                "online": True
            })
            self.Send_to_all_except_one(self.Add("players", data.get("players")[len(data["players"])-1]),player_id)

        

        # Main Loop
        try:
            while self.run:
                # Get Clients request_quene
                request_data: str = client_socket.recv(1048576).decode('utf-8')
                request_quene: list[dict] = json.loads(request_data)

                # Handle requests
                for i in range(len(request_quene)):
                    match request_quene[i].get("type"):
                        case "SendAll":
                            self.__Handle_SendAll(request_quene[i],data,player_id)
                        case "Add":
                            self.__Handle_Add(request_quene[i],data,player_id)
                        case "Delete":
                            self.__Handle_Delete(request_quene[i],data,player_id)
                        case "Change":
                            self.__Handle_Change(request_quene[i],data,player_id)
                        case "CheckData":
                            self.__Handle_CheckData(request_quene[i],data,player_id)
                        case _:
                            raise ConnectionError(f"Client (id: {player_id}) sent and invalid request (-type)")

                # Send the client it's quene
                response_data: str = json.dumps(self.client_quenes[player_id])
                self.client_quenes[player_id] = []
                client_socket.send(response_data.encode('utf-8'))

                
            client_socket.close()
        except Exception:
            player_index: int = self.__Get_index_of_id(data, "players", player_id)
            data["players"][player_index]["online"] = False
            self.Send_to_all_except_one(self.Change("players", data["players"][player_index]), player_id)
            self.client_quenes[player_id] = [] # Empty this clients quene
            print(f"Client (id: {player_id}) disconnected")



            

            








    def __Handle_CheckData(self, command: dict, data: dict, player_id: int) -> None: 
        location: str = command.get('location')
        length: int = command.get('length')
        all_ids: str = command.get('all_ids')
        checksum: int = command.get('checksum')
        checksum2: int = command.get('checksum2')
        
        found: bool = False
        for quene_entry in self.client_quenes[player_id]:
            if quene_entry.get("location") == location:
                found = True
        if found == False:
            server_check: dict = self.__Calculate_CheckSum(command, data)



            if server_check.get("length") == length and server_check.get("all_ids") == all_ids:
                if server_check.get("checksum") == checksum and server_check.get("checksum2") == checksum2:
                    self.Send_to_one(self.__CheckResponse(location, True), player_id)
                else:
                    self.Send_to_one(self.SaveAll(location, data), player_id)
            else:
                self.Send_to_one(self.SaveAll(location, data), player_id)
        else:
            self.Send_to_one(self.__CheckResponse(location, False),player_id)



    def __CheckResponse(self, location: str, success: bool) -> dict:
        return {
            "type": "CheckResponse",
            "location": location,
            "success": success
        }


    def __Calculate_CheckSum(self, check: dict, data: dict) -> dict:
        length: int
        all_ids: str
        checksum: int
        checksum2: int

        length: int = len(data[check.get("location")])

        all_ids: str = ""
        for element in data[check.get("location")]:
            all_ids += str(element.get("id"))

        # This algorithm to calculate a checksum isn't THE BEST way of doing it, but it works MANY times
        checksum: int = 0
        checksum2: int = 0
        data_as_string: str = str(data[check.get("location")]).lower()
        for character in data_as_string:
            match character:
                case "0": checksum += 7;       checksum2 += 5
                case "1": checksum += 500;     checksum2 += 70000
                case "2": checksum += 10000;   checksum2 += 1
                case "3": checksum += 500000;  checksum2 += 100000
                case "4": checksum += 3;       checksum2 += 1000000
                case "5": checksum += 300;     checksum2 += 30
                case "6": checksum += 9000;    checksum2 += 50
                case "7": checksum += 90000;   checksum2 += 70
                case "8": checksum += 30;      checksum2 += 300000
                case "9": checksum += 700000;  checksum2 += 3
                case "a": checksum += 100;     checksum2 += 90
                case "b": checksum += 3000;    checksum2 += 100
                case "c": checksum += 300000;  checksum2 += 500000
                case "d": checksum += 9;       checksum2 += 300
                case "e": checksum += 10000000;checksum2 += 700000
                case "f": checksum += 90;      checksum2 += 7
                case "g": checksum += 7000;    checksum2 += 500
                case "h": checksum += 100000;  checksum2 += 3000000
                case "i": checksum += 900;     checksum2 += 700
                case "j": checksum += 30000;   checksum2 += 900
                case "k": checksum += 3000000; checksum2 += 5000000 
                case "l": checksum += 1;       checksum2 += 1000
                case "m": checksum += 1000000; checksum2 += 3000
                case "n": checksum += 5000;    checksum2 += 5000
                case "o": checksum += 900000;  checksum2 += 10
                case "p": checksum += 10;      checksum2 += 7000
                case "q": checksum += 7000000; checksum2 += 9000
                case "r": checksum += 50;      checksum2 += 10000
                case "s": checksum += 50000;   checksum2 += 900000
                case "t": checksum += 700;     checksum2 += 9000000
                case "u": checksum += 5000000; checksum2 += 9
                case "v": checksum += 1000;    checksum2 += 5000000
                case "w": checksum += 9000000; checksum2 += 7000000
                case "x": checksum += 5;       checksum2 += 30000
                case "y": checksum += 70000;   checksum2 += 50000
                case "z": checksum += 70;      checksum2 += 10000000

        return {
            "length": length,
            "all_ids": all_ids,
            "checksum": checksum,
            "checksum2": checksum2
        }



    def __Handle_SendAll(self, command: dict, data: dict, player_id: int) -> None: 
        location: str = command.get('location')
        if location == "": # Send everything
            self.Send_to_one(self.SaveAll("",deepcopy(data)), player_id)
        else: # Only send part of the data
            self.Send_to_one(self.SaveAll(location,deepcopy(data[location])), player_id)


    def __Handle_Add(self, command: dict, data: dict, player_id: int) -> None:
        location: str = command.get('location')
        element: dict = command.get('element')
        self.Send_to_all_except_one(deepcopy(command), player_id)
        data[location].append(element)


    def __Handle_Delete(self, command: dict, data: dict, player_id: int) -> None:
        location: str = command.get("location")
        element_id: int = command.get("id")
        self.Send_to_all_except_one(deepcopy(command), player_id)
        i = -1
        while True:
            i += 1
            if data[location][i].get("id") == element_id:
                break
        del data[location][i]


    def __Handle_Change(self, command: dict, data: dict, player_id: int) -> None: 
        location: str = command.get("location")
        element: dict = command.get("element")
        element_id: int = element.get("id")
        self.Send_to_all_except_one(deepcopy(command), player_id)
        i = -1
        while True:
            i += 1
            if data[location][i].get("id") == element_id:
                break
        data[location][i] = element






    def __Get_index_of_id(self, data: dict, location: str, element_id: int) -> int:
        output = -1
        for i in range(0,len(data[location])):
            if data[location][i].get("id") == element_id:
                output = i
        return output

    
    def Send_to_all_except_one(self, command: dict, except_id: int):
        """
        Send a command to all clients except one.
        """
        for i in range(0, len(self.client_quenes)):
            if i != except_id:
                self.client_quenes[i].append(deepcopy(command))
    

    def Send_to_all(self, command: dict):
        """
        Send a command to all clients.
        """
        for i in range(0, len(self.client_quenes)):
            self.client_quenes[i].append(deepcopy(command))


    def Send_to_one(self, command: dict, player_id: int):
        """
        Send a command to one client
        """
        self.client_quenes[player_id].append(deepcopy(command))


    def SaveAll(self, location: str = "", data: list[dict] | dict = []) -> dict: 
        """
        Generates the command to Save all data and wipe the old data to a client
        If location is empty, the server will send everything
        If location is given, only send the data at the location 
        """
        if location == "":
            return {
                "type": "SaveAll",
                "location": location,
                "data": deepcopy(data)
            }
        else:
            return {
                "type": "SaveAll",
                "location": location,
                "data": deepcopy(data[location])
            }


    def Add(self, location: str, element: dict) -> dict: 
        """
        Generates the command to add an element at the given location.
        The element needs a field "id" in it.
        """
        return {
            "type": "Add",
            "location": location,
            "element": deepcopy(element)
        }


    def Delete(self, location: str, element_id: int) -> dict:  
        """
        Generates the command to delete an element at the given location.
        """
        return {
            "type": 'Delete',
            "location": location,
            "id": element_id
        }


    def Change(self, location: str, element: dict) -> dict:  
        """
        Generates the command to change something to something new in the data dictionary.
        No ID is needed, the server will automatically check the new element for its ID.
        """
        return {
            "type": 'Change',
            "location": location,
            "element": deepcopy(element)
        }


    



            












class ConnectionError(Exception):
    """
    Class for all errors during a connection\n
    using the Connection Framework v2 by Redstone_Teddy
    """
    def __init__(self, message: str="") -> None:
        print(Print_color.RED + message)
        print(Print_style.RESET_ALL)
        super().__init__(message)

