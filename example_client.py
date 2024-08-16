from os import path as os_path
from os import chdir as os_chdir
directory = os_path.dirname(os_path.abspath(__file__))
os_chdir(directory) #Small Bugfix, that in some situations, the code_path isn't correct




data = {
    "players": [],
    "boxes": [],
    "player_id": -1
}

ip: str = "10.10.10.110"
port: int = 12345
password: str = "password"
version: str = "123"
username: str = "test2"



import client.client as client
client_obj = client.Connection()
client_obj.Connect(data, ip, port, password, version, username)


import time
print("Connecting to server...")
while True:
    time.sleep(0.5)
    if client_obj.connected == True:
        break
print("Connected to the server.")


client_obj.SendAll("")

import easygui
while True:
    user_input = easygui.choicebox("Pick, what you want to do...","Example Client", ["exit","check data","edit local data","check statistics","CMD - SendAll","CMD - Add", "CMD - Delete", "CMD - Change", "CMD - CheckData"])
    match user_input:
        case "exit":
            client_obj.Disconnect()
            break


        case "check data":
            easygui.textbox("This is the stored data:","Example Client", str(data))


        case "edit local data":
            cmd_input = easygui.textbox("This is the stored data.\nChange it in here","Example Client", str(data))
            from copy import deepcopy
            new_data = eval(cmd_input)
            for key in new_data:
                data[key] = deepcopy(new_data[key])


        case "check statistics":
            print(f"""
---- Client Statistics ----
Client is connected:   {client_obj.connected}
Last ping to server:   {time.strftime('%H:%M:%S', time.localtime(client_obj.last_send_time//1000))}
Average ping time:     {client_obj.ping}ms
Pending Checks:        {client_obj.check_locations}
                  """)
            

        case "CMD - SendAll":
            cmd_input = easygui.multenterbox("Fill in the values\nSendAll","Example Client",["location (str)"])
            # Send to Server
            client_obj.SendAll(cmd_input[0])
            

        case "CMD - Add":
            cmd_input = easygui.multenterbox("Fill in the values\nAdd","Example Client",["location (str)","element (dict)"])
            # Send to Server
            client_obj.Add(cmd_input[0], eval(cmd_input[1]))
            # Make the action on the local data
            data[cmd_input[0]].append(eval(cmd_input[1]))


        case "CMD - Delete":
            cmd_input = easygui.multenterbox("Fill in the values\nDelete","Example Client",["location (str)","id (int)"])
            # Send to Server
            client_obj.Delete(cmd_input[0], int(cmd_input[1]))
            # Make the action on the local data
            i = -1
            while True:
                i += 1
                if data[cmd_input[0]][i].get("id") == int(cmd_input[1]):
                    break
            del data[cmd_input[0]][i]
            

        case "CMD - Change":
            cmd_input = easygui.multenterbox("Fill in the values\nChange","Example Client",["location (str)","element (dict)"])
            # Send to Server
            client_obj.Change(cmd_input[0], eval(cmd_input[1]))
            # Make the action on the local data
            i = -1
            while True:
                i += 1
                if data[cmd_input[0]][i].get("id") == eval(cmd_input[1]).get("id"):
                    break
            data[cmd_input[0]][i] = eval(cmd_input[1])


        case "CMD - CheckData":
            cmd_input = easygui.enterbox("In which location should the check be made?","Example Client")
            client_obj.CheckData(cmd_input)
            