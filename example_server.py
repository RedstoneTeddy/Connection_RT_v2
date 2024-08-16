from os import path as os_path
from os import chdir as os_chdir
directory = os_path.dirname(os_path.abspath(__file__))
os_chdir(directory) #Small Bugfix, that in some situations, the code_path isn't correct






data = {
    "players": [],
    "boxes": []
}


server_certificate: str = "server/server.crt"
server_key: str = "server/server.key"
ip: str = "" # If empty, server automatically checks the IP address of the machine it's running on
port: int = 12345
password: str = "password"
version: str = "123"
max_players: int = 2


import server.server as server
server_obj = server.Connection(server_certificate, server_key, ip, port, password, version, max_players)
server_obj.Startup_server(data)
print(f"IP: {server_obj.ip} Port: {server_obj.port}")


import time
print("Starting up server...")
while True:
    time.sleep(0.5)
    if server_obj.run == True:
        break
print("Server startup finished.")



import easygui
while True:
    user_input = easygui.choicebox("Pick, what you want to do...","Example Server", ["exit", "check data","CMD - SaveAll","CMD - Add", "CMD - Delete", "CMD - Change"])
    match user_input:
        case "exit":
            server_obj.Shutdown_server()
            break


        case "check data":
            easygui.textbox("This is the data stored:","Example Server", str(data))


        case "CMD - SaveAll":
            cmd_input = easygui.multenterbox("Fill in the values\nSendAll","Example Server",["location (str)"])
            cmd = server_obj.SaveAll(cmd_input[0],data)
            cmd_input = easygui.choicebox("Select whom to send the command", "Example Server",["Send to one","Send to all","Send to all except one"])
            if cmd_input == "Send to one":
                id_input = easygui.integerbox("Give the ID of the player", "Example Server")
                server_obj.Send_to_one(cmd, id_input)
            elif cmd_input == "Send to all":
                server_obj.Send_to_all(cmd)
            elif cmd_input == "Send to all except one":
                id_input = easygui.integerbox("Give the ID of the player to exclude", "Example Server")
                server_obj.Send_to_all_except_one(cmd, id_input)

            
        case "CMD - Add":
            cmd_input = easygui.multenterbox("Fill in the values\nAdd","Example Server",["location (str)","element (dict)"])
            cmd = server_obj.Add(cmd_input[0], eval(cmd_input[1]))
            # Make the action on the local data
            data[cmd_input[0]].append(eval(cmd_input[1]))
            cmd_input = easygui.choicebox("Select whom to send the command", "Example Server",["Send to one","Send to all","Send to all except one"])
            if cmd_input == "Send to one":
                id_input = easygui.integerbox("Give the ID of the player", "Example Server")
                server_obj.Send_to_one(cmd, id_input)
            elif cmd_input == "Send to all":
                server_obj.Send_to_all(cmd)
            elif cmd_input == "Send to all except one":
                id_input = easygui.integerbox("Give the ID of the player to exclude", "Example Server")
                server_obj.Send_to_all_except_one(cmd, id_input)
            

        case "CMD - Delete":
            cmd_input = easygui.multenterbox("Fill in the values\nDelete","Example Server",["location (str)","id (int)"])
            cmd = server_obj.Delete(cmd_input[0], int(cmd_input[1]))
            # Make the action on the local data
            i = -1
            while True:
                i += 1
                if data[cmd_input[0]][i].get("id") == int(cmd_input[1]):
                    break
            del data[cmd_input[0]][i]
            cmd_input = easygui.choicebox("Select whom to send the command", "Example Server",["Send to one","Send to all","Send to all except one"])
            if cmd_input == "Send to one":
                id_input = easygui.integerbox("Give the ID of the player", "Example Server")
                server_obj.Send_to_one(cmd, id_input)
            elif cmd_input == "Send to all":
                server_obj.Send_to_all(cmd)
            elif cmd_input == "Send to all except one":
                id_input = easygui.integerbox("Give the ID of the player to exclude", "Example Server")
                server_obj.Send_to_all_except_one(cmd, id_input)
            

        case "CMD - Change":
            cmd_input = easygui.multenterbox("Fill in the values\nChange","Example Server",["location (str)","element (dict)"])
            cmd = server_obj.Change(cmd_input[0], eval(cmd_input[1]))
            # Make the action on the local data
            i = -1
            while True:
                i += 1
                if data[cmd_input[0]][i].get("id") == eval(cmd_input[1]).get("id"):
                    break
            data[cmd_input[0]][i] = eval(cmd_input[1])
            cmd_input = easygui.choicebox("Select whom to send the command", "Example Server",["Send to one","Send to all","Send to all except one"])
            if cmd_input == "Send to one":
                id_input = easygui.integerbox("Give the ID of the player", "Example Server")
                server_obj.Send_to_one(cmd, id_input)
            elif cmd_input == "Send to all":
                server_obj.Send_to_all(cmd)
            elif cmd_input == "Send to all except one":
                id_input = easygui.integerbox("Give the ID of the player to exclude", "Example Server")
                server_obj.Send_to_all_except_one(cmd, id_input)









