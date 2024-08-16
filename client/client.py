from copy import deepcopy
import socket
import ssl
from time import time_ns, sleep
from colorama import Fore as Print_color
from colorama import Style as Print_style
import _thread
import json


##############################################################
####This Connection Framework is written by Redstone_Teddy####
####  It can for example be used for a Multiplayer Game   ####
##############################################################


class Connection():
    """
    Class to handle a connection as the Client.\n
    Connection Framework by Redstone_Teddy
    """
    def __init__(self):
        self.socket_client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4 & TCP
        self.quene: list[dict] =  [] # This is the main quene, everything, that needs to be send to the server, will be in here
        self.connected: bool = False
        self.last_send_time: int = 0 # Stores the last time data was send in Milliseconds
        self.thread_error: str = "" # If the __Threaded_client has an error it will be stored in here, before it exits.
        self.ping: int = -1 # Time between clients request to the server until the response has come back and got processed in milliseconds.
        self.__ping_list: list[int] = [] # List for calculating average ping time
        self.min_ping: int = 50 # Minimum ping time, wait at least this many milliseconds before sending another packet to the server
        self.check_locations: list[dict] = []
        



    def Connect(self, data: dict, ip: str = "", port: int = 12345, password: str = "", version: str = "", username: str = "") -> None:
        """
        Connects to the server using the specified IP and port
        """
        # Check for Port & IP address
        if port > 65535:
            raise ConnectionError("The Port is above 65535 (the allowed maximum)!")
        elif port < 1:
            raise ConnectionError("The Port is smaller than 1 (the allowed minimum)!")
        if ip == "":
            raise ConnectionError("No IP address was specified!")

        _thread.start_new_thread(self.__Threaded_client, (data, ip, port, password, version, username))



    def __Threaded_client(self, data: dict, ip: str = "", port: int = 12345, password: str = "", version: str = "", username: str = "") -> None:
        self.socket_client.connect((ip, port))
        self.socket_client: socket.socket = ssl.wrap_socket(self.socket_client, ssl_version=ssl.PROTOCOL_TLSv1_2)

        # Password and Version Verification
        init_send_data: str = json.dumps({
            "password": password,
            "version": version,
            "username": username
        })
        self.socket_client.send(init_send_data.encode('utf-8'))
        init_response_data: str = self.socket_client.recv(1048576).decode('utf-8')
        init_response: dict = json.loads(init_response_data)

        
        if init_response.get("accepted") == True:
            self.player_id = init_response.get("player_id")
            data["player_id"] = self.player_id
        else:
            self.thread_error = init_response.get("reason")
            raise ConnectionError(init_response.get("reason"))
        


        self.connected = True

        # Main Loop
        try:
            while self.connected:
                # Wait atleast 50 milliseconds for the next packet to the server
                time_dif: int = int(self.last_send_time + self.min_ping - (time_ns() // 1000000))
                if time_dif > 0: 
                    sleep(time_dif / 1000)


                self.last_send_time = time_ns() // 1000000
                

                # Send quene to server, even if it's empty
                self.__Append_Check_to_quene(data)
                send_data: str = json.dumps(self.quene)
                self.quene = []
                self.socket_client.send(send_data.encode('utf-8'))
    
                # Get Servers response_quene
                response_data: str = self.socket_client.recv(1048576).decode('utf-8')
                response_quene: list[dict] = json.loads(response_data)


                # Handle requests
                for i in range(len(response_quene)):
                    match response_quene[i].get("type"):
                        case "SaveAll":
                            self.__Handle_SaveAll(response_quene[i],data)
                        case "Add":
                            self.__Handle_Add(response_quene[i],data)
                        case "Delete":
                            self.__Handle_Delete(response_quene[i],data)
                        case "Change":
                            self.__Handle_Change(response_quene[i],data)
                        case "CheckResponse":
                            self.__Handle_CheckResponse(response_quene[i])
                        case _:
                            raise ConnectionError("Server sent and invalid response (-type)")

                self.__ping_list.append((time_ns() // 1000000) - self.last_send_time)
                if len(self.__ping_list) > 50: del self.__ping_list[0]
                self.ping = round(sum(self.__ping_list)/len(self.__ping_list),1)
            self.socket_client.close()
        except Exception:
            self.connected = False
            self.quene = []
        


    def __Handle_CheckResponse(self, command: dict) -> None:
        location = command.get("location")
        for check_entry_index in range(len(self.check_locations)):
            if self.check_locations[check_entry_index].get("location") == location:
                if command.get("success") == True:
                    del self.check_locations[check_entry_index]
                else:
                    self.check_locations[check_entry_index]["fail_count"] += 1




    def __Handle_SaveAll(self, command: dict, data: dict | list[dict]) -> None:
        location: str = command.get("location")
        if location == "": # Save all data
            new_data: dict = command.get("data")
            for key in new_data:
                data[key] = deepcopy(new_data[key])
        else: # Only save data of the specified location
            new_data: list = command.get("data")
            data[location] = new_data
        # If there is an ongoing check for this location, delete it.
        for check_entry_index in range(len(self.check_locations)):
            if self.check_locations[check_entry_index].get("location") == location:
                del self.check_locations[check_entry_index]


    def __Handle_Add(self, command: dict, data: dict) -> None: 
        location: str = command.get('location')
        element: dict = command.get('element')
        data[location].append(element)


    def __Handle_Delete(self, command: dict, data: dict) -> None: 
        location: str = command.get("location")
        element_id: int = command.get("id")
        i = -1
        while True:
            i += 1
            if data[location][i].get("id") == element_id:
                break
        del data[location][i]

    def __Handle_Change(self, command: dict, data: dict) -> None: 
        location: str = command.get("location")
        element: dict = command.get("element")
        element_id: int = element.get("id")
        i = -1
        while True:
            i += 1
            if data[location][i].get("id") == element_id:
                break
        data[location][i] = element




    def Disconnect(self) -> None:
        """
        Disconnects from the server
        """
        self.connected = False


    def SendAll(self, location:str = "") -> None:
        """
        Sends a SendAll request to the server.
        The Server will Send all Data back to the client.
        If location is empty, the server will send everything
        If location is given, only send the data at the location 
        """
        if self.connected:
            self.quene.append({
                "type": 'SendAll',
                "location": location
            })
        else:
            raise ConnectionError("Client is not connected to a server!")
   
    def Add(self, location: str, element: dict) -> None:
        """
        Tells the server to add something to the data dictionary,
        The element needs a field "id" in it.
        """
        if self.connected:
            self.quene.append({
                "type": 'Add',
                "location": location,
                "element": deepcopy(element)
            })
        else:
            raise ConnectionError("Client is not connected to a server!")     
        
    def Delete(self, location: str, element_id: int) -> None:
        """
        Tells the server to delete something from the data dictionary
        """
        if self.connected:
            self.quene.append({
                "type": 'Delete',
                "location": location,
                "id": element_id
            })
        else:
            raise ConnectionError("Client is not connected to a server!")  
         
    def Change(self, location: str, element: dict) -> None:
        """
        Tells the server to change something to something new in the data dictionary.
        No ID is needed, the server will automatically check the new element for its ID.
        """
        if self.connected:
            self.quene.append({
                "type": 'Change',
                "location": location,
                "element": deepcopy(element)
            })
        else:
            raise ConnectionError("Client is not connected to a server!")  
        
    def CheckData(self, location: str) -> None:
        """
        Checks if the server and client have the same data at the given location.
        If not, the server will overwrite all client data in this location.
        If the wanted location is frequently accessed by this client, other clients connected to the server, or the server itself, the check will need some time to be completed successfully.
        """
        if self.connected:
            # Check if a check for this location is already scheduled
            found: bool = False
            for check in self.check_locations:
                if check.get("location") == location:
                    found: bool = True
            if found == False:
                self.check_locations.append({
                    "location": location,
                    "fail_count": 0
                })
        else:
            raise ConnectionError("Client is not connected to a server!")  
        

    def __Append_Check_to_quene(self, data:dict) -> None:
        for check in self.check_locations:
            found: bool = False
            for quene_entry in self.quene:
                if quene_entry.get("location") == check.get("location"):
                    found:bool = True
            if found == False:
                self.__Calculate_CheckSum(check , data)
            else:
                check["fail_count"] += 1


    def __Calculate_CheckSum(self, check: dict, data: dict) -> None:
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



        # package all checks into a single quene_entry
        self.quene.append({
            "type": "CheckData",
            "location": check.get("location"),
            "length": length,
            "all_ids": all_ids,
            "checksum": checksum,
            "checksum2": checksum2
        })


        
        
    
    




class ConnectionError(Exception):
    """
    Class for all errors during a connection\n
    using the Connection Framework v2 by Redstone_Teddy
    """
    def __init__(self, message: str="") -> None:
        print(Print_color.RED + message)
        print(Print_style.RESET_ALL)
        super().__init__(message)

